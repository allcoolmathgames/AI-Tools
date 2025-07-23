// This script handles the client-side logic for the AI Email Subject Line Generator.

document.addEventListener('DOMContentLoaded', () => {
    // Get references to HTML elements
    const emailContentInput = document.getElementById('emailContentInput');
    const toneInput = document.getElementById('toneInput');
    const subjectsOutput = document.getElementById('subjectsOutput');
    const generateBtn = document.getElementById('generateBtn');
    const loader = document.getElementById('loader');
    const errorMessage = document.getElementById('errorMessage');

    // Add an event listener to the "Generate Subjects" button
    if (generateBtn) {
        generateBtn.addEventListener('click', async () => {
            const content = emailContentInput ? emailContentInput.value.trim() : '';
            const tone = toneInput ? toneInput.value : 'Professional'; // Default tone

            // Clear previous results and errors
            if (errorMessage) errorMessage.style.display = 'none';
            if (subjectsOutput) subjectsOutput.value = '';

            // Validate input
            if (!content) {
                if (errorMessage) {
                    errorMessage.textContent = 'Please describe what your email is about.';
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
                const response = await fetch('/api/generate_email_subjects', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        content: content,
                        tone: tone 
                    }),
                });

                const data = await response.json();

                if (!response.ok) {
                    // Handle errors returned from the backend
                    throw new Error(data.error || 'Failed to generate subject lines.');
                }

                // Display the generated subject lines in the output textarea
                if (subjectsOutput && data.subjects) {
                    // If subjects are an array, join them with newlines
                    if (Array.isArray(data.subjects)) {
                        subjectsOutput.value = data.subjects.join('\n');
                    } else {
                        subjectsOutput.value = data.subjects;
                    }
                } else {
                     throw new Error('Invalid response from server.');
                }

            } catch (error) {
                console.error('Error generating subject lines:', error);
                if (errorMessage) {
                    errorMessage.textContent = `Error: ${error.message}`;
                    errorMessage.style.display = 'block';
                }
            } finally {
                // Hide loader and re-enable the button
                if (loader) loader.style.display = 'none';
                if (generateBtn) {
                    generateBtn.disabled = false;
                    generateBtn.textContent = 'Generate Subjects';
                }
            }
        });
    }

});

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