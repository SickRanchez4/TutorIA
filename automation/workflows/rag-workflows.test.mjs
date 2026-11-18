import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { runInNewContext } from 'node:vm'

const readWorkflow = (name) => JSON.parse(readFileSync(new URL(name, import.meta.url), 'utf8'))
const upload = readWorkflow('upload-to-pinecone.json')
const enrichCode = upload.nodes.find(node => node.name === 'Enriquecer Metadatos y Aislamiento').parameters.jsCode
const admin = readWorkflow('knowledge-index-admin.json')
const validateCode = admin.nodes.find(node => node.name === 'Validar acción del agente').parameters.jsCode
const confirmCode = admin.nodes.find(node => node.name === 'Confirmar operación').parameters.jsCode
const enrich = (originals, extracted) => runInNewContext(`(function () { ${enrichCode} })()`, {
  $: () => ({ all: () => originals }),
  $input: { all: () => extracted },
})
const validate = (body) => JSON.parse(JSON.stringify(runInNewContext(`(function () { ${validateCode} })()`, { $json: { body } })))

test('recovers original binaries after extraction strips them, preserving per-file identity', () => {
  const originals = ['fisica.pdf', 'algebra.pdf'].map((fileName, index) => ({
    json: { fileName, institucion_id: 'institution-test', curso_id: '405' },
    binary: { data: { id: `filesystem-v2:pdf-${index}` } },
  }))
  const results = enrich(originals, [{ json: { text: 'Newton' } }, { json: { text: 'Matrices' } }])
  for (let index = 0; index < results.length; index++) {
    assert.equal(results[index].binary, originals[index].binary)
    assert.equal(results[index].json.metadata.archivo, originals[index].json.fileName)
    assert.equal(results[index].pairedItem.item, index)
    assert.equal(results[index].json.metadata.namespace, 'inst_institution-test_curso_405')
  }
})

test('rejects missing original PDF and scanned PDFs without extractable text', () => {
  const original = { json: { fileName: 'fisica.pdf' } }
  assert.throws(() => enrich([original], [{ json: { text: 'Newton' } }]), /PDF original/)
  assert.throws(() => enrich([original], [{ json: { text: '' } }]), /OCR/)
})

test('builds descriptive profiles from extracted text without pretending to summarize the whole book', () => {
  const original = {
    json: { fileName: 'darwin.pdf', institucion_id: 'tenant', curso_id: '405' },
    binary: { data: { id: 'pdf-test' } },
  }
  const text = 'Introducción\nVariación en los seres vivos.\nCapítulo I\nSelección natural\nCapítulo I\n'
  const [result] = enrich([original], [{ json: {
    text, numpages: 478, info: { Title: 'El origen de las especies', Author: 'Charles Darwin' },
  } }])
  assert.equal(result.json.documentProfile.titulo, 'El origen de las especies')
  assert.equal(result.json.documentProfile.paginas, 478)
  assert.equal(result.json.documentProfile.extracto_inicial, text.trim())
  assert.deepEqual(Array.from(result.json.documentProfile.secciones), ['Introducción', 'Capítulo I'])
})

const rag = readWorkflow('tool-rag-chat.json')
const main = readWorkflow('students-agent-chatbot.json')
const code = (workflow, name) => workflow.nodes.find(node => node.name === name).parameters.jsCode
const run = (source, environment) => JSON.parse(JSON.stringify(runInNewContext(`(function () { ${source} })()`, environment)))

test('normalization preserves image input and passes document/history context through the existing webhook contract', () => {
  const image = { data_url: 'data:image/png;base64,c3ludGhldGlj', name: 'ejercicio.png', mime_type: 'image/png' }
  const payload = {
    institucion_id: 'tenant', curso_id: 405, conversation_id: 'conversation-test',
    image, chatbot_temperature: 0, max_tokens: 500,
    course_materials: [{ archivo: 'fisica.pdf' }],
    recent_history: [{ role: 'user', content: 'Explica la fuerza' }],
  }
  for (const json of [payload, { body: payload }]) {
    const result = run(code(main, 'Obtener input'), { $input: { first: () => ({ json }) } })[0].json
    assert.equal(result.inputType, 'image')
    assert.equal(result.pineconeNamespace, 'inst_tenant_curso_405')
    assert.equal(result.chatbotTemperature, 0)
    assert.equal(result.maxTokens, 500)
    assert.deepEqual(result.image, image)
    assert.deepEqual(result.courseMaterials, payload.course_materials)
    assert.deepEqual(result.recentHistory, payload.recent_history)
  }
})

