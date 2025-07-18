import logging
import re
import os # Added for environment variable access
import nltk # For NLTK data setup
import json # For JSON parsing

# --- Gemini API Configuration ---
# IMPORTANT: It is necessary to install the google-generativeai library.
# 'pip install google-generativeai' run karein.
try:
    import google.generativeai as genai
    # Configure your Gemini API key from environment variables for production.
    # On Railway, set a variable named GOOGLE_API_KEY with your actual API key.
    gemini_api_key = os.environ.get("GOOGLE_API_KEY")
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        logging.info("Google Generative AI library loaded and configured for summarizer_tool.")
        GEMINI_API_AVAILABLE = True
    else:
        logging.warning("GOOGLE_API_KEY environment variable not set. Gemini functions will not work in summarizer_tool.")
        GEMINI_API_AVAILABLE = False
        # Define a helper message for missing API key if it's not set
        def missing_api_key_error_msg(tool_name):
            return f"Error: Gemini API not configured for {tool_name}. Please ensure GOOGLE_API_KEY environment variable is set."
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in summarizer_tool.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for summarizer_tool: {e}. Gemini functions might not work.")
    GEMINI_API_AVAILABLE = False

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- NLTK Data Path Setup (Zaroori agar NLTK use ho) ---
# Create directory for NLTK data if it doesn't exist
nltk_data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'nltk_data')
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)
    logging.info(f"Created NLTK data directory: {nltk_data_dir}")
nltk.data.path.append(nltk_data_dir)
logging.info(f"NLTK data path added: {nltk_data_dir}")

# --- NLTK Data Download Check ---
def ensure_nltk_data():
    """Ensures necessary NLTK data is downloaded."""
    try:
        nltk.data.find('tokenizers/punkt')
        logging.info("NLTK 'punkt' tokenizer already exists.")
    except nltk.downloader.DownloadError:
        logging.info("Downloading NLTK 'punkt' tokenizer...")
        nltk.download('punkt', download_dir=nltk_data_dir)
        logging.info("NLTK 'punkt' tokenizer downloaded.")
    
    try:
        nltk.data.find('corpora/stopwords')
        logging.info("NLTK 'stopwords' corpus already exists.")
    except nltk.downloader.DownloadError:
        logging.info("Downloading NLTK 'stopwords' corpus...")
        nltk.download('stopwords', download_dir=nltk_data_dir)
        logging.info("NLTK 'stopwords' corpus downloaded.")

# Ensure NLTK data is available when the module starts
ensure_nltk_data()

# --- Gemini Model Helper Function ---
def get_gemini_model():
    """Helper function to get a Gemini model that supports generateContent."""
    if not GEMINI_API_AVAILABLE:
        # Provide specific error message if API is not available due to missing key
        raise Exception("Gemini API is not available. Ensure GOOGLE_API_KEY is set.")
    
    available_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    selected_model_name = None
    for model_info in available_models:
        # Prefer gemini-2.0-flash because it is efficient
        if 'gemini-2.0-flash' in model_info.name:
            selected_model_name = model_info.name
            break
    
    if not selected_model_name:
        if available_models:
            # If flash model is not found, use any available model
            selected_model_name = available_models[0].name
            logging.warning(f"gemini-2.0-flash not found. Using available model: {selected_model_name}")
        else:
            raise Exception("No Gemini model found that supports content generation.")
    
    return genai.GenerativeModel(selected_model_name)

# --- Summarizer Tool Logic ---
def summarize_text(text, length_ratio=0.5):
    """Summarizes the given text using the Gemini model."""
    if not GEMINI_API_AVAILABLE:
        logging.error(missing_api_key_error_msg("summarizer_tool"))
        return missing_api_key_error_msg("summarizer_tool")

    try:
        # Convert length_ratio to float
        length_ratio = float(length_ratio) 

        model = get_gemini_model()
        
        input_length = len(text.split())
        min_summary_words = max(20, int(input_length * (length_ratio - 0.2)))
        max_summary_words = max(min_summary_words + 10, int(input_length * length_ratio))

        prompt = (
            f"Please summarize the following text concisely. The summary should be between "
            f"{min_summary_words} and {max_summary_words} words, maintaining the core information. "
            f"Do not add any new information or elaborate excessively. Focus solely on extracting key points from the provided text.\n\n"
            f"Original text:\n---\n{text}\n---\n\nSummary:"
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=30,
                candidate_count=1,
            )
        )
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            summary_text = response.candidates[0].content.parts[0].text.strip()
            # Remove leading "Summary:" if present
            summary_text = re.sub(r'^(Summary:)?\s*', '', summary_text, flags=re.IGNORECASE).strip()
            return summary_text
        else:
            return "Gemini could not generate a summary. Please try different input."

    except Exception as e:
        logging.error(f"Error summarizing text with Gemini: {e}", exc_info=True)
        return f"Error: Summarization failed with Gemini. Details: {str(e)}"