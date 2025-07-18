import logging
import re
import os
import nltk # For NLTK data setup
import json # For JSON parsing

# --- Gemini API Configuration ---
# IMPORTANT: It is necessary to install the google-generativeai library.
# 'pip install google-generativeai' run karein.
try:
    import google.generativeai as genai
    # Your Gemini API key is configured here.
    # This key is crucial for using the Gemini model.
    # User-provided API key: AIzaSyBnLc4iJy4KFR5iA1Cwy6c207wAyMfwHn0
    genai.configure(api_key="AIzaSyBnLc4iJy4KFR5iA1Cwy6c207wAyMfwHn0")
    logging.info("Google Generative AI library loaded and configured for trending_news_generator_tool.")
    GEMINI_API_AVAILABLE = True
except ImportError:
    logging.warning("Google Generative AI library not found. Gemini functions will not work in trending_news_generator_tool.")
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logging.error(f"Error configuring Gemini API for trending_news_generator_tool: {e}. Gemini functions might not work.")
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
        raise Exception("Gemini API is not available.")
    
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

# --- Trending News Generator Tool Logic ---
def generate_trending_news(keywords, category, num_articles):
    """Generates trending news summaries using the Gemini model."""
    if not GEMINI_API_AVAILABLE:
        logging.error("Gemini API is not available for trending news generation. Please install 'google-generativeai' and configure API key.")
        return "Error: Gemini API not configured for trending news generation. Please install 'google-generativeai' and set your API key."

    try:
        model = get_gemini_model()
        
        prompt = (
            f"Provide a concise summary of {num_articles} trending news articles in English. " # Explicitly request English
        )
        if keywords:
            prompt += f"Focus on topics related to '{keywords}'. "
        if category:
            prompt += f"From the category '{category}'. "
        prompt += f"Ensure the news is diverse, sounds realistic, and each article has a headline and a brief summary. "
        prompt += "Do not use any markdown formatting like **bold**, *italic*, or ##headings. Provide plain text." # Add formatting instruction
        
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
            news_summary = response.candidates[0].content.parts[0].text.strip()
            return news_summary
        else:
            return "Gemini could not generate trending news summary. Please try different keywords."

    except Exception as e:
        logging.error(f"Error generating trending news summary with Gemini: {e}", exc_info=True)
        return f"Error: Trending news summary generation failed with Gemini. Details: {str(e)}"