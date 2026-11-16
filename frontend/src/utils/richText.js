import MarkdownIt from 'markdown-it'
import texmath from 'markdown-it-texmath'
import katex from 'katex'
import DOMPurify from 'dompurify'

// The tutor agent answers in Markdown with LaTeX math: \( \), \[ \], $ $ or $$ $$.
const markdown = new MarkdownIt({ html: false, linkify: true, breaks: true })
  .use(texmath, {
    engine: katex,
    delimiters: ['dollars', 'brackets'],
    katexOptions: { throwOnError: false, strict: 'ignore' },
  })

DOMPurify.addHook('afterSanitizeAttributes', (node) => {
  if (node.tagName === 'A' && node.getAttribute('href')) {
    node.setAttribute('target', '_blank')
    node.setAttribute('rel', 'noopener noreferrer')
  }
})

export function renderRichText(source) {
  return DOMPurify.sanitize(markdown.render(String(source || '')), {
    USE_PROFILES: { html: true, mathMl: true, svg: true },
    ADD_ATTR: ['target'],
  })
}
