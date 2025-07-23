// This script handles the client-side logic for the AI Trending News Generator Tool.

document.addEventListener('DOMContentLoaded', () => {
    // Get references to HTML elements
    const newsTopicInput = document.getElementById('newsTopicInput');
    const newsCategoryInput = document.getElementById('newsCategoryInput');
    const numArticlesInput = document.getElementById('numArticlesInput');
    const generateNewsBtn = document.getElementById('generateNewsBtn');
    const newsOutput = document.getElementById('newsOutput');
    const loader = document.getElementById('loader');
    const errorMessage = document.getElementById('errorMessage');
    const outputCounter = document.getElementById('outputCounter');

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
        if (generateNewsBtn) generateNewsBtn.disabled = false;
        // Do not clear newsOutput here, only when input changes explicitly
        if (newsOutput) updateWordCount(newsOutput, outputCounter); // Update output word count
    }

    // Initial update on page load for output text area (it starts empty)
    if (newsOutput && outputCounter) {
        updateWordCount(newsOutput, outputCounter);
    }

    // Add event listeners to input fields to reset UI when user types/changes
    if (newsTopicInput) {
        newsTopicInput.addEventListener('input', () => {
            // Clear output and hide error/loader when input changes
            newsOutput.value = '';
            updateWordCount(newsOutput, outputCounter);
            resetUI();
        });
    }
    if (newsCategoryInput) {
        newsCategoryInput.addEventListener('change', () => { // For select element, 'change' is more appropriate
            newsOutput.value = '';
            updateWordCount(newsOutput, outputCounter);
            resetUI();
        });
    }
    if (numArticlesInput) {
        numArticlesInput.addEventListener('input', () => {
            newsOutput.value = '';
            updateWordCount(newsOutput, outputCounter);
            resetUI();
        });
    }

    // Generate News button click handler
    if (generateNewsBtn && newsOutput && loader && errorMessage) {
        generateNewsBtn.addEventListener('click', async () => {
            const topic = newsTopicInput.value.trim();
            const category = newsCategoryInput.value.trim();
            const numArticles = numArticlesInput.value.trim();
            console.log('DEBUG: Topic value:', topic); // Yeh line add karein
            console.log('DEBUG: Category value:', category); // Yeh line add karein

            // For debugging: check the actual value being retrieved from the dropdown
            // console.log('Category value from dropdown:', category); 
            // Ensure your HTML <option value="Politics">Politics</option> has correct values.

            // Basic validation: at least one input field should have a value
            if (!topic && !category) {
                errorMessage.textContent = 'Please enter a news topic/keywords or select a category.';
                errorMessage.style.display = 'block';
                newsOutput.value = ''; // Clear any previous output
                if (outputCounter) updateWordCount(newsOutput, outputCounter);
                return;
            }

            // Clear previous output and error, show loader
            newsOutput.value = '';
            if (outputCounter) updateWordCount(newsOutput, outputCounter);
            errorMessage.style.display = 'none';
            loader.style.display = 'block';
            generateNewsBtn.disabled = true; // Disable button during processing

            try {
                // Corrected: Send request to your Flask backend API endpoint
                // Removed direct Gemini API URL and apiKey variable.
                // The backend (trending_news_generator_tool.py) will handle the Gemini API call securely.
                const response = await fetch('/api/generate_trending_news', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    // Send data as expected by the Flask backend's API endpoint
                    body: JSON.stringify({ keywords: topic, category: category, num_articles: numArticles }), 
                });

                const data = await response.json();

                // Check for errors from the API
                if (!response.ok) {
                    // If response is not OK (e.g., 400, 500 status from Flask backend)
                    // The 'data' object from Flask will contain the error message
                    throw new Error(data.error || 'Failed to generate trending news.');
                }

                if (newsOutput && data.news_summary) { // Check for 'news_summary' key as returned by Flask backend
                    newsOutput.value = data.news_summary;
                    updateWordCount(newsOutput, outputCounter);
                } else {
                    errorMessage.textContent = 'Error: Could not generate trending news. Invalid response from AI or empty data.';
                    errorMessage.style.display = 'block';
                    console.error('Unexpected response structure from Flask backend:', data);
                }

            } catch (error) {
                console.error('Error during news generation:', error);
                errorMessage.textContent = `Error: ${error.message}. Please try again.`;
                errorMessage.style.display = 'block';
                newsOutput.value = 'Could not generate trending news. Please try again.';
                if (outputCounter) updateWordCount(newsOutput, outputCounter);
            } finally {
                // Hide loader and re-enable button
                if (loader) {
                    loader.style.display = 'none';
                }
                if (generateNewsBtn) {
                    generateNewsBtn.disabled = false;
                }
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