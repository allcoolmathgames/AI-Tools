const translations = {};

async function loadTranslations(pageName) {
    try {
        const response = await fetch(`/static/lang/${pageName}.json`);
        if (!response.ok) {
            console.warn(`Translation file not found or failed to load: /static/lang/${pageName}.json`);
            return;
        }
        const data = await response.json();
        Object.assign(translations, data);
    } catch (error) {
        console.error("Error loading translations:", error);
    }
}

function getTranslation(key) {
    const lang = localStorage.getItem('lang') || 'en';
    if (translations[key] && translations[key][lang]) {
        return translations[key][lang];
    }
    return key;
}

function translatePage() {
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        const lang = localStorage.getItem('lang') || 'en';
        if (translations[key] && translations[key][lang]) {
            if (element.tagName === 'TITLE' || (element.tagName === 'META' && element.name === 'description')) {
                element.setAttribute('content', translations[key][lang]);
            } else {
                element.textContent = translations[key][lang];
            }
        } else {
            if (translations[key] && translations[key]['en']) {
                element.textContent = translations[key]['en'];
            } else {
                console.warn(`Translation key '${key}' not found for language '${lang}' or 'en'.`);
            }
        }
    });

    document.querySelectorAll('[data-translate-placeholder]').forEach(element => {
        const key = element.getAttribute('data-translate-placeholder');
        const lang = localStorage.getItem('lang') || 'en';
        if (translations[key] && translations[key][lang]) {
            element.placeholder = translations[key][lang];
        } else if (translations[key] && translations[key]['en']) {
            element.placeholder = translations[key]['en'];
        }
    });
}

async function setLanguage(lang) {
    localStorage.setItem('lang', lang);
    document.body.setAttribute('data-lang', lang);

    const supportedLangs = ['ur', 'ar', 'pt', 'ru', 'es', 'de'];
    let currentRelativePath = window.location.pathname;
    let basePagePath = currentRelativePath;

    // Strip existing language prefix
    for (const prefix of supportedLangs) {
        if (basePagePath.startsWith(`/${prefix}/`)) {
            basePagePath = basePagePath.substring(prefix.length + 1);
            break;
        }
    }

    if (basePagePath === '') {
        basePagePath = '/';
    }

    const pageJsonMap = {
        '/': 'index',
        'gpa-calculator': 'index',
        'prior-semester-gpa': 'prior-semester-final-gpa',
        'gpa-planning': 'gpa-planning-calculator',
        'blogs': 'blogs',
        'privacy-policy': 'privacy-policy',
        'terms-conditions': 'terms-conditions',
        'about-us': 'about-us',
        'contact': 'contact'
    };
    const actualJsonFileName = pageJsonMap[basePagePath === '/' ? '/' : basePagePath.substring(1)] || null;

    await loadTranslations('common');
    if (actualJsonFileName) {
        await loadTranslations(actualJsonFileName);
    } else {
        console.log(`Translation not explicitly configured for page: ${basePagePath}. Only common translations will apply.`);
    }

    let newPathname = '';
    if (lang !== 'en') {
        newPathname = (basePagePath === '/') ? `/${lang}/` : `/${lang}${basePagePath}`;
    } else {
        newPathname = basePagePath;
    }

    history.replaceState({ path: newPathname }, '', newPathname);
    console.log(`Browser URL forcefully updated to: ${newPathname}`);

    const canonicalLink = document.querySelector('link[rel="canonical"]');
    if (canonicalLink) {
        canonicalLink.setAttribute('href', new URL(newPathname, window.location.origin).href);
        console.log(`Canonical updated: ${canonicalLink.href}`);
    }

    document.querySelectorAll('link[rel="alternate"][hreflang]').forEach(link => {
        const hreflang = link.getAttribute('hreflang');
        let currentLinkBaseHref = new URL(link.getAttribute('href')).pathname;

        for (const prefix of supportedLangs) {
            if (currentLinkBaseHref.startsWith(`/${prefix}/`)) {
                currentLinkBaseHref = currentLinkBaseHref.substring(prefix.length + 1);
                break;
            }
        }

        if (currentLinkBaseHref === '') {
            currentLinkBaseHref = '/';
        }

        let newAlternateHref = '';
        if (hreflang !== 'en') {
            newAlternateHref = (currentLinkBaseHref === '/') ? `/${hreflang}/` : `/${hreflang}${currentLinkBaseHref}`;
        } else {
            newAlternateHref = currentLinkBaseHref;
        }

        link.setAttribute('href', new URL(newAlternateHref, window.location.origin).href);
        console.log(`Hreflang link (${hreflang}) updated: ${link.href}`);
    });

    document.querySelectorAll('a[href]').forEach(linkElement => {
        const originalHref = linkElement.getAttribute('href');
        if (originalHref && originalHref.startsWith('/') && !originalHref.startsWith('//') && !originalHref.includes('://')) {
            let linkPath = originalHref;

            for (const prefix of supportedLangs) {
                if (linkPath.startsWith(`/${prefix}/`)) {
                    linkPath = linkPath.substring(prefix.length + 1);
                    break;
                }
            }

            if (linkPath === '') {
                linkPath = '/';
            }

            let newLinkHref = '';
            if (lang !== 'en') {
                newLinkHref = (linkPath === '/') ? `/${lang}/` : `/${lang}${linkPath}`;
            } else {
                newLinkHref = linkPath;
            }

            if (linkElement.getAttribute('href') !== newLinkHref) {
                linkElement.setAttribute('href', newLinkHref);
                console.log(`Link updated: ${originalHref} -> ${newLinkHref}`);
            }
        }
    });

    translatePage();
}

document.addEventListener('DOMContentLoaded', async () => {
    const languageSwitchers = document.querySelectorAll('.language-switcher');
    let initialLang = localStorage.getItem('lang') || 'en';

    await setLanguage(initialLang);

    languageSwitchers.forEach(switcher => {
        switcher.value = initialLang;
        switcher.addEventListener('change', async (event) => {
            const newLang = event.target.value;
            console.log(`Language changed via dropdown to: ${newLang}`);
            await setLanguage(newLang);
            languageSwitchers.forEach(otherSwitcher => {
                if (otherSwitcher !== event.target) {
                    otherSwitcher.value = newLang;
                }
            });
        });
    });
});
