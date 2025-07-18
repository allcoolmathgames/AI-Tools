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
        logging.info("Google Generative AI library loaded and configured for rewriter_tool.")
        GEMINI_API_AVAILABLE = True
    else:
        logging.warning("GOOGLE_API_KEY environment variable not set. Gemini functions will not work in rewriter_tool.")
        GEMINI_API_AVAILABLE = False
        # Define a helper message for missing API key if it's not set
        def missing_api_key_error_msg(tool_name):
            return f"Error: Gemini API not configured for {tool_name}. Please ensure GOOGLE_API_KEY environment variable is set."
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in rewriter_tool.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for rewriter_tool: {e}. Gemini functions might not work.")
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

# --- Article Rewriter Tool Logic ---
def rewrite_article(text, creativity=0.5):
    """Rewrites the given text using the Gemini model."""
    if not GEMINI_API_AVAILABLE:
        logging.error(missing_api_key_error_msg("rewriter_tool"))
        return f"Error: Gemini API not configured for rewriting. Please install 'google-generativeai' and set your API key."

    try:
        model = get_gemini_model()
        
        prompt = (
            f"Rewrite the following text in English to make it unique and engaging. " # Explicitly request English
            f"Adjust the tone and style with a creativity level of {int(creativity*100)}%. "
            f"Maintain the original meaning but rephrase sentences and vocabulary significantly. "
            f"Do not use any markdown formatting, such as **bold**, *italic*, or ##headings. Provide plain text.\n\n" # Add formatting instruction
            f"Original text:\n---\n{text}\n---\n\nRewritten text:"
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.5 + (creativity * 0.5), # Adjust temperature based on creativity level
                top_p=0.9,
                top_k=40,
                candidate_count=1,
            )
        )
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            rewritten_text = response.candidates[0].content.parts[0].text.strip()
            # Remove leading "Rewritten text:" if present
            rewritten_text = re.sub(r'^(Rewritten text:)?\s*', '', rewritten_text, flags=re.IGNORECASE).strip()
            return rewritten_text
        else:
            return "Gemini could not generate rewritten text. Please try different input."

    except Exception as e:
        logging.error(f"Error rewriting text with Gemini: {e}", exc_info=True)
        return f"Error: Rewriting failed with Gemini. Details: {str(e)}"

# --- Paraphrasing Tool Logic ---
def paraphrase_text(text):
    """Paraphrases the given text by calling the rewrite_article function."""
    # Paraphrasing for the rewriter tool uses a default creativity level
    return rewrite_article(text, creativity=0.7)