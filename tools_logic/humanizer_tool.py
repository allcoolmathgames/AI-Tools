import logging
import re
import os
import nltk # For NLTK data setup
import json # For JSON parsing

# --- Gemini API Configuration ---
# IMPORTANT: It is necessary to install the google-generativeai library.
# 'pip install google-generativeai' run karein.
try:
    import google.generativeai as genai
    # Your Gemini API key is configured here.
    # This key is crucial for using the Gemini model.
    # User-provided API key: AIzaSyBnLc4iJy4KFR5iA1Cwy6c207wAyMfwHn0
    genai.configure(api_key="AIzaSyBnLc4iJy4KFR5iA1Cwy6c207wAyMfwHn0")
    logging.info("Google Generative AI library loaded and configured for humanizer_tool.")
    GEMINI_API_AVAILABLE = True
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in humanizer_tool.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for humanizer_tool: {e}. Gemini functions might not work.")
    GEMINI_API_AVAILABLE = False

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- NLTK Data Path Setup ---
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
        raise Exception("Gemini API is not available.")
    
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

# --- Humanizer Tool Logic ---
def humanize_text(text, creativity=0.7):
    """Humanizes AI-generated text using the Gemini model."""
    if not GEMINI_API_AVAILABLE:
        logging.error("Gemini API is not available for humanization. Please install 'google-generativeai' and configure API key.")
        return f"Error: Gemini API not configured for humanization. Please install 'google-generativeai' and set your API key."

    try:
        model = get_gemini_model()
        
        prompt = (
            f"Please rewrite the following text in a more natural, human-like, and engaging way in English. " # Explicitly request English
            f"Aim for a {int(creativity*100)}% creative flair while maintaining the original meaning. "
            f"Remove any robotic or overly formal phrasing, and inject a natural flow. "
            f"Do not use any markdown formatting, such as **bold**, *italic*, or ##headings. Provide plain text.\n\n" # Added explicit markdown avoidance
            f"Original text:\n---\n{text}\n---\n\nRewritten human-like version:"
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.9,
                top_p=0.9,
                top_k=40,
                candidate_count=1,
            )
        )
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            humanized_text = response.candidates[0].content.parts[0].text.strip()
            # Remove leading "Rewritten human-like version:" if present
            humanized_text = re.sub(r'^(Rewritten human-like version:)?\s*', '', humanized_text, flags=re.IGNORECASE).strip()
            return humanized_text
        else:
            return "Gemini could not generate humanized text. Please try different input."

    except Exception as e:
        logging.error(f"Error humanizing text with Gemini: {e}", exc_info=True)
        return f"Error: Humanization failed with Gemini. Details: {str(e)}"