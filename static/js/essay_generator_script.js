// This script handles the client-side logic for the AI Essay Generator Tool.

document.addEventListener('DOMContentLoaded', () => {
    // Get references to HTML elements
    const essayTopicInput = document.getElementById('essayTopicInput');
    const essayToneInput = document.getElementById('essayToneInput');
    const essayLengthInput = document.getElementById('essayLengthInput');
    const essayLengthValue = document.getElementById('essayLengthValue');
    const generateEssayBtn = document.getElementById('generateEssayBtn');
    const essayOutput = document.getElementById('essayOutput');
    const loader = document.getElementById('loader');
    const errorMessage = document.getElementById('errorMessage');
    const outputCounter = document.getElementById('outputCounter');

    // Note: essayKeywordsInput is removed from the frontend as it's not directly used by the t5-small backend for structured inclusion in essay generation
    // If you want to include keywords, you'd need to modify the Python backend's essay generation logic
    // const essayKeywordsInput = document.getElementById('essayKeywordsInput'); // Removed from current usage

    // Function to update word count for a given textarea
    function updateWordCount(textArea, counterElement) {
        if (!textArea || !counterElement) return;
        const text = textArea.value;
        if (text.trim() === '') {
            counterElement.textContent = '0 words';
        } else {
            const wordCount = text.trim().split(/\s+/).filter(word => word.length > 0).length;
            counterElement.textContent = `${wordCount} words`;
        }
    }

    // Function to reset UI elements
    function resetUI() {
        if (loader) loader.style.display = 'none';
        if (errorMessage) errorMessage.style.display = 'none';
        if (generateEssayBtn) generateEssayBtn.disabled = false;
        // Do not clear essayOutput here, only when input changes
        if (essayOutput) updateWordCount(essayOutput, outputCounter); // Update output word count
    }

    // Initial update on page load for output text area (it starts empty)
    if (essayOutput && outputCounter) {
        updateWordCount(essayOutput, outputCounter);
    }

    // Update desired length display as slider moves
    if (essayLengthInput && essayLengthValue) {
        // Map slider value to descriptive lengths (e.g., "Short", "Medium", "Long")
        const lengthMap = {
            "short": "Short (approx. 300 words)",
            "medium": "Medium (approx. 700 words)",
            "long": "Long (approx. 1200 words)"
        };
        // Set initial display
        essayLengthValue.textContent = lengthMap[essayLengthInput.value] || essayLengthInput.value;

        essayLengthInput.addEventListener('input', () => {
            essayLengthValue.textContent = lengthMap[essayLengthInput.value] || essayLengthInput.value;
            resetUI(); // Reset UI whenever slider value changes
        });
    }

    // Add event listeners to input fields to reset UI when user types
    if (essayTopicInput) {
        essayTopicInput.addEventListener('input', () => {
            // Clear output and hide error/loader when input changes
            essayOutput.value = '';
            updateWordCount(essayOutput, outputCounter);
            resetUI();
        });
    }
    // If essayKeywordsInput was present, its event listener would be here too:
    // if (essayKeywordsInput) {
    //     essayKeywordsInput.addEventListener('input', () => {
    //         essayOutput.value = '';
    //         updateWordCount(essayOutput, outputCounter);
    //         resetUI();
    //     });
    // }
    if (essayToneInput) {
        essayToneInput.addEventListener('change', () => { // For select element, 'change' is more appropriate
            essayOutput.value = '';
            updateWordCount(essayOutput, outputCounter);
            resetUI();
        });
    }

    // Generate Essay button click handler
    if (generateEssayBtn && essayTopicInput && essayOutput && loader && errorMessage) {
        generateEssayBtn.addEventListener('click', async () => {
            const essayTopic = essayTopicInput.value.trim();
            // const essayKeywords = essayKeywordsInput.value.trim(); // Removed for t5-small model on backend
            const essayTone = essayToneInput.value.trim();
            const essayLength = essayLengthInput.value.trim(); // "short", "medium", "long" from the select value

            // Basic validation: ensure essay topic is provided
            if (!essayTopic) {
                errorMessage.textContent = 'Please enter an essay topic to generate an essay.';
                errorMessage.style.display = 'block';
                essayOutput.value = ''; // Clear any previous output
                if (outputCounter) updateWordCount(essayOutput, outputCounter);
                return;
            }

            // Clear previous output and error, show loader
            essayOutput.value = '';
            if (outputCounter) updateWordCount(essayOutput, outputCounter);
            errorMessage.style.display = 'none';
            loader.style.display = 'block';
            generateEssayBtn.disabled = true; // Disable button during processing

            try {
                // Prepare the data to send to your Flask backend
                const requestBody = {
                    topic: essayTopic,
                    length: essayLength, // 'short', 'medium', 'long'
                    style: essayTone // 'formal', 'informal', 'creative' etc.
                    // keywords: essayKeywords // Only if backend logic supports structured keyword inclusion
                };

                // Fetch call to your Flask backend's API endpoint
                const response = await fetch('/api/generate_essay', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestBody)
                });

                const data = await response.json(); // Parse the JSON response from Flask

                if (response.ok) { // Check if the HTTP status code is 2xx (success)
                    if (data.error) {
                        // Backend returned an error message in the response body
                        errorMessage.textContent = `Error: ${data.error}`;
                        errorMessage.style.display = 'block';
                        essayOutput.value = ''; // Clear output on error
                        console.error('Backend error:', data.error);
                    } else {
                        // Display the generated essay
                        essayOutput.value = data.essay;
                        updateWordCount(essayOutput, outputCounter);
                    }
                } else {
                    // Handle non-2xx HTTP responses (e.g., 400, 500 from Flask)
                    const errorMsg = data.error || 'An unexpected error occurred on the server.';
                    errorMessage.textContent = `Error: ${errorMsg}`;
                    errorMessage.style.display = 'block';
                    essayOutput.value = ''; // Clear output on error
                    console.error('Server error:', data);
                }

            } catch (error) {
                // Handle network errors or issues with fetch itself
                console.error('Error during essay generation fetch:', error);
                errorMessage.textContent = `Network Error: ${error.message}. Please check your connection and try again.`;
                errorMessage.style.display = 'block';
                essayOutput.value = 'Could not generate essay due to a network issue.';
                if (outputCounter) updateWordCount(essayOutput, outputCounter);
            } finally {
                // Hide loader and re-enable button
                loader.style.display = 'none';
                generateEssayBtn.disabled = false;
            }
        });
    }

});

    // --- FAQ Accordion Functionality (reused from main script for consistency) ---
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        const icon = item.querySelector('.faq-question i');

        if (question) {
            question.addEventListener('click', () => {
                // Close other active items
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
                // Toggle current item
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
    // --- End FAQ Accordion Functionality ---