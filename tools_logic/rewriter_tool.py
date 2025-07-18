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
    logging.info("Google Generative AI library loaded and configured for rewriter_tool.")
    GEMINI_API_AVAILABLE = True
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in rewriter_tool.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for rewriter_tool: {e}. Gemini functions might not work.")
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

# --- Article Rewriter Tool Logic ---
def rewrite_article(text, creativity=0.5):
    """Diye gaye text ko Gemini model ka istemal karte hue rewrite karta hai."""
    if not GEMINI_API_AVAILABLE:
        logging.error("Gemini API rewriting ke liye available nahi. 'google-generativeai' install karein aur API key configure karein.")
        return f"Error: Gemini API rewriting ke liye configure nahi. 'google-generativeai' install karein aur apni API key set karein."

    try:
        model = get_gemini_model()
        
        prompt = (
            f"Rewrite the following text to make it unique and engaging. "
            f"Adjust the tone and style with a creativity level of {int(creativity*100)}%. "
            f"Maintain the original meaning but rephrase sentences and vocabulary significantly.\n\n"
            f"Original text:\n---\n{text}\n---\n\nRewritten text:"
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.5 + (creativity * 0.5), # Creativity level ke hisab se temperature adjust karein
                top_p=0.9,
                top_k=40,
                candidate_count=1,
            )
        )
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            rewritten_text = response.candidates[0].content.parts[0].text.strip()
            rewritten_text = re.sub(r'^(Rewritten text:)?\s*', '', rewritten_text, flags=re.IGNORECASE).strip()
            return rewritten_text
        else:
            return "Gemini se koi rewritten text generate nahi ho saka. Dusra input try karein."

    except Exception as e:
        logging.error(f"Gemini se text rewrite karne mein error: {e}", exc_info=True)
        return f"Error: Rewriting Gemini se fail ho gai. Tafseelat: {str(e)}"

# --- Paraphrasing Tool Logic ---
def paraphrase_text(text):
    """Diye gaye text ko rewrite_article function ka istemal karte hue paraphrase karta hai."""
    # Paraphrasing ke liye rewrite_article function ko default creativity ke sath call karein
    return rewrite_article(text, creativity=0.7)