document.addEventListener('DOMContentLoaded', function() {
    // --- FAQ Section Toggle ---
    document.querySelectorAll('.faq-section .faq-item h3').forEach(header => {
        if (!header.querySelector('.toggle-icon')) {
            header.innerHTML += ' <span class="toggle-icon">-</span>';
        }
        const paragraph = header.nextElementSibling;
        if (paragraph && paragraph.tagName === 'P') {
            paragraph.style.maxHeight = paragraph.scrollHeight + "px";
            paragraph.style.overflow = 'hidden';
            paragraph.style.transition = 'max-height 0.3s ease-out';
            header.classList.add('active');
        }
        header.addEventListener('click', () => {
            const paragraph = header.nextElementSibling;
            const toggleIcon = header.querySelector('.toggle-icon');
            document.querySelectorAll('.faq-section .faq-item p').forEach(p => {
                if (p !== paragraph && p.style.maxHeight && p.style.maxHeight !== '0px') {
                    p.style.maxHeight = '0';
                    p.previousElementSibling.querySelector('.toggle-icon').textContent = '+';
                    p.previousElementSibling.classList.remove('active');
                }
            });
            if (paragraph.style.maxHeight && paragraph.style.maxHeight !== '0px') {
                paragraph.style.maxHeight = '0';
                toggleIcon.textContent = '+';
                header.classList.remove('active');
            } else {
                paragraph.style.maxHeight = paragraph.scrollHeight + "px";
                toggleIcon.textContent = '-';
                header.classList.add('active');
            }
        });
    });

    // --- Language Switcher Logic ---
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