/* -------------------------------------------------------
 * language.js (Final Version for ALL Pages & Tools)
 * - Detects current language from URL
 * - Loads /static/lang/<tool>.json dynamically
 * - Supports kebab-case tool names (abstract-generator, ai-email-generator, etc.)
 * - Handles header & footer translations
 * - Keeps English URLs clean (no /en), other langs as /<lang>/...
 * ----------------------------------------------------- */

(function () {
  const DEFAULT_LANG = 'en';

  // Supported languages
  const SUPPORTED_LANGS = ['en', 'es', 'id', 'pt', 'fr', 'nl', 'it', 'de', 'ru', 'ar', 'vi'];

  // Homepage key
  const DEFAULT_PAGE_KEY = 'summarizer';

  // All tool pages (kebab-case names)
  const TOOL_PAGES = new Set([
    'abstract-generator',
    'acronym-generator',
    'adjective-generator',
    'ai-email-generator',
    'ai-product-description-generator',
    'ai-story-generator',
    'ai-text-to-humanize',
    'article-rewriter',
    'business-name-generator',
    'conclusion-generator',
    'content-idea-generator',
    'email-subject-line-generator',
    'essay-generator',
    'grammar-checker',
    'hook-generator',
    'paraphrasing-tool',
    'plagiarism-checker',
    'slogan-generator',
    'summarizer',
    'title-generator',
    'trending-news-generator',
    'tools'
  ]);

  // Standalone pages (about, contact, etc.)
  const STANDALONE_PAGES = new Set([
    'about-us',
    'contact',
    'privacy-policy',
    'terms-conditions'
  ]);

  // Special pages (header & footer)
  const EXTRA_PAGES = ['header', 'footer'];

  // ---------- URL Helpers ----------

  function detectLangFromPath() {
    const parts = window.location.pathname.split('/');
    return SUPPORTED_LANGS.includes(parts[1]) ? parts[1] : DEFAULT_LANG;
  }

  function stripLangPrefix(pathname) {
    return pathname.replace(/^\/(en|es|id|pt|fr|nl|it|de|ru|ar|vi)(\/|$)/, '/');
  }

  function isBlog() {
    const clean = stripLangPrefix(window.location.pathname).toLowerCase();
    return clean.startsWith('/blogs/');
  }

  // Determine page key
  function getPageKey() {
    const clean = stripLangPrefix(window.location.pathname).toLowerCase();
    const parts = clean.split('/').filter(Boolean);

    if (parts.length === 0) return DEFAULT_PAGE_KEY; // homepage
    if (parts[0] === 'blogs') return null;           // blogs have no translation

    if (parts[0] === 'pages') {
      const file = (parts[1] || '').replace('.html', '');
      return STANDALONE_PAGES.has(file) ? file : null;
    }

    const first = parts[0];
    if (TOOL_PAGES.has(first)) return first;

    const maybeFile = first.replace('.html', '');
    if (STANDALONE_PAGES.has(maybeFile)) return maybeFile;

    return DEFAULT_PAGE_KEY;
  }

  // ---------- Apply Translations ----------

  function setText(el, val) {
    el.textContent = val;
  }

  function applyTranslations(dict, currentLang) {
    const langBlock = dict[currentLang] || dict[DEFAULT_LANG] || {};

    document.documentElement.setAttribute('lang', currentLang);
    if (langBlock.page_title) document.title = langBlock.page_title;

    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (langBlock[key] !== undefined) setText(el, langBlock[key]);
    });

    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (langBlock[key] !== undefined) el.setAttribute('placeholder', langBlock[key]);
    });

    document.querySelectorAll('[data-i18n-content]').forEach(el => {
      const key = el.getAttribute('data-i18n-content');
      if (langBlock[key] !== undefined) el.setAttribute('content', langBlock[key]);
    });
  }

  // ---------- Fetch + Init ----------

  async function loadTranslations(currentLang) {
    const pageKey = getPageKey();
    if (!pageKey) return;

    const cacheBuster = Date.now();
    const urls = [`/static/lang/${pageKey}.json?v=${cacheBuster}`];

    // Always load header & footer translations too
    EXTRA_PAGES.forEach(extra => urls.push(`/static/lang/${extra}.json?v=${cacheBuster}`));

    for (const url of urls) {
      try {
        const res = await fetch(url);
        if (!res.ok) {
          console.warn(`[i18n] Failed to fetch ${url} (status ${res.status})`);
          continue;
        }
        const data = await res.json();
        applyTranslations(data, currentLang);
      } catch (e) {
        console.error('[i18n] Translation load error:', e);
      }
    }
  }

  // ---------- Language Switcher ----------

  function initLangSwitcher(currentLang) {
    const switcher = document.getElementById('langSwitcher');
    if (!switcher) return;

    switcher.value = SUPPORTED_LANGS.includes(currentLang) ? currentLang : DEFAULT_LANG;

    switcher.addEventListener('change', e => {
      const lang = e.target.value;
      const clean = stripLangPrefix(window.location.pathname);
      const search = window.location.search || '';
      const hash = window.location.hash || '';

      if (lang === DEFAULT_LANG) {
        window.location.href = `${clean}${search}${hash}`;
      } else {
        const path = clean.startsWith('/') ? clean : `/${clean}`;
        window.location.href = `/${lang}${path}${search}${hash}`;
      }
    });
  }

  // ---------- Boot ----------

  document.addEventListener('DOMContentLoaded', () => {
    const currentLang = detectLangFromPath();
    initLangSwitcher(currentLang);

    if (!isBlog()) {
      loadTranslations(currentLang);
    }
  });

  // Make functions accessible for debugging
  window.__i18n = { getPageKey, detectLangFromPath };

})();
