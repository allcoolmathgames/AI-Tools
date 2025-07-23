import os
import re
import logging
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
        logging.info("Google Generative AI library loaded and configured for abstract_generator_tool.")
        GEMINI_API_AVAILABLE = True
    else:
        logging.warning("GOOGLE_API_KEY environment variable not set. Gemini functions will not work in abstract_generator_tool.")
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in abstract_generator_tool.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for abstract_generator_tool: {e}. Gemini functions might not work.")
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

# --- Abstract Generator Tool Logic ---
# Global model instance to avoid re-initializing on every call
_abstract_generator_model = None

def generate_abstract(text):
    """Generates a concise and professional abstract in English for the given text using the Gemini model."""
    global _abstract_generator_model # Use the global model instance

    if not GEMINI_API_AVAILABLE:
        logging.error(missing_api_key_error_msg("abstract_generator_tool"))
        return missing_api_key_error_msg("abstract_generator_tool")
    
    # Check NLTK data status, though for abstract generation, NLTK isn't strictly necessary for the AI part.
    if not _nltk_data_available: # Use the global status flag
        logging.warning("NLTK data setup issue detected, but abstract generation might still proceed.")

    try:
        if not _abstract_generator_model:
            _abstract_generator_model = get_gemini_model()
        
        if not _abstract_generator_model:
            return "Error: Gemini model could not be loaded for abstract generation."

        prompt = (
            f"Generate a concise and professional abstract in English for the following document or text. "
            f"The abstract should summarize the main objectives, methods, results, and conclusions. "
            f"Do not use any markdown formatting like **bold**, *italic*, or ##headings. Provide plain text.\n\n"
            f"Document/Text:\n---\n{text}\n---\n\nAbstract:"
        )
        response = _abstract_generator_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                top_p=0.8,
                top_k=30,
                candidate_count=1,
            )
        )
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            abstract_text = response.candidates[0].content.parts[0].text.strip()
            # Remove leading "Abstract:" if present
            abstract_text = re.sub(r'^(Abstract:)?\s*', '', abstract_text, flags=re.IGNORECASE).strip()
            return abstract_text
        else:
            return "Gemini could not generate an abstract. Please try different details."
    except Exception as e:
        error_message = f"An error occurred while generating abstract with Gemini: {e}"
        logging.error(error_message, exc_info=True)
        return f"Error: {error_message}"

if __name__ == '__main__':
    # Example Usage:
    # Set your GOOGLE_API_KEY environment variable before running this directly
    # os.environ["GOOGLE_API_KEY"] = "YOUR_GEMINI_API_KEY"

    sample_text = """
    This research paper investigates the impact of climate change on coastal ecosystems, specifically focusing on coral reefs in the Indo-Pacific region. We employed a multi-faceted approach combining satellite imagery analysis, in-situ temperature monitoring, and biodiversity surveys conducted over a period of ten years. Our findings indicate a significant correlation between rising ocean temperatures and increased coral bleaching events, leading to a measurable decline in reef biodiversity. We also observed changes in fish populations and migration patterns, suggesting broader ecological disruptions. The study highlights the urgent need for global climate action and localized conservation efforts to mitigate these impacts. Future research should explore the resilience mechanisms of certain coral species and the potential for assisted migration strategies.
    """
    
    generated_abstract = generate_abstract(sample_text)
    print("--- Generated Abstract ---")
    print(generated_abstract)
    print("--------------------------")

    # Example with missing API key
    original_api_key = os.getenv("GOOGLE_API_KEY")
    if original_api_key:
        del os.environ["GOOGLE_API_KEY"] # Temporarily unset for test
    
    generated_abstract_no_key = generate_abstract(sample_text)
    print("\n--- Generated Abstract (No API Key) ---")
    print(generated_abstract_no_key)
    print("---------------------------------------")

    if original_api_key:
        os.environ["GOOGLE_API_KEY"] = original_api_key # Restore API key