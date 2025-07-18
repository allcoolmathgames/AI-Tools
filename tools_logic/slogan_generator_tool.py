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
        logging.info("Google Generative AI library loaded and configured for slogan_generator_tool.")
        GEMINI_API_AVAILABLE = True
    else:
        logging.warning("GOOGLE_API_KEY environment variable not set. Gemini functions will not work in slogan_generator_tool.")
        GEMINI_API_AVAILABLE = False
        # Define a helper message for missing API key if it's not set
        def missing_api_key_error_msg(tool_name):
            return f"Error: Gemini API not configured for {tool_name}. Please ensure GOOGLE_API_KEY environment variable is set."
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in slogan_generator_tool.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for slogan_generator_tool: {e}. Gemini functions might not work.")
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

# --- Slogan Generator Tool Logic ---
def generate_slogans(keywords, num_slogans=5):
    """Generates slogans using the Gemini model."""
    if not GEMINI_API_AVAILABLE:
        logging.error(missing_api_key_error_msg("slogan_generator_tool"))
        return [missing_api_key_error_msg("slogan_generator_tool")]
    try:
        model = get_gemini_model()
        response_schema = {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "slogan": {"type": "STRING"}
                }
            }
        }
        prompt = (
            f"Generate {num_slogans} unique, catchy, and memorable advertising slogans in English " # Explicitly request English
            f"for a brand or campaign related to '{keywords}'. "
            "Each slogan should be concise and highly impactful. Do not use any markdown formatting like **bold**, *italic*, or ##headings. Provide plain text." # Add formatting instruction
        )
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.9,
                top_p=0.9,
                top_k=40,
                candidate_count=1,
            )
        )
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            json_string = response.candidates[0].content.parts[0].text
            slogans_data = json.loads(json_string)
            slogans_list = [item["slogan"].strip() for item in slogans_data if "slogan" in item]
            
            unique_slogans = []
            seen_slogans = set()
            for slogan in slogans_list:
                if slogan.lower() not in seen_slogans:
                    unique_slogans.append(slogan)
                    seen_slogans.add(slogan.lower())
                if len(unique_slogans) >= num_slogans:
                    break
            
            if not unique_slogans:
                return ["Gemini could not generate any slogans. Please try different keywords."]
            
            return unique_slogans[:num_slogans]
        else:
            return ["Gemini could not generate any slogans. Please try different keywords."]

    except Exception as e:
        logging.error(f"Error generating slogans with Gemini: {e}", exc_info=True)
        return [f"Error: Slogan generation failed with Gemini. Details: {str(e)}"]