test('external knowledge requires an explicit boolean permission in both entry points', () => {
  const mermaid = readWorkflow('tool-generador-mermaid.json')
  for (const [value, expected] of [[undefined, false], [false, false], ['false', false], [true, true], ['true', true]]) {
    const mainInput = { extend_knowledge: value }
    const normalized = run(code(main, 'Obtener input'), { $input: { first: () => ({ json: mainInput }) } })[0].json
    assert.equal(normalized.extendKnowledge, expected)
    const resourceInput = { query: 'Un diagrama', namespace: 'inst_tenant_curso_405', allowGeneralKnowledge: value }
    const resource = run(code(mermaid, 'Preparar Entrada'), { $input: { first: () => ({ json: resourceInput }) } })[0].json
    assert.equal(resource.allowGeneralKnowledge, expected)
  }
  for (const value of ['yes', 1, {}, []]) {
    assert.throws(() => run(code(main, 'Obtener input'), {
      $input: { first: () => ({ json: { extend_knowledge: value } }) },
    }), /booleano/)
  }
})

test('retrieval reads flattened and nested PDF pages, deduplicates and preserves complete passages within its context budget', () => {
  const chunk = (text, metadata) => ({ json: { document: { pageContent: text, metadata } } })
  const items = [
    chunk('Selección natural', { archivo: 'darwin.pdf', 'loc.pageNumber': '26' }),
    chunk('Selección   natural', { archivo: 'darwin.pdf', 'loc.pageNumber': 26 }),
    chunk('Variación', { archivo: 'darwin.pdf', loc: { pageNumber: 14 } }),
    chunk('Texto sin página', { archivo: 'otro.pdf', page: 'unknown' }),
    ...Array.from({ length: 20 }, (_, i) => chunk(`${i} ${'a'.repeat(3200)}`, { archivo: 'darwin.pdf', page: i + 30 })),
  ]
  const [{ json: result }] = run(code(rag, 'Formatear Contexto'), { $input: { all: () => items } })
  assert.deepEqual(result.citations.slice(0, 3), [
    { archivo: 'darwin.pdf', pagina: 26 },
    { archivo: 'darwin.pdf', pagina: 14 },
    { archivo: 'otro.pdf', pagina: null },
  ])
  assert.equal(result.context.match(/Selección/g).length, 1)
  assert.ok(result.context.length <= 28000)
  assert.ok(result.context.includes('del PDF'))
  assert.equal(result.hasContext, true)
  const empty = run(code(rag, 'Formatear Contexto'), { $input: { all: () => [{ json: {} }] } })[0].json
  assert.equal(empty.hasContext, false)
  assert.deepEqual(empty.citations, [])
  assert.match(empty.context, /No se encontró material relevante/)
})

test('semantic grounding retains only verified source passages and fails closed on invalid decisions', () => {
  const retrieved = {
    hasContext: true,
    passages: [
      { id: 1, archivo: 'darwin.pdf', pagina: 10, text: 'Una mención incidental de Francia.' },
      { id: 2, archivo: 'darwin.pdf', pagina: 26, text: 'Las variaciones heredables favorecen distinta descendencia.' },
    ],
  }
  const apply = decision => run(code(rag, 'Aplicar Respaldo'), {
    $: () => ({ first: () => ({ json: retrieved }) }),
    $json: { output: typeof decision === 'string' ? decision : JSON.stringify(decision) },
  })[0].json
  const accepted = apply({ supported: true, sourceIds: [2] })
  assert.equal(accepted.hasContext, true)
  assert.ok(accepted.context.includes(retrieved.passages[1].text))
  assert.ok(!accepted.context.includes('Francia'))
  assert.deepEqual(accepted.citations, [{ archivo: 'darwin.pdf', pagina: 26 }])
  const declined = apply({ supported: false, sourceIds: [] })
  assert.equal(declined.hasContext, false)
  assert.deepEqual(declined.citations, [])
  assert.ok(!declined.context.includes('Francia'))
  for (const decision of [
    { supported: true, sourceIds: [] }, { supported: true, sourceIds: [99] },
    { supported: true, sourceIds: ['2'] }, { supported: false, sourceIds: [2] },
    { supported: 'true', sourceIds: [2] }, 'invalid JSON',
  ]) assert.throws(() => apply(decision))
  const empty = run(code(rag, 'Aplicar Respaldo'), {
    $: () => ({ first: () => ({ json: { hasContext: false, passages: [] } }) }),
    $json: {},
  })[0].json
  assert.equal(empty.hasContext, false)
})

test('closed courses bypass the teaching model without evidence while open courses keep general answers', () => {
  const guard = main.nodes.find(node => node.name === '¿Respuesta respaldada o extensión habilitada?')
  const expression = guard.parameters.conditions.conditions[0].leftValue
  for (const [hasContext, extendKnowledge, allowed] of [[false, false, false], [true, false, true], [false, true, true]]) {
    assert.equal(runInNewContext(expression.slice(3, -2), {
      $json: { hasContext },
      $: () => ({ first: () => ({ json: { extendKnowledge } }) }),
    }), allowed)
  }
  const rejectedNode = main.connections[guard.name].main[1][0].node
  const declined = run(code(main, rejectedNode), {})[0].json
  assert.ok(declined.output.length > 0)
  assert.equal(declined.hasContext, false)
  assert.deepEqual(declined.citations, [])
})

test('overview and follow-up queries use only the current course catalog and history, rejecting mismatched namespaces', () => {
  const base = {
    institutionId: 'tenant', courseId: 405, pineconeNamespace: 'inst_tenant_curso_405',
    courseMaterials: [{ archivo: 'darwin.pdf', titulo: 'El origen de las especies' }],
    recentHistory: [{ role: 'user', content: 'Explica la selección natural' }],
  }
  const prepare = input => run(code(main, 'Preparar Contexto'), { $input: { first: () => ({ json: input }) } })[0].json
  const overview = prepare({ ...base, message: '¿Cuál es tu tema principal?' })
  assert.match(overview.retrievalQuery, /El origen de las especies/)
  const followup = prepare({ ...base, message: 'Dame un ejemplo de eso' })
  assert.match(followup.retrievalQuery, /selección natural/)
  for (const message of ['B', 'A, porque sobreviven más', 'No sé', 'Necesito una pista']) {
    assert.match(prepare({ ...base, message }).retrievalQuery, /selección natural/)
  }
  assert.throws(() => prepare({ ...base, pineconeNamespace: 'inst_other_curso_405' }), /namespace/)
})

test('resource requests retain the current image and recent referent without altering the selected mode or course', () => {
  const cfg = {
    requestedMode: 'recursos', courseId: 405, pineconeNamespace: 'inst_tenant_curso_405',
    message: 'Representa ese proceso con un diagrama',
    recentHistory: [{ role: 'user', content: 'Explica la selección natural' }],
    hasImageAnalysis: true, imageAnalysis: 'Se observan variaciones de pelaje.',
    chatbotTemperature: 0, chatbotPrompt: 'Instrucción personalizada de prueba',
  }
  const [{ json: result }] = run(code(main, 'Construir Configuración del Agente'), {
    $: () => ({ first: () => ({ json: cfg }) }),
  })
  assert.match(result.resourceQuery, /Representa ese proceso/)
  assert.match(result.resourceQuery, /selección natural/)
  assert.match(result.resourceQuery, /variaciones de pelaje/)
  assert.equal(result.requestedMode, 'recursos')
  assert.equal(result.pineconeNamespace, 'inst_tenant_curso_405')
  assert.equal(result.temperature, 0)
  assert.ok(!result.systemMessage.includes(cfg.chatbotPrompt))
  const prompt = runInNewContext(main.nodes.find(node => node.name === 'Agente del Curso').parameters.text.slice(3, -2), {
    $: () => ({ first: () => ({ json: cfg }) }),
    $json: { context: 'Las variaciones heredables se transmiten.' },
  })
  assert.ok(prompt.includes(cfg.chatbotPrompt))
  assert.ok(prompt.includes(cfg.message))
  assert.ok(prompt.indexOf('Las variaciones heredables se transmiten.') < prompt.lastIndexOf(cfg.message))
  assert.ok(result.resourceQuery.endsWith(cfg.message))
})

