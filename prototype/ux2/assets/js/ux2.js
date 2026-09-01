/* ==========================================================================
   UX2-G2 PROTOTYPE RENDERERS — DHObjectLayout + BibliographicRecord
   Presentation-layer only. No domain DTOs. Slot presence contract per G1-A §1.2.
   DOM built via createElement/textContent — no innerHTML, no XSS surface.
   ========================================================================== */
(() => {
  

  function el(tag, className, text) {
    const node = document.createElement(tag)
    if (className) node.className = className
    if (text !== undefined) node.textContent = text
    return node
  }

  function statusEl(status, label) {
    const st = status || 'DATA_GAP'
    const node = el('span', 'hfm-status', label || st)
    node.setAttribute('data-status', st)
    return node
  }

  /* ---- DHObjectLayout -------------------------------------------------- */
  /* config.header/context/evidence/relations:
     { state: PRESENT|ABSENT_OPTIONAL|INCOMPLETE_WITH_EVIDENCE_STATE,
       build: () => HTMLElement[] (builders), label?, note?, status?,
       titleTag?: presentation-only object-title heading level } */
  /*
   * titleTag (header slot only, presentation-only, OPTIONAL):
   *   'h1'..'h6' | 1..6 | 'p' | 0 | 'none'
   * Declares the semantic heading level of the DHObjectLayout object title
   * so it fits the DOCUMENT OUTLINE of the surface that hosts the layout
   * (G2 F-1: no fixed <h3>; level adapts to context). 'p' / 0 / 'none'
   * renders the title as a non-heading element and defers heading
   * semantics entirely to the outer surface. When titleTag is set, the
   * renderer re-tags any built node with class 'dh-object__title' to the
   * declared tag (deterministic enforcement). Default (no titleTag): the
   * tag created by the surface's build() is kept unchanged.
   */
  window.renderDHObjectLayout = (container, config) => {
    const article = el('article', 'dh-object')
    article.setAttribute('data-primitive', 'dh-object')

    const titles = { header: '对象', context: '语境', evidence: '证据', relations: '关联' }
    ;['header', 'context', 'evidence', 'relations'].forEach((slotKey) => {
      const slot = config[slotKey]
      if (!slot) return
      if (slot.state === 'ABSENT_OPTIONAL') return // collapses completely
      const section = el('section', 'dh-object__slot')
      section.setAttribute('data-slot', slotKey)
      section.setAttribute('data-slot-state', slot.state || 'PRESENT')
      section.appendChild(el('p', 'dh-object__slot-title', titles[slotKey]))
      if (slot.state === 'INCOMPLETE_WITH_EVIDENCE_STATE') {
        const note = el('div', 'incomplete-note')
        note.setAttribute('role', 'status')
        note.appendChild(statusEl(slot.status, slot.label))
        note.appendChild(el('span', null, slot.note || ''))
        section.appendChild(note)
      }
      ;(slot.build ? slot.build() : []).forEach((n) => {
        if (slotKey === 'header' && slot.titleTag && n.nodeType === 1 && n.classList.contains('dh-object__title')) {
          section.appendChild(dhObjectTitle(slot.titleTag, n.textContent))
        } else {
          section.appendChild(n)
        }
      })
      article.appendChild(section)
    })

    container.textContent = ''
    container.appendChild(article)
  }

  /* ---- DHObjectLayout object title -------------------------------------- */
  /* Reusable presentation-only factory: creates the object title at the
     semantic level chosen by the surface to fit its document outline.
     tagOrLevel: 'h1'..'h6' | 1..6 | 'p' | 0 | 'none'. Invalid values fall
     back to a non-heading <p> (heading semantics deferred to the surface). */
  window.dhObjectTitle = (tagOrLevel, text) => {
    let tag = 'p'
    if (typeof tagOrLevel === 'number' && tagOrLevel >= 1 && tagOrLevel <= 6) tag = 'h' + tagOrLevel
    else if (typeof tagOrLevel === 'string' && /^h[1-6]$/.test(tagOrLevel)) tag = tagOrLevel
    const node = el(tag, 'dh-object__title', text)
    return node
  }

  /* ---- BibliographicRecord --------------------------------------------- */
  /* record: { title, meta: [{label, value}], status?, statusLabel? } */
  window.renderBibRecord = (container, record) => {
    const wrap = el('div', 'bib-record')
    wrap.setAttribute('data-primitive', 'bib-record')
    const title = el('p', 'bib-record__title')
    if (record.status) title.appendChild(statusEl(record.status, record.statusLabel || record.status))
    title.appendChild(document.createTextNode(record.title))
    wrap.appendChild(title)
    const meta = el('p', 'bib-record__meta')
    ;(record.meta || []).forEach((m) => {
      const span = el('span')
      span.appendChild(el('b', null, m.label))
      span.appendChild(document.createTextNode(' ' + m.value))
      meta.appendChild(span)
    })
    wrap.appendChild(meta)
    container.textContent = ''
    container.appendChild(wrap)
  }

  /* ---- status badge helper ---------------------------------------------- */
  window.badge = (status, label) => statusEl(status, label)
})()
