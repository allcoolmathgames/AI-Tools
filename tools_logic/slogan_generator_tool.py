import logging
import re
import os
import nltk
import json

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Helper function for missing API key messages (defined globally to ensure availability)
def missing_api_key_error_msg(tool_name):
    return f"Error: Gemini API not configured for {tool_name}. Please ensure GOOGLE_API_KEY environment variable is set."

# --- Gemini API Configuration ---
# IMPORTANT: It is necessary to install the google-generativeai library.
# 'pip install google-generativeai' run karein.
GEMINI_API_AVAILABLE = False
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
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in slogan_generator_tool.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for slogan_generator_tool: {e}. Gemini functions might not work.")
    GEMINI_API_AVAILABLE = False


# --- NLTK Data Path Setup ---
# Define NLTK data directory to a universally writable path like /app/nltk_data
NLTK_DATA_DIR = os.path.join('/app', 'nltk_data')
os.makedirs(NLTK_DATA_DIR, exist_ok=True) # Ensure directory exists
logging.info(f"Created NLTK data directory (if not exists): {NLTK_DATA_DIR}")
nltk.data.path.append(NLTK_DATA_DIR) # Add to NLTK's search path
logging.info(f"NLTK data path added: {NLTK_DATA_DIR}")

# --- NLTK Data Download Check ---
def ensure_nltk_data():
    """Ensures necessary NLTK data (punkt, stopwords) are available by checking.
        Downloads are expected to be handled during the build process via a separate script."""
    try:
        # Check if 'punkt' tokenizer is available
        nltk.data.find('tokenizers/punkt')
        logging.info("NLTK 'punkt' tokenizer is available.")
        
        # Check if 'stopwords' corpus is available
        nltk.data.find('corpora/stopwords')
        logging.info("NLTK 'stopwords' corpus is available.")
        
        return True # Indicate success
    except LookupError as e:
        # If data is not found, log an error indicating it needs pre-downloading
        logging.error(f"NLTK data missing: {e}. Please ensure data is pre-downloaded during build process into {NLTK_DATA_DIR}.")
        return False # Indicate failure
    except Exception as e:
        # Catch any other unexpected errors during data check
        logging.error(f"NLTK data check failed: {e}")
        return False # Indicate failure

# Call NLTK data check once on module load
# Store the status to use later if needed
_nltk_data_available = ensure_nltk_data()
if not _nltk_data_available:
    logging.error("Critical: NLTK data is not fully set up. Some functionalities may not work.")


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

# --- Slogan Generator Tool Logic ---
# Global model instance to avoid re-initializing on every call
_slogan_generator_model = None

def generate_slogans(keywords, num_slogans=5, target_language="English"): # target_language parameter add kiya
    """Generates slogans using the Gemini model."""
    global _slogan_generator_model # Use the global model instance

    if not GEMINI_API_AVAILABLE:
        logging.error(missing_api_key_error_msg("slogan_generator_tool"))
        return [missing_api_key_error_msg("slogan_generator_tool")]
    
    # Check NLTK data status, though for slogan generation, NLTK isn't strictly necessary for the AI part.
    if not _nltk_data_available: # Use the global status flag
        logging.warning("NLTK data setup issue detected, but slogan generation might still proceed.")

    try:
        if not _slogan_generator_model:
            _slogan_generator_model = get_gemini_model()
        
        if not _slogan_generator_model:
            return ["Error: Gemini model could not be loaded for slogan generation."]

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
            f"Generate {num_slogans} unique, catchy, and memorable advertising slogans in {target_language} " # prompt mein target_language use kiya
            f"for a brand or campaign related to '{keywords}'. "
            f"Each slogan should be concise and highly impactful. Do not use any markdown formatting like **bold**, *italic*, or ##headings. "
            f"Provide the output as a JSON array of objects, where each object has a key 'slogan' and its value is the slogan. Example: [{{'slogan': 'Think Different'}}, {{'slogan': 'Just Do It'}}].\n\n"
        )
        response = _slogan_generator_model.generate_content(
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
                return [f"Gemini could not generate any slogans in {target_language}. Please try different keywords."] # localized message
            
            return unique_slogans[:num_slogans]
        else:
            return [f"Gemini could not generate any slogans in {target_language}. Please try different keywords."] # localized message

    except Exception as e:
        logging.error(f"Error generating slogans with Gemini: {type(e).__name__}: {e}", exc_info=True) # Enhanced error logging
        return [f"Error: Slogan generation failed with Gemini. Details: {str(e)}"]