test('resource preparation honors an explicit no-evidence result and supports the legacy empty-context marker', () => {
  const mermaid = readWorkflow('tool-generador-mermaid.json')
  const prepare = ragResult => run(code(mermaid, 'Preparar Conocimiento'), {
    $: () => ({ first: () => ({ json: { query: 'Un diagrama', allowGeneralKnowledge: false } }) }),
    $input: { first: () => ({ json: ragResult }) },
  })[0].json
  assert.equal(prepare({ hasContext: false, context: 'La consulta no aportó evidencia.' }).hasContext, false)
  assert.equal(prepare({ context: 'No se encontró material relevante sobre el tema.' }).hasContext, false)
  const supported = prepare({ hasContext: true, context: 'Variación y supervivencia.' })
  assert.equal(supported.hasContext, true)
  assert.ok(supported.prompt.endsWith('Un diagrama'))
})

test('visual resources require a teaching explanation rather than returning an unexplained graphic', () => {
  const mermaid = readWorkflow('tool-generador-mermaid.json')
  const validate = resource => run(code(mermaid, 'Validar Mermaid'), {
    $input: { first: () => ({ json: { output: JSON.stringify(resource) } }) },
    $: () => ({ first: () => ({ json: { hasContext: true, citations: [] } }) }),
  })[0].json
  const resource = { title: 'Selección natural', explanation: 'Las ramas muestran condiciones concurrentes que afectan a la reproducción.', graphic: 'flowchart TD\nA-->C\nB-->C' }
  assert.equal(validate(resource).success, true)
  assert.equal(validate({ ...resource, explanation: '' }).success, false)
  assert.equal(validate({ ...resource, title: '' }).success, false)
})

test('chat propagates citations from mandatory and additional retrieval while leaving resource output independent', () => {
  const initial = { context: 'Darwin', hasContext: true, citations: [{ archivo: 'darwin.pdf', pagina: 10 }] }
  const additional = { citations: [{ archivo: 'darwin.pdf', pagina: 10 }, { archivo: 'darwin.pdf', pagina: 26 }] }
  const response = (requestedMode, subOutput) => run(code(main, 'Formatear Respuesta'), {
    $json: subOutput,
    $: name => ({ first: () => ({ json: name === 'Construir Configuración del Agente' ? { requestedMode } : initial }) }),
  })[0].json
  const chat = response('chat', {
    output: 'Respuesta académica',
    intermediateSteps: [{ action: { tool: 'rag_chat_tool' }, observation: JSON.stringify([additional]) }],
  })
  assert.equal(chat.answer, 'Respuesta académica')
  assert.equal(chat.hasContext, true)
  assert.deepEqual(chat.citations, [{ archivo: 'darwin.pdf', pagina: 10 }, { archivo: 'darwin.pdf', pagina: 26 }])
  const resource = response('recursos', { graphic: 'flowchart TD\nA-->B', citations: [], hasContext: false })
  assert.equal(resource.resource.graphic, 'flowchart TD\nA-->B')
  assert.deepEqual(resource.citations, [])
})

test('administration derives its namespace from institution/course and ignores caller namespace', () => {
  const result = validate({ action: 'clear_course', institucion_id: 'tenant-a', curso_id: 405, namespace: 'another-course' })
  assert.deepEqual(result, [{ json: { action: 'clear_course', archivo: null, namespace: 'inst_tenant-a_curso_405' } }])
  assert.throws(() => validate({ action: 'clear_course', curso_id: 405 }), /inválidos/)
  assert.throws(() => validate({ action: 'delete_document', institucion_id: 'tenant-a', curso_id: 405 }), /archivo/)
})

test('cleanup accepts only successful deletes or explicitly absent namespaces, never other HTTP errors', () => {
  const request = { action: 'clear_course', namespace: 'inst_tenant-a_curso_405' }
  const confirm = (result) => runInNewContext(`(function () { ${confirmCode} })()`, {
    $: () => ({ first: () => ({ json: request }) }),
    $input: { first: () => ({ json: result }) },
  })
  assert.equal(confirm({ statusCode: 200, body: {} })[0].json.success, true)
  assert.equal(confirm({ statusCode: 404, body: { code: 5, message: 'Namespace not found' } })[0].json.already_empty, true)
  for (const result of [{ statusCode: 401 }, { statusCode: 500 }, { statusCode: 404, body: { message: 'Not found' } }]) {
    assert.throws(() => confirm(result), /no confirmó/)
  }
})
