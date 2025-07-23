// This script handles the client-side logic for the AI Product Description Generator Tool.

document.addEventListener('DOMContentLoaded', () => {
    // Get references to HTML elements
    const productNameInput = document.getElementById('productNameInput');
    const productKeywordsInput = document.getElementById('productKeywordsInput');
    const targetAudienceInput = document.getElementById('targetAudienceInput');
    const toneInput = document.getElementById('toneInput');
    const generateDescriptionBtn = document.getElementById('generateDescriptionBtn');
    const descriptionOutput = document.getElementById('descriptionOutput');
    const loader = document.getElementById('loader');
    const errorMessage = document.getElementById('errorMessage');
    const outputCounter = document.getElementById('outputCounter'); // Only output has a counter for description length

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
        if (generateDescriptionBtn) generateDescriptionBtn.disabled = false;
        if (descriptionOutput) descriptionOutput.value = ''; // Clear output
        if (outputCounter) updateWordCount(descriptionOutput, outputCounter); // Reset output word count
    }

    // Initial update on page load for output text area (it starts empty)
    if (descriptionOutput && outputCounter) {
        updateWordCount(descriptionOutput, outputCounter);
    }

    // Add event listeners to input fields to reset UI when user types
    if (productNameInput) {
        productNameInput.addEventListener('input', resetUI);
    }
    if (productKeywordsInput) {
        productKeywordsInput.addEventListener('input', resetUI);
    }
    if (targetAudienceInput) {
        targetAudienceInput.addEventListener('input', resetUI);
    }
    if (toneInput) {
        toneInput.addEventListener('change', resetUI); // For select element, 'change' is more appropriate
    }


    // Generate Description button click handler
    if (generateDescriptionBtn && productNameInput && descriptionOutput && loader && errorMessage) {
        generateDescriptionBtn.addEventListener('click', async () => {
            const productName = productNameInput.value.trim();
            const keywords = productKeywordsInput.value.trim();
            const targetAudience = targetAudienceInput.value.trim();
            const tone = toneInput.value.trim();

            // Basic validation: ensure product name or keywords are provided
            if (!productName && !keywords) {
                errorMessage.textContent = 'Please enter a product name or keywords to generate a description.';
                errorMessage.style.display = 'block';
                descriptionOutput.value = ''; // Clear any previous output
                if (outputCounter) updateWordCount(descriptionOutput, outputCounter);
                return;
            }

            // Clear previous output and error, show loader
            descriptionOutput.value = '';
            if (outputCounter) updateWordCount(descriptionOutput, outputCounter);
            errorMessage.style.display = 'none';
            loader.style.display = 'block';
            generateDescriptionBtn.disabled = true; // Disable button during processing

            try {
                // Fetch call to the Flask backend API endpoint
                // Removed direct Gemini API URL and apiKey variable.
                // The backend (product_description_generator_tool.py) will handle the Gemini API call securely.
                const response = await fetch('/api/generate_product_description', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    // Send data as expected by the Flask backend's API endpoint
                    body: JSON.stringify({ 
                        productName: productName,
                        productKeywords: keywords, // Ensure this matches backend parameter name
                        targetAudience: targetAudience, // Ensure this matches backend parameter name
                        tone: tone 
                    })
                });

                const data = await response.json();

                // Check for errors from the API
                if (!response.ok) {
                    // If response is not OK (e.g., 400, 500 status from Flask backend)
                    // The 'data' object from Flask will contain the error message
                    throw new Error(data.error || 'Failed to generate product description.');
                }

                // Display the generated description
                if (descriptionOutput && data.description) { // Check for 'description' key as returned by Flask backend
                    descriptionOutput.value = data.description;
                    updateWordCount(descriptionOutput, outputCounter);
                } else {
                    errorMessage.textContent = 'Error: Could not generate product description. Invalid response from AI or empty data.';
                    errorMessage.style.display = 'block';
                    console.error('Unexpected response structure from Flask backend:', data);
                }

            } catch (error) {
                console.error('Error during product description generation:', error);
                errorMessage.textContent = `Error: ${error.message}. Please try again.`;
                errorMessage.style.display = 'block';
                descriptionOutput.value = 'Could not generate product description. Please try again.';
                if (outputCounter) updateWordCount(descriptionOutput, outputCounter);
            } finally {
                // Hide loader and re-enable button
                if (loader) {
                    loader.style.display = 'none';
                }
                if (generateDescriptionBtn) {
                    generateDescriptionBtn.disabled = false;
                }
            }
        });
    }
})
    // --- FAQ Accordion Functionality ---
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