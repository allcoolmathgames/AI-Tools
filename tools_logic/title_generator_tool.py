import logging
import re
import os
import nltk # NLTK data setup ke liye
import json # JSON parsing ke liye

# --- Gemini API Configuration ---
# IMPORTANT: google-generativeai library install karna zaroori hai.
# 'pip install google-generativeai' run karein.
try:
    import google.generativeai as genai
    # Aapki Gemini API key yahan configure ki gai hai.
    # Yeh key Gemini model ko istemal karne ke liye zaroori hai.
    # User ne di hui API key: AIzaSyBnLc4iJy4KFR5iA1Cwy6c207wAyMfwHn0
    genai.configure(api_key="AIzaSyBnLc4iJy4KFR5iA1Cwy6c207wAyMfwHn0")
    logging.info("Google Generative AI library loaded and configured for title_generator_tool.")
    GEMINI_API_AVAILABLE = True
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in title_generator_tool.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for title_generator_tool: {e}. Gemini functions might not work.")
    GEMINI_API_AVAILABLE = False

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- NLTK Data Path Setup ---
nltk_data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'nltk_data')
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)
    logging.info(f"Created NLTK data directory: {nltk_data_dir}")
nltk.data.path.append(nltk_data_dir)
logging.info(f"NLTK data path added: {nltk_data_dir}")

# --- NLTK Data Download Check ---
def ensure_nltk_data():
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
        # gemini-2.0-flash ko prefer karein kyunki yeh efficient hai
        if 'gemini-2.0-flash' in model_info.name:
            selected_model_name = model_info.name
            break
    
    if not selected_model_name:
        if available_models:
            # Agar flash model na mile to koi bhi available model use karein
            selected_model_name = available_models[0].name
            logging.warning(f"gemini-2.0-flash not found. Using available model: {selected_model_name}")
        else:
            raise Exception("No Gemini model found that supports content generation.")
    
    return genai.GenerativeModel(selected_model_name)

# --- Title Generator Tool Logic ---
def generate_titles(topic):
    """Gemini model ka istemal karte hue compelling titles generate karta hai."""
    if not GEMINI_API_AVAILABLE:
        logging.error("Gemini API title generation ke liye available nahi. 'google-generativeai' install karein aur API key configure karein.")
        return ["Error: Gemini API title generation ke liye configure nahi."]
    try:
        model = get_gemini_model()
        response_schema = {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING"}
                }
            }
        }
        prompt = (
            f"'{topic}' ke mutaliq content ke liye 5-7 catchy, SEO-friendly, aur compelling titles generate karein. "
            f"Aise titles par focus karein jo clicks hasil karein aur audience ko engage karein.\n\n"
        )
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.7,
                top_p=0.8,
                top_k=30,
                candidate_count=1,
            )
        )
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            json_string = response.candidates[0].content.parts[0].text
            titles_data = json.loads(json_string)
            titles_list = [item["title"].strip() for item in titles_data if "title" in item]
            return titles_list if titles_list else ["Koi titles generate nahi ho sakay."]
        else:
            return ["Koi titles generate nahi ho sakay."]
    except Exception as e:
        logging.error(f"Gemini se titles generate karne mein error: {e}", exc_info=True)
        return [f"Error: Title generation fail ho gai. Tafseelat: {str(e)}"]