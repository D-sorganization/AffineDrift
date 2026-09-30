;(function (root, factory) {
  const api = factory(root)
  root.AffineDriftSearchMaturityBadge = api

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api
  }
})(typeof window !== 'undefined' ? window : globalThis, function (root) {
  const MATURITY_INDEX_URL = '/data/search-maturity.json'
  const RESULT_LINK_SELECTOR = '.search-result-doc .search-result-link[href]'
  const TITLE_CONTAINER_SELECTOR = '.search-result-title-container'
  const BADGE_CLASS = 'badge--maturity'

  // Normalizes a Quarto search result href (absolute or relative to the
  // current page, possibly with a query string or #fragment) into the same
  // site-root-relative "dir/page.html" key generate_search_maturity_index.py
  // uses, so the two always agree without either side special-casing offsets.
  function normalizeHref(href) {
    if (!href) {
      return ''
    }
    try {
      const base = document.baseURI || root.location.href
      const url = new URL(href, base)
      return url.pathname.replace(/^\/+/, '')
    } catch (_error) {
      return href.replace(/^\/+/, '').split(/[?#]/)[0]
    }
  }

  function enhanceResults(scope, maturityIndex) {
    if (!maturityIndex || Object.keys(maturityIndex).length === 0) {
      return
    }
    const links = scope.querySelectorAll(RESULT_LINK_SELECTOR)
    links.forEach((link) => {
      const titleContainer = link.querySelector(TITLE_CONTAINER_SELECTOR)
      if (!titleContainer || titleContainer.querySelector(`.${BADGE_CLASS}`)) {
        return
      }
      const maturity = maturityIndex[normalizeHref(link.getAttribute('href'))]
      if (!maturity || !maturity.label) {
        return
      }
      const badge = document.createElement('span')
      badge.className = ['badge', BADGE_CLASS, maturity.variant ? `badge--${maturity.variant}` : '']
        .filter(Boolean)
        .join(' ')
      badge.textContent = maturity.label
      titleContainer.appendChild(badge)
    })
  }

  function init(options) {
    const opts = options || {}
    const fetchImpl = opts.fetch || (typeof root.fetch === 'function' ? root.fetch.bind(root) : null)
    if (!fetchImpl) {
      return false
    }
    const maturityUrl = opts.maturityUrl || MATURITY_INDEX_URL

    let maturityIndex = null
    fetchImpl(maturityUrl)
      .then((response) => (response && response.ok ? response.json() : {}))
      .then((data) => {
        maturityIndex = data || {}
        enhanceResults(document, maturityIndex)
      })
      .catch(() => {
        maturityIndex = {}
      })

    const observer = new root.MutationObserver(() => {
      if (maturityIndex) {
        enhanceResults(document, maturityIndex)
      }
    })
    observer.observe(document.body, { childList: true, subtree: true })

    return true
  }

  function initOnDomReady() {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', function () {
        init()
      })
    } else {
      init()
    }
  }

  if (!root.__AFFINEDRIFT_SEARCH_MATURITY_BADGE_NO_AUTO_INIT__) {
    initOnDomReady()
  }

  return {
    normalizeHref,
    enhanceResults,
    init,
  }
})
