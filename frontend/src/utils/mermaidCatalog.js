export const MERMAID_DIAGRAM_CATALOG = [
  { type: 'flowchart', label: 'Procesos y relaciones', pattern: /^(?:flowchart|graph)\b/i },
  { type: 'mindmap', label: 'Mapa mental', pattern: /^mindmap\b/i },
  { type: 'sequenceDiagram', label: 'Diagrama de secuencia', pattern: /^sequenceDiagram\b/i },
  { type: 'stateDiagram-v2', label: 'Diagrama de estados', pattern: /^stateDiagram(?:-v2)?\b/i },
  { type: 'classDiagram', label: 'Diagrama de clases', pattern: /^classDiagram\b/i },
  { type: 'erDiagram', label: 'Entidades y relaciones', pattern: /^erDiagram\b/i },
  { type: 'gantt', label: 'Cronograma Gantt', pattern: /^gantt\b/i },
  { type: 'timeline', label: 'Línea de tiempo', pattern: /^timeline\b/i },
  { type: 'pie', label: 'Gráfico circular', pattern: /^pie\b/i },
  { type: 'quadrantChart', label: 'Matriz de cuadrantes', pattern: /^quadrantChart\b/i },
  { type: 'journey', label: 'Recorrido por etapas', pattern: /^journey\b/i },
  { type: 'requirementDiagram', label: 'Diagrama de requisitos', pattern: /^requirementDiagram\b/i },
  { type: 'gitGraph', label: 'Historial de versiones', pattern: /^gitGraph\b/i },
  { type: 'sankey-beta', label: 'Flujo cuantitativo Sankey', pattern: /^sankey-beta\b/i },
  { type: 'xychart-beta', label: 'Gráfico de datos XY', pattern: /^xychart-beta\b/i },
  { type: 'block-beta', label: 'Diagrama de bloques', pattern: /^block-beta\b/i },
  { type: 'architecture-beta', label: 'Arquitectura de sistemas', pattern: /^architecture-beta\b/i },
  { type: 'packet-beta', label: 'Estructura de paquetes', pattern: /^packet-beta\b/i },
  { type: 'kanban', label: 'Tablero Kanban', pattern: /^kanban\b/i },
  { type: 'C4Context', label: 'Arquitectura C4: contexto', pattern: /^C4Context\b/i },
  { type: 'C4Container', label: 'Arquitectura C4: contenedores', pattern: /^C4Container\b/i },
]

export function getSupportedMermaidType(source) {
  const firstLine = String(source)
    .split(/\r?\n/)
    .map(line => line.trim())
    .find(line => line && !line.startsWith('%%'))

  return MERMAID_DIAGRAM_CATALOG.find(({ pattern }) => pattern.test(firstLine || ''))?.type || null
}

export function normalizeMermaidSource(source) {
  const type = getSupportedMermaidType(source)
  const lines = String(source).split(/\r?\n/)

  if (type === 'gantt' && !lines.some(line => /^\s*todayMarker\s+/i.test(line))) {
    const headerIndex = lines.findIndex(line => line.trim() && !line.trim().startsWith('%%'))
    // An out-of-range today marker can expand Mermaid's measured SVG bounds dramatically.
    lines.splice(headerIndex + 1, 0, 'todayMarker off')
    return lines.join('\n')
  }

  if (type === 'mindmap') {
    return lines.map((line, index) => (
      // Mermaid reads a bare child named "mindmap" as a new diagram declaration.
      index > 0 && line.trim().toLowerCase() === 'mindmap'
        ? `${line.match(/^\s*/)[0]}Mapa mental`
        : line
    )).join('\n')
  }

  if (type === 'journey') {
    // Journey section labels use no colon; colons delimit task scores below.
    return lines.map(line => line.replace(/^(\s*section\s+[^:\r\n]+):\s*(.*)$/i, '$1 - $2')).join('\n')
  }

  return String(source)
}
