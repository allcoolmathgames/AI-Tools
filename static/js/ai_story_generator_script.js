// This script handles the client-side logic for the AI Story Generator Tool.

document.addEventListener('DOMContentLoaded', () => {
    // Get references to HTML elements
    const storyTopicInput = document.getElementById('storyTopicInput');
    const storyGenreInput = document.getElementById('storyGenreInput');
    const storyCharactersInput = document.getElementById('storyCharactersInput');
    const generateStoryBtn = document.getElementById('generateStoryBtn');
    const storyOutput = document.getElementById('storyOutput');
    const loader = document.getElementById('loader');
    const errorMessage = document.getElementById('errorMessage');
    const outputCounter = document.getElementById('outputCounter'); // Only output has a counter for story length

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
        if (generateStoryBtn) generateStoryBtn.disabled = false;
        if (storyOutput) storyOutput.value = ''; // Clear output
        if (outputCounter) updateWordCount(storyOutput, outputCounter); // Reset output word count
    }

    // Initial update on page load for output text area (it starts empty)
    if (storyOutput && outputCounter) {
        updateWordCount(storyOutput, outputCounter);
    }

    // Add event listener to input fields to reset UI when user types
    if (storyTopicInput) {
        storyTopicInput.addEventListener('input', resetUI);
    }
    if (storyGenreInput) {
        storyGenreInput.addEventListener('change', resetUI); // For select element, 'change' is more appropriate
    }
    if (storyCharactersInput) {
        storyCharactersInput.addEventListener('input', resetUI);
    }


    // Generate Story button click handler
    if (generateStoryBtn && storyTopicInput && storyOutput && loader && errorMessage) {
        generateStoryBtn.addEventListener('click', async () => {
            const topic = storyTopicInput.value.trim();
            const genre = storyGenreInput.value.trim();
            const characters = storyCharactersInput.value.trim();

            // Basic validation: ensure at least a topic is provided
            if (!topic) {
                errorMessage.textContent = 'Please enter a story topic or keywords.';
                errorMessage.style.display = 'block';
                storyOutput.value = ''; // Clear any previous output
                if (outputCounter) updateWordCount(storyOutput, outputCounter);
                return;
            }

            // Clear previous output and error, show loader
            storyOutput.value = '';
            if (outputCounter) updateWordCount(storyOutput, outputCounter);
            errorMessage.style.display = 'none';
            loader.style.display = 'block';
            generateStoryBtn.disabled = true; // Disable button during processing

            try {
                // Corrected: Send request to your Flask backend API endpoint
                // Removed direct Gemini API URL and apiKey variable.
                // The backend (story_generator_tool.py) will handle the Gemini API call securely.
                const response = await fetch('/api/generate_story', { // Flask backend endpoint
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    // Send data as expected by the Flask backend's API endpoint
                    body: JSON.stringify({ 
                        topic: topic, 
                        genre: genre, 
                        characters: characters 
                    })
                });

                const data = await response.json();

                // Check for errors from the API
                if (!response.ok) {
                    // If response is not OK (e.g., 400, 500 status from Flask backend)
                    // The 'data' object from Flask will contain the error message
                    throw new Error(data.error || 'Failed to generate story.');
                }

                if (storyOutput && data.story) { // Check for 'story' key as returned by Flask backend
                    storyOutput.value = data.story;
                    updateWordCount(storyOutput, outputCounter);
                } else {
                    errorMessage.textContent = 'Error: Could not generate story. Invalid response from AI or empty data.';
                    errorMessage.style.display = 'block';
                    console.error('Unexpected response structure from Flask backend:', data);
                }

            } catch (error) {
                console.error('Error during story generation:', error);
                errorMessage.textContent = `Error: ${error.message}. Please try again.`;
                errorMessage.style.display = 'block';
                storyOutput.value = 'Could not generate story. Please try again.';
                if (outputCounter) updateWordCount(storyOutput, outputCounter);
            } finally {
                // Hide loader and re-enable button
                if (loader) {
                    loader.style.display = 'none';
                }
                if (generateStoryBtn) {
                    generateStoryBtn.disabled = false;
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