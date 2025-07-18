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
    logging.info("Google Generative AI library loaded and configured for email_tools.")
    GEMINI_API_AVAILABLE = True
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in email_tools.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for email_tools: {e}. Gemini functions might not work.")
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

# ==============================================================================
# Email Tools Logic
# ==============================================================================

def generate_email(subject, purpose, recipient=''):
    """Gemini model ka istemal karte hue email content generate karta hai."""
    if not GEMINI_API_AVAILABLE:
        logging.error("Gemini API email generation ke liye available nahi. 'google-generativeai' install karein aur API key configure karein.")
        return f"Error: Gemini API email generation ke liye configure nahi. 'google-generativeai' install karein aur apni API key set karein."

    try:
        model = get_gemini_model()
        
        email_prompt = (
            f"Aik professional email generate karein.\n"
            f"Subject: {subject}\n"
            f"Purpose: {purpose}\n"
        )
        if recipient:
            email_prompt += f"Recipient: {recipient}\n"
        email_prompt += "\nEmail ko munasib tareeqe se format karein, 'Dear [Recipient Name or Team],' se shuru karein aur aik professional closing ke sath khatam karein."

        response = model.generate_content(
            email_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
                top_p=0.8,
                top_k=30,
                candidate_count=1,
            )
        )
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            generated_email = response.candidates[0].content.parts[0].text.strip()
            return generated_email
        else:
            return "Gemini se koi email content generate nahi ho saka. Dusri tafseelat try karein."

    except Exception as e:
        logging.error(f"Gemini se email generate karne mein error: {e}", exc_info=True)
        return f"Error: Email generation Gemini se fail ho gai. Tafseelat: {str(e)}"

def generate_email_subjects(content, tone):
    """Gemini model ka istemal karte hue email subjects generate karta hai."""
    if not GEMINI_API_AVAILABLE:
        logging.error("Gemini API email subject generation ke liye available nahi. 'google-generativeai' install karein aur API key configure karein.")
        return ["Error: Gemini API email subject generation ke liye configure nahi."]
    try:
        model = get_gemini_model()
        response_schema = {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "subject": {"type": "STRING"}
                }
            }
        }
        prompt = (
            f"'{content}' ke mutaliq email ke liye 3-5 catchy aur effective email subject lines generate karein. "
            f"Tone '{tone}' hona chahiye. Open rates barhane par focus karein.\n\n"
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
            subjects_data = json.loads(json_string)
            subjects_list = [item["subject"].strip() for item in subjects_data if "subject" in item]
            return subjects_list if subjects_list else ["Koi email subjects generate nahi ho sakay."]
        else:
            return ["Koi email subjects generate nahi ho sakay."]
    except Exception as e:
        logging.error(f"Gemini se email subjects generate karne mein error: {e}", exc_info=True)
        return [f"Error: Email subject generation fail ho gai. Tafseelat: {str(e)}"]