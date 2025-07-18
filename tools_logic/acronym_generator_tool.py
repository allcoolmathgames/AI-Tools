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
        logging.info("Google Generative AI library loaded and configured for acronym_generator_tool.")
        GEMINI_API_AVAILABLE = True
    else:
        logging.warning("GOOGLE_API_KEY environment variable not set. Gemini functions will not work in acronym_generator_tool.")
        GEMINI_API_AVAILABLE = False
        # Define a helper message for missing API key if it's not set
        def missing_api_key_error_msg(tool_name):
            return f"Error: Gemini API not configured for {tool_name}. Please ensure GOOGLE_API_KEY environment variable is set."
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in acronym_generator_tool.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for acronym_generator_tool: {e}. Gemini functions might not work.")
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

# --- Acronym Generator Tool Logic ---
def generate_acronym(text):
    """Generates an acronym using the Gemini model."""
    if not GEMINI_API_AVAILABLE:
        logging.error(missing_api_key_error_msg("acronym_generator_tool"))
        return missing_api_key_error_msg("acronym_generator_tool")
    try:
        model = get_gemini_model()
        prompt = (
            f"Generate a concise acronym in English from the following phrase or text. " # Explicitly request English
            f"Only use the first letter of each significant word. Exclude common words like 'a', 'an', 'the', 'of', 'for'. "
            f"Provide only the acronym itself, without any additional text or explanations. Do not use any markdown formatting like **bold**, *italic*, or ##headings.\n\n" # Add formatting instruction
            f"Text: {text}\n\nAcronym:"
        )
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                top_p=0.7,
                top_k=20,
                candidate_count=1,
            )
        )
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            acronym_text = response.candidates[0].content.parts[0].text.strip()
            # Remove leading "Acronym:" if present
            acronym_text = re.sub(r'^(Acronym:)?\s*', '', acronym_text, flags=re.IGNORECASE).strip()
            return acronym_text if acronym_text else "N/A"
        else:
            return "N/A" # Default if Gemini does not generate
    except Exception as e:
        logging.error(f"Error generating acronym with Gemini: {e}", exc_info=True)
        return f"Error: Acronym generation failed. Details: {str(e)}"