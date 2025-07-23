document.addEventListener('DOMContentLoaded', () => {
    const inputTextarea = document.getElementById('inputText');
    const inputCounter = document.getElementById('inputCounter');
    const checkPlagiarismBtn = document.getElementById('checkPlagiarismBtn');

    // Elements for circular progress bars (Plagiarism graphical result)
    const plagiarismPieChart = document.getElementById('plagiarismPieChart');
    const uniquePieChart = document.getElementById('uniquePieChart');
    const plagiarismPercentageSpan = document.getElementById('plagiarismPercentage');
    const uniquePercentageSpan = document.getElementById('uniquePercentage');

    // Element for AI detection result
    const aiDetectionResultDiv = document.getElementById('aiDetectionResult');
    
    // Element for displaying general error messages to the user
    const errorMessageDiv = document.getElementById('errorMessage');

    const loader = document.getElementById('loader'); 
    const resultCharts = document.querySelector('.result-charts'); 
    
    // Function to update word count for input
    function updateWordCount(textarea, counter) {
        if (!textarea || !counter) return;
        const text = textarea.value;
        const words = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
        counter.textContent = `${words} words`;
    }

    // Function to update a single pie chart visual and percentage
    function updatePieChart(element, percentage, color, labelSpan) {
        if (!element || !labelSpan) return;
        element.style.background = `conic-gradient(${color} 0% ${percentage}%, #e0e0e0 ${percentage}% 100%)`;
        labelSpan.textContent = `${percentage}%`;
    }

    // Function to display error messages
    function showErrorMessage(message) {
        if (!errorMessageDiv) return;
        errorMessageDiv.innerHTML = message; // Use innerHTML to render lists if needed
        errorMessageDiv.style.display = message ? 'block' : 'none';
    }

    // Function to reset UI to initial state
    function resetUI() {
        showErrorMessage('');
        updatePieChart(plagiarismPieChart, 0, 'red', plagiarismPercentageSpan);
        updatePieChart(uniquePieChart, 100, uniquePercentageSpan); // Should be 100% unique initially
        if (aiDetectionResultDiv) {
            aiDetectionResultDiv.textContent = 'Estimated AI Content: --';
            aiDetectionResultDiv.style.fontWeight = 'normal';
        }
    }

    // Event listener for input text area
    if (inputTextarea) {
        inputTextarea.addEventListener('input', () => {
            updateWordCount(inputTextarea, inputCounter);
        });
    }

    // Handle the "Analyze Text" button click
    if (checkPlagiarismBtn) {
        checkPlagiarismBtn.addEventListener('click', async () => {
            const text = inputTextarea.value.trim();

            if (text.length === 0) {
                showErrorMessage('Please enter text to analyze.');
                return;
            }
            
            // Clear previous error and show loader
            showErrorMessage('');
            if (loader) loader.style.display = 'block';
            checkPlagiarismBtn.disabled = true;
            checkPlagiarismBtn.textContent = 'Analyzing...';

            try {
                const response = await fetch('/api/check_plagiarism_ai', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text }),
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || `Server responded with status ${response.status}`);
                }

                // Process and display results
                const plagiarismScore = Math.round(parseFloat(data.plagiarism_percentage));
                const uniqueScore = 100 - plagiarismScore;
                updatePieChart(plagiarismPieChart, plagiarismScore, 'red', plagiarismPercentageSpan);
                updatePieChart(uniquePieChart, uniqueScore, 'green', uniquePercentageSpan);
                
                const aiPercentage = (parseFloat(data.ai_probability) * 100).toFixed(2);
                if (aiDetectionResultDiv) {
                    aiDetectionResultDiv.textContent = `Estimated AI Content: ${aiPercentage}%`;
                }

            } catch (error) {
                console.error('An unhandled error occurred:', error);
                showErrorMessage(`An unexpected error occurred: ${error.message}`);
                resetUI(); // Reset UI on error
            } finally {
                if (loader) loader.style.display = 'none';
                checkPlagiarismBtn.disabled = false;
                checkPlagiarismBtn.textContent = 'Analyze Text';
            }
        });
    }

    // Initial setup when the page loads
    updateWordCount(inputTextarea, inputCounter); 
    resetUI();
});

    // --- FAQ Accordion Functionality ---
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        const icon = item.querySelector('.faq-question i.fas'); 
        
        if (question && answer && icon) { 
            question.addEventListener('click', () => {
                const currentlyActive = document.querySelector('.faq-item.active');
                if (currentlyActive && currentlyActive !== item) {
                    const otherAnswer = currentlyActive.querySelector('.faq-answer');
                    const otherIcon = currentlyActive.querySelector('.faq-question i.fas');
                    currentlyActive.classList.remove('active');
                    otherAnswer.style.maxHeight = "0";
                    otherIcon.classList.replace('fa-minus', 'fa-plus');
                }
                
                item.classList.toggle('active');

                if (item.classList.contains('active')) {
                    answer.style.maxHeight = answer.scrollHeight + "px";
                    icon.classList.replace('fa-plus', 'fa-minus');
                } else {
                    answer.style.maxHeight = "0";
                    icon.classList.replace('fa-minus', 'fa-plus');
                }
            });
        }
    });