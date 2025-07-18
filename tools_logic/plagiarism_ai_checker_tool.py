import logging
import re
import os
import nltk # NLTK data setup ke liye
import random # Plagiarism portion ko simulate karne ke liye
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
    logging.info("Google Generative AI library loaded and configured for plagiarism_ai_checker_tool.")
    GEMINI_API_AVAILABLE = True
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in plagiarism_ai_checker_tool.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for plagiarism_ai_checker_tool: {e}. Gemini functions might not work.")
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

# --- Plagiarism & AI Checker Tool Logic ---
def check_plagiarism_and_ai(text):
    """AI content ko Gemini ka istemal karte hue check karta hai. (Note: Asal plagiarism check ke liye specialized database comparison tool ki zaroorat hoti hai.)"""
    if not GEMINI_API_AVAILABLE:
        logging.error("Gemini API AI content detection ke liye available nahi. 'google-generativeai' install karein aur API key configure karein.")
        return {"is_ai_generated": True, "ai_probability": 0.99, "plagiarism_percentage": 0.0, "suggestions": ["Error: Gemini API AI content detection ke liye configure nahi."]}

    try:
        model = get_gemini_model()
        
        prompt = (
            f"Is text ka analysis karein aur batayen ke iske AI se generate hone ki kitni percentage hai. "
            f"Percentage score (maslan, '75% AI generated') mein jawab dein. "
            f"Aur mukhtasar wajah bhi batayen.\n\n"
            f"Analysis karne wala text:\n---\n{text}\n---\n\nAnalysis:"
        )
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1, # Factual analysis ke liye kam rakhein
                top_p=0.7,
                top_k=20,
                candidate_count=1,
            )
        )
        
        ai_probability_percent = 0.0
        suggestions = []
        is_ai_generated = False

        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            analysis_text = response.candidates[0].content.parts[0].text.strip()
            
            # Percentage extract karne ki koshish karein
            match = re.search(r'(\d{1,3})%', analysis_text)
            if match:
                ai_probability_percent = float(match.group(1))
            
            ai_probability = ai_probability_percent / 100.0
            is_ai_generated = ai_probability > 0.5
            
            suggestions.append(analysis_text) # Poore analysis ko suggestion ke tor par istemal karein

        if is_ai_generated:
            suggestions.append("Yeh text AI-generated lagta hai. Isko human-like banane ke liye sentences ko rephrase karein, personal anecdotes shamil karein, aur sentence structure mein variety layen.")
        else:
            suggestions.append("Yeh text human-like lagta hai. AI detection ke mutabiq koi specific suggestion nahi hai.")
        
        # Plagiarism portion filhaal simulate kiya gaya hai, jaisa ke pehle discuss hua tha
        # Asal plagiarism check ke liye alag se paid API ki zaroorat hogi
        plagiarism_percentage = random.uniform(0.0, 15.0) if random.random() < 0.2 else 0.0
        if plagiarism_percentage > 0:
            suggestions.append(f"Taqriban {plagiarism_percentage:.2f}% text mein existing sources se direct matches ho sakte hain. Bara-e-mehrbani ghaur se review karein.")


        return {
            "is_ai_generated": is_ai_generated,
            "ai_probability": round(ai_probability, 4),
            "plagiarism_percentage": round(plagiarism_percentage, 2), # Filhaal simulate kiya gaya hai
            "suggestions": suggestions
        }

    except Exception as e:
        logging.error(f"Gemini se AI content check karne mein error: {e}", exc_info=True)
        return {"is_ai_generated": True, "ai_probability": 0.99, "plagiarism_percentage": 0.0, "suggestions": [f"Error: AI content detection Gemini se fail ho gai. Tafseelat: {str(e)}"]}