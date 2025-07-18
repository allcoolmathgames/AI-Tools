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
        logging.info("Google Generative AI library loaded and configured for essay_generator_tool.")
        GEMINI_API_AVAILABLE = True
    else:
        logging.warning("GOOGLE_API_KEY environment variable not set. Gemini functions will not work in essay_generator_tool.")
        GEMINI_API_AVAILABLE = False
        # Define a helper message for missing API key if it's not set
        def missing_api_key_error_msg(tool_name):
            return f"Error: Gemini API not configured for {tool_name}. Please ensure GOOGLE_API_KEY environment variable is set."
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in essay_generator_tool.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for essay_generator_tool: {e}. Gemini functions might not work.")
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

# --- Essay Generator Tool Logic ---
def generate_essay(topic, length="medium", style="formal", keywords=""):
    """Generates essay content using the Gemini model."""
    if not GEMINI_API_AVAILABLE:
        logging.error(missing_api_key_error_msg("essay_generator_tool"))
        return missing_api_key_error_msg("essay_generator_tool")

    length_map = {
        "short": "around 200-300 words",
        "medium": "around 500-700 words",
        "long": "around 1000-1200 words",
        "100": "around 100 words",
        "1500": "around 1500 words",
        "500": "around 500 words",
        "750": "around 750 words",
        "1000": "around 1000 words",
        "1250": "around 1250 words",
        "1400": "around 1400 words",
        "150": "around 150 words",
        "200": "around 200 words",
        "250": "around 250 words",
        "300": "around 300 words",
        "350": "around 350 words",
        "400": "around 400 words",
        "450": "around 450 words",
        "550": "around 550 words",
        "600": "around 600 words",
        "650": "around 650 words",
        "700": "around 700 words",
        "800": "around 800 words",
        "850": "around 850 words",
        "900": "around 900 words",
        "950": "around 950 words",
        "1050": "around 1050 words",
        "1100": "around 1100 words",
        "1150": "around 1150 words",
        "1200": "around 1200 words",
        "1300": "around 1300 words",
        "1350": "around 1350 words",
        "1450": "around 1450 words",
    }
    word_count_target = length_map.get(str(length).lower(), "a reasonable length (500-700 words)")

    try:
        model = get_gemini_model()
        
        prompt = (
            f"Write an essay in English on the topic: '{topic}'.\n" 
            f"The essay should be {word_count_target} and written in a {style} style. "
        )
        if keywords:
            prompt += f"Include these keywords: {keywords}. "
        prompt += "Include an introduction, body paragraphs with supporting details, and a conclusion. "
        prompt += "Do not use markdown formatting like **bold** or *italic*. Present the text as plain paragraphs." 
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                top_p=0.8,
                top_k=30,
                candidate_count=1,
            )
        )
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            generated_essay = response.candidates[0].content.parts[0].text.strip()
            return generated_essay
        else:
            return "Gemini could not generate an essay. Please try a different topic or adjust parameters."

    except Exception as e:
        logging.error(f"Error generating essay with Gemini: {e}", exc_info=True)
        return f"Error: Essay generation failed with Gemini. Details: {str(e)}"