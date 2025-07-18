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
    logging.info("Google Generative AI library loaded and configured for summarizer_tool.")
    GEMINI_API_AVAILABLE = True
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in summarizer_tool.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for summarizer_tool: {e}. Gemini functions might not work.")
    GEMINI_API_AVAILABLE = False

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- NLTK Data Path Setup (Zaroori agar NLTK use ho) ---
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

# --- Summarizer Tool Logic ---
def summarize_text(text, length_ratio=0.5):
    """Diye gaye text ko Gemini model ka istemal karte hue summarize karta hai."""
    if not GEMINI_API_AVAILABLE:
        logging.error("Gemini API summarization ke liye available nahi. 'google-generativeai' install karein aur API key configure karein.")
        return f"Error: Gemini API summarization ke liye configure nahi. 'google-generativeai' install karein aur apni API key set karein."

    try:
        # length_ratio ko float mein convert karein
        length_ratio = float(length_ratio) 

        model = get_gemini_model()
        
        input_length = len(text.split())
        min_summary_words = max(20, int(input_length * (length_ratio - 0.2)))
        max_summary_words = max(min_summary_words + 10, int(input_length * length_ratio))

        prompt = (
            f"Please summarize the following text concisely. The summary should be between "
            f"{min_summary_words} and {max_summary_words} words, maintaining the core information. "
            f"Do not add any new information or elaborate excessively. Focus solely on extracting key points from the provided text.\n\n" # Ye line add ki gai hai
            f"Original text:\n---\n{text}\n---\n\nSummary:"
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=30,
                candidate_count=1,
            )
        )
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            summary_text = response.candidates[0].content.parts[0].text.strip()
            # "Summary:" jaisi shuruati lines ko hata dein
            summary_text = re.sub(r'^(Summary:)?\s*', '', summary_text, flags=re.IGNORECASE).strip()
            return summary_text
        else:
            return "Gemini se koi summary generate nahi ho saki. Dusra input try karein."

    except Exception as e:
        logging.error(f"Gemini se text summarize karne mein error: {e}", exc_info=True)
        return f"Error: Summarization Gemini se fail ho gai. Tafseelat: {str(e)}"