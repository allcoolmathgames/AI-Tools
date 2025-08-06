document.addEventListener('DOMContentLoaded', function() {

    //  Language Switcher Logic ---
    const languageSwitcher = document.getElementById('language-switcher');
    if (languageSwitcher) {
        languageSwitcher.addEventListener('change', (event) => {
            const selectedLang = event.target.value;
            if (typeof setLanguage === 'function') {
                setLanguage(selectedLang);
            }
        });
        if (typeof getPreferredLanguage === 'function') {
            languageSwitcher.value = getPreferredLanguage();
        }
    }
});