// This script handles the client-side logic for the AI Conclusion Generator.

document.addEventListener('DOMContentLoaded', () => {
    // Get references to HTML elements
    const inputText = document.getElementById('inputText');
    const conclusionOutput = document.getElementById('conclusionOutput');
    const generateBtn = document.getElementById('generateBtn');
    const loader = document.getElementById('loader');
    const errorMessage = document.getElementById('errorMessage');

    // Add an event listener to the "Generate Conclusion" button
    if (generateBtn) {
        generateBtn.addEventListener('click', async () => {
            const text = inputText ? inputText.value.trim() : '';

            // Clear previous results and errors
            if (errorMessage) errorMessage.style.display = 'none';
            if (conclusionOutput) conclusionOutput.value = '';

            // Validate input
            if (!text) {
                if (errorMessage) {
                    errorMessage.textContent = 'Please paste your main text to generate a conclusion.';
                    errorMessage.style.display = 'block';
                }
                return;
            }

            // Show loader and disable the button
            if (loader) loader.style.display = 'block';
            if (generateBtn) {
                generateBtn.disabled = true;
                generateBtn.textContent = 'Generating...';
            }

            try {
                // Make a POST request to the backend API
                const response = await fetch('/api/generate_conclusion', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        text: text 
                    }),
                });

                const data = await response.json();

                if (!response.ok) {
                    // Handle errors returned from the backend
                    throw new Error(data.error || 'Failed to generate conclusion.');
                }

                // Display the generated conclusion in the output textarea
                if (conclusionOutput && data.conclusion) {
                    conclusionOutput.value = data.conclusion;
                } else {
                     throw new Error('Invalid response from server.');
                }

            } catch (error) {
                console.error('Error generating conclusion:', error);
                if (errorMessage) {
                    errorMessage.textContent = `Error: ${error.message}`;
                    errorMessage.style.display = 'block';
                }
            } finally {
                // Hide loader and re-enable the button
                if (loader) loader.style.display = 'none';
                if (generateBtn) {
                    generateBtn.disabled = false;
                    generateBtn.textContent = 'Generate Conclusion';
                }
            }
        });
    }

    // --- FAQ Accordion Functionality (for consistency across pages) ---
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        const icon = item.querySelector('.faq-question i');

        if (question) {
            question.addEventListener('click', () => {
                const currentlyActive = document.querySelector('.faq-item.active');
                if (currentlyActive && currentlyActive !== item) {
                    currentlyActive.classList.remove('active');
                    const otherAnswer = currentlyActive.querySelector('.faq-answer');
                    const otherIcon = currentlyActive.querySelector('.faq-question i');
                    if (otherAnswer) otherAnswer.style.maxHeight = "0";
                    if (otherIcon) {
                        otherIcon.classList.remove('fa-minus');
                        otherIcon.classList.add('fa-plus');
                    }
                }
                
                item.classList.toggle('active');

                if (item.classList.contains('active')) {
                    if (answer) {
                        answer.style.maxHeight = answer.scrollHeight + "px";
                    }
                    if (icon) {
                        icon.classList.remove('fa-plus');
                        icon.classList.add('fa-minus');
                    }
                } else {
                    if (answer) {
                        answer.style.maxHeight = "0";
                    }
                    if (icon) {
                        icon.classList.remove('fa-minus');
                        icon.classList.add('fa-plus');
                    }
                }
            });
        }
    });
});