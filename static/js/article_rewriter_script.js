const inputText = document.getElementById('inputText');
const rewrittenText = document.getElementById('rewrittenText'); // Changed from outputText
const rewriteBtn = document.getElementById('rewriteBtn');
const creativitySlider = document.getElementById('creativitySlider'); // Changed from lengthSlider
const creativityValue = document.getElementById('creativityValue'); // Changed from sliderValue
const inputWordCount = document.getElementById('inputWordCount'); // Changed from inputCounter
const outputWordCount = document.getElementById('outputWordCount'); // Changed from outputCounter
const errorMessage = document.getElementById('errorMessage');
const loader = document.getElementById('loader');

// Update slider value display
if (creativitySlider && creativityValue) {
    creativityValue.textContent = `${creativitySlider.value}%`;
    creativitySlider.addEventListener('input', () => {
        creativityValue.textContent = `${creativitySlider.value}%`;
    });
}

// Word counter
function updateWordCount(textArea, counterElement) {
    if (!textArea || !counterElement) return;
    const text = textArea.value.trim();
    counterElement.textContent = text ? text.split(/\s+/).length : 0; // Updated to show only number
}

// Input listener
if (inputText) {
    inputText.addEventListener('input', () => {
        updateWordCount(inputText, inputWordCount);
        rewrittenText.value = '';
        updateWordCount(rewrittenText, outputWordCount);
        if (errorMessage) errorMessage.style.display = 'none';
        if (loader) loader.style.display = 'none';
    });
    updateWordCount(inputText, inputWordCount);
}

// Rewrite button click
if (rewriteBtn) {
    rewriteBtn.addEventListener('click', async () => {
        if (!inputText || !rewrittenText || !creativitySlider || !errorMessage || !loader) return;

        const text = inputText.value.trim();
        const creativity = parseInt(creativitySlider.value) / 100;

        rewrittenText.value = '';
        updateWordCount(rewrittenText, outputWordCount);
        errorMessage.style.display = 'none';

        if (!text) {
            errorMessage.textContent = 'Please enter an article to rewrite.';
            errorMessage.style.display = 'block';
            return;
        }

        loader.style.display = 'block';
        rewriteBtn.disabled = true;
        rewriteBtn.textContent = 'Rewriting...';
        rewriteBtn.classList.add('loading');

        try {
            const response = await fetch('/api/rewrite', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, creativity }),
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Failed to rewrite article.');

            rewrittenText.value = data.rewritten_text;
        } catch (error) {
            errorMessage.textContent = `Error: ${error.message}`;
            errorMessage.style.display = 'block';
            rewrittenText.value = 'An error occurred during rewriting. Please try again.';
        } finally {
            loader.style.display = 'none';
            rewriteBtn.disabled = false;
            rewriteBtn.textContent = 'Rewrite Article';
            rewriteBtn.classList.remove('loading');
            updateWordCount(rewrittenText, outputWordCount);
        }
    });
}

// Output initial word count
if (rewrittenText && outputWordCount) {
    updateWordCount(rewrittenText, outputWordCount);
}

// FAQ toggle
const faqItems = document.querySelectorAll('.faq-item');
faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    const answer = item.querySelector('.faq-answer');
    const icon = item.querySelector('.faq-question i');

    if (question) {
        question.addEventListener('click', () => {
            const active = document.querySelector('.faq-item.active');
            if (active && active !== item) {
                active.classList.remove('active');
                const a = active.querySelector('.faq-answer');
                const i = active.querySelector('.faq-question i');
                if (a) a.style.maxHeight = '0';
                if (i) {
                    i.classList.remove('fa-minus');
                    i.classList.add('fa-plus');
                }
            }

            item.classList.toggle('active');
            if (item.classList.contains('active')) {
                if (answer) answer.style.maxHeight = answer.scrollHeight + 'px';
                if (icon) {
                    icon.classList.remove('fa-plus');
                    icon.classList.add('fa-minus');
                }
            } else {
                if (answer) answer.style.maxHeight = '0';
                if (icon) {
                    icon.classList.remove('fa-minus');
                    icon.classList.add('fa-plus');
                }
            }
        });
    }
});