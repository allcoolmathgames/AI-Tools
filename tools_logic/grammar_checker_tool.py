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
        logging.info("Google Generative AI library loaded and configured for grammar_checker_tool.")
        GEMINI_API_AVAILABLE = True
    else:
        logging.warning("GOOGLE_API_KEY environment variable not set. Gemini functions will not work in grammar_checker_tool.")
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in grammar_checker_tool.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for grammar_checker_tool: {e}. Gemini functions might not work.")
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

# --- Grammar Checker Tool Logic ---
# Global model instance to avoid re-initializing on every call
_grammar_checker_model = None

def check_grammar(text, target_language="English"): # target_language parameter add kiya
    """Checks grammar and suggests style improvements using the Gemini model."""
    global _grammar_checker_model # Use the global model instance

    if not GEMINI_API_AVAILABLE:
        logging.error(missing_api_key_error_msg("grammar_checker_tool"))
        return missing_api_key_error_msg("grammar_checker_tool")
    
    # Check NLTK data status, though for grammar checking, NLTK isn't strictly necessary for the AI part.
    if not _nltk_data_available: # Use the global status flag
        logging.warning("NLTK data setup issue detected, but grammar check might still proceed.")

    try:
        if not _grammar_checker_model:
            _grammar_checker_model = get_gemini_model()
        
        if not _grammar_checker_model:
            return "Error: Gemini model could not be loaded for grammar check."
        
        prompt = (
            f"Review the following text in {target_language} for grammar, spelling, punctuation, and style. " # prompt mein target_language use kiya
            f"Provide a list of specific corrections and suggestions for improvement. "
            f"Format the output as a clear list of identified issues and their proposed corrections/improvements. "
            f"Do not use any markdown formatting like **bold**, *italic*, or ##headings. Present the text as plain paragraphs or bullet points if necessary.\n\n"
            f"Text to check:\n---\n{text}\n---\n\nCorrections and Suggestions:"
        )
        
        response = _grammar_checker_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                top_p=0.7,
                top_k=20,
                candidate_count=1,
            )
        )
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            corrections = response.candidates[0].content.parts[0].text.strip()
            # Remove leading "Corrections and Suggestions:" if present
            corrections = re.sub(r'^(Corrections and Suggestions:)?\s*', '', corrections, flags=re.IGNORECASE).strip()
            return corrections
        else:
            return "Gemini could not generate grammar corrections or suggestions. The text might be perfect, or try different input."

    except Exception as e:
        logging.error(f"Error checking grammar with Gemini: {type(e).__name__}: {e}", exc_info=True) # Enhanced error logging
        return f"Error: Grammar check failed with Gemini. Details: {str(e)}"