/* -------------------------------------------------------
 * language.js
 * - Detects current language from URL
 * - Loads the right /static/lang/<page>.json
 * - Replaces texts marked with data-i18n / data-i18n-placeholder
 * - Keeps English URLs clean (no /en), other langs as /<lang>/...
 * ----------------------------------------------------- */

(function () {
  const DEFAULT_LANG = 'en';

  // The languages you support
  const SUPPORTED_LANGS = ['en', 'es', 'id', 'br', 'fr', 'nl', 'it', 'de', 'ru', 'ar', 'vi'];

  // Homepage == summarizer
  const DEFAULT_PAGE_KEY = 'summarizer';

  // Tool pages (folder names) you localized -> <name>.json
  const TOOL_PAGES = new Set([
    'trending_news_generator',
    'title_generator',
    'summarizer',
    'slogan_generator',
    'plagiarism_checker',
    'paraphrasing_tool',
    'hook_generator',
    'grammar_checker',
    'essay_generator',
    'email_subject_line_generator',
    'content_idea_generator',
    'conclusion_generator',
    'business_name_generator',
    'article_rewriter',
    'ai_text_to_humanize',
    'ai_story_generator',
    'ai_product_description_generator',
    'ai_email_generator',
    'adjective_generator',
    'acronym_generator',
    'abstract_generator',
    'index' // only if you ever really use index.json
  ]);

  // Standalone pages (templates/pages/...)
  const STANDALONE_PAGES = new Set([
    'about_us',
    'contact',
    'privacy_policy',
    'terms_conditions'
  ]);

  // ---------- URL helpers ----------

  function detectLangFromPath() {
    const parts = window.location.pathname.split('/');
    return SUPPORTED_LANGS.includes(parts[1]) ? parts[1] : DEFAULT_LANG;
  }

  function stripLangPrefix(pathname) {
    return pathname.replace(/^\/(en|es|id|br|fr|nl|it|de|ru|ar|vi)(\/|$)/, '/');
  }

  function isBlog() {
    const clean = stripLangPrefix(window.location.pathname).toLowerCase();
    return clean.startsWith('/blogs/');
  }

  /**
   * Decide which json to load for this route
   * Rules:
   *   - "/" -> DEFAULT_PAGE_KEY (summarizer)
   *   - "/<tool>[/index.html]" -> <tool>
   *   - "/pages/<page>.html" -> <page> (if in STANDALONE_PAGES)
   *   - otherwise null
   */
  function getPageKey() {
    const clean = stripLangPrefix(window.location.pathname).toLowerCase();
    const parts = clean.split('/').filter(Boolean); // remove empty

    // Root "/" => your homepage (summarizer)
    if (parts.length === 0) return DEFAULT_PAGE_KEY;

    // Blogs are not localized
    if (parts[0] === 'blogs') return null;

    // /pages/about_us.html
    if (parts[0] === 'pages') {
      const file = (parts[1] || '').replace('.html', '');
      return STANDALONE_PAGES.has(file) ? file : null;
    }

    // /summarizer/, /summarizer/index.html, etc.
    const first = parts[0];
    if (TOOL_PAGES.has(first)) return first;

    // /about_us.html directly
    const maybeFile = first.replace('.html', '');
    if (STANDALONE_PAGES.has(maybeFile)) return maybeFile;

    // Fallback to homepage key
    return DEFAULT_PAGE_KEY;
  }

  // ---------- Apply translations ----------

  function setText(el, val) {
    // If you ever store HTML in your JSON, switch to innerHTML
    el.textContent = val;
  }

  function applyTranslations(dict, currentLang) {
    const langBlock = dict[currentLang] || dict[DEFAULT_LANG] || {};

    // Update document language attribute
    document.documentElement.setAttribute('lang', currentLang);

    // document.title
    if (langBlock.page_title) document.title = langBlock.page_title;

    // Regular text nodes
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (langBlock[key] !== undefined) setText(el, langBlock[key]);
    });

    // placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (langBlock[key] !== undefined) el.setAttribute('placeholder', langBlock[key]);
    });
  }

  // ---------- Fetch + init ----------

  async function loadTranslations(currentLang) {
    const pageKey = getPageKey();
    if (!pageKey) return; // nothing to translate (blogs or explicitly skipped)

    const cacheBuster = Date.now(); // avoid dev cache issues
    const url = `/static/lang/${pageKey}.json?v=${cacheBuster}`;

    try {
      const res = await fetch(url);
      if (!res.ok) {
        console.error(`[i18n] Failed to fetch ${url} (status ${res.status})`);
        return;
      }
      const data = await res.json();
      applyTranslations(data, currentLang);
    } catch (e) {
      console.error('[i18n] Translation load error:', e);
    }
  }

  // ---------- Switcher ----------

  function initLangSwitcher(currentLang) {
    const switcher = document.getElementById('langSwitcher');
    if (!switcher) return;

    // Set current value
    switcher.value = SUPPORTED_LANGS.includes(currentLang) ? currentLang : DEFAULT_LANG;

    switcher.addEventListener('change', e => {
      const lang = e.target.value;
      const clean = stripLangPrefix(window.location.pathname);
      const search = window.location.search || '';
      const hash = window.location.hash || '';

      if (lang === DEFAULT_LANG) {
        // English => no prefix
        window.location.href = `${clean}${search}${hash}`;
      } else {
        // other => /<lang>/...
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
})();
