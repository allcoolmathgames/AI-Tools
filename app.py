import os
import logging
from flask import Flask, request, jsonify, render_template, redirect, abort
from flask_cors import CORS
from langdetect import detect, LangDetectException # Ensure langdetect is installed (pip install langdetect)

# Import specific functions from the new modular tool files
# Ensure these files exist in your 'tools_logic' folder.
# NOTE: The 'NLTK data check failed' error in logs indicates an issue within these imported tool_logic files
#       where nltk.info is being used. This needs to be fixed inside those individual tool files.
from tools_logic.summarizer_tool import summarize_text
from tools_logic.rewriter_tool import rewrite_article, paraphrase_text
from tools_logic.plagiarism_ai_checker_tool import check_plagiarism_and_ai
from tools_logic.content_idea_generator_tool import generate_content_ideas
from tools_logic.slogan_generator_tool import generate_slogans
from tools_logic.humanizer_tool import humanize_text
from tools_logic.email_tools import generate_email, generate_email_subjects
from tools_logic.grammar_checker_tool import check_grammar
from tools_logic.story_generator_tool import generate_story
from tools_logic.product_description_generator_tool import generate_product_description
from tools_logic.essay_generator_tool import generate_essay
from tools_logic.trending_news_generator_tool import generate_trending_news
from tools_logic.acronym_generator_tool import generate_acronym
from tools_logic.abstract_generator_tool import generate_abstract
from tools_logic.adjective_generator_tool import generate_adjectives
from tools_logic.hook_generator_tool import generate_hooks
from tools_logic.title_generator_tool import generate_titles
from tools_logic.conclusion_generator_tool import generate_conclusion
from tools_logic.business_name_generator_tool import generate_business_names


# Configure logging for the application
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the Flask application
app = Flask(__name__, static_folder='static', template_folder='templates')
# Enable Cross-Origin Resource Sharing (CORS) for all routes
CORS(app)

# ==============================================================================
# HTML Page Routes: Define routes for serving HTML templates to the user
# All routes are modified to accept an optional language code prefix
# ==============================================================================

SUPPORTED_LANGUAGES = ["en", "es", "id", "pt", "fr", "nl", "it", "de", "ru", "ar", "vi"] # 'br' changed to 'pt' for consistency


# Mapping of tool URLs to their template paths
TOOL_TEMPLATE_MAP = {
    'summarizer': 'summarizer/index.html',
    'article-rewriter': 'article_rewriter/index.html',
    'plagiarism-checker': 'plagiarism_checker/index.html',
    'paraphrasing-tool': 'paraphrasing_tool/index.html',
    'content-idea-generator': 'content_idea_generator/index.html',
    'slogan-generator': 'slogan_generator/index.html',
    'ai-text-to-humanize': 'ai_text_to_humanize/index.html',
    'ai-email-generator': 'ai_email_generator/index.html',
    'grammar-checker': 'grammar_checker/index.html',
    'ai-story-generator': 'ai_story_generator/index.html',
    'ai-product-description-generator': 'ai_product_description_generator/index.html',
    'essay-generator': 'essay_generator/index.html',
    'trending-news-generator': 'trending_news_generator/index.html',
    'acronym-generator': 'acronym_generator/index.html',
    'abstract-generator': 'abstract_generator/index.html',
    'adjective-generator': 'adjective_generator/index.html',
    'hook-generator': 'hook_generator/index.html',
    'title-generator': 'title_generator/index.html',
    'conclusion-generator': 'conclusion_generator/index.html',
    'business-name-generator': 'business_name_generator/index.html',
    'email-subject-line-generator': 'email_subject_line_generator/index.html',
    'tools': 'tools/index.html' # Explicitly added for the All Tools page
}

# Mapping of language codes to full names for display/detection
LANGUAGE_CODE_TO_NAME = {
    "en": "English",
    "es": "Spanish",
    "id": "Indonesian",
    "pt": "Portuguese", # 'br' is typically for Portuguese (Brazil), 'pt' for general Portuguese
    "fr": "French",
    "nl": "Dutch",
    "it": "Italian",
    "de": "German",
    "ru": "Russian",
    "ar": "Arabic",
    "vi": "Vietnamese",
    "ur": "Urdu", # Example additional language
    "zh-cn": "Chinese (Simplified)", # Example additional language
    "ja": "Japanese",
    "ko": "Korean", # Example additional language
    # Add more mappings as needed
}

def get_request_language(text_to_detect):
    """Detects the language of the given text, returns full language name, defaults to English if detection fails."""
    if not text_to_detect or len(text_to_detect.strip()) < 20: # Ensure stripping whitespace and sufficient length for detection
        logging.info("Text too short or empty for reliable language detection, defaulting to English.")
        return "English"
    try:
        detected_code = detect(text_to_detect)
        # Return full language name if mapped, otherwise return the code or default to English
        full_language_name = LANGUAGE_CODE_TO_NAME.get(detected_code, detected_code)
        logging.info(f"Detected language code: {detected_code}, Full language name: {full_language_name}")
        return full_language_name
    except LangDetectException as e:
        logging.warning(f"Could not detect language for text: {e}. Defaulting to English.")
        return "English"
    except Exception as e:
        logging.error(f"An unexpected error occurred during language detection: {e}. Defaulting to English.")
        return "English"


# Consolidated route decorator for all HTML pages
# This decorator adds two routes for each view function: one with a language prefix and one without.
def route_with_language(path):
    def decorator(f):
        # Register the route with a language code prefix
        app.add_url_rule(f'/<lang_code>{path}', endpoint=f.__name__, view_func=f)
        # Register the route without a language code prefix (for default language)
        app.add_url_rule(path, endpoint=f.__name__, view_func=f)
        return f # Return the original function
    return decorator

# Apply the consolidated decorator to all page routes
@route_with_language('/')
def index(lang_code=None):
    """Renders the main index page (AI Summarizer tool)."""
    return render_template('summarizer/index.html')

@route_with_language('/summarizer')
def summarizer_page(lang_code=None):
    """Renders the AI Summarizer tool page."""
    return render_template('summarizer/index.html')

@route_with_language('/article-rewriter')
def article_rewriter_page(lang_code=None):
    """Renders the Article Rewriter tool page."""
    return render_template('article_rewriter/index.html')

@route_with_language('/plagiarism-checker')
def plagiarism_checker_page(lang_code=None):
    """Renders the Plagiarism Checker tool page."""
    return render_template('plagiarism_checker/index.html')

@route_with_language('/paraphrasing-tool')
def paraphrasing_tool_page(lang_code=None):
    """Renders the Paraphrasing Tool page."""
    return render_template('paraphrasing_tool/index.html')

@route_with_language('/content-idea-generator')
def content_idea_generator_page(lang_code=None):
    """Renders the Content Idea Generator tool page."""
    return render_template('content_idea_generator/index.html')

@route_with_language('/slogan-generator')
def slogan_generator_page(lang_code=None):
    """Renders the Slogan Generator tool page."""
    return render_template('slogan_generator/index.html')

@route_with_language('/ai-text-to-humanize')
def ai_humanizer_page(lang_code=None):
    """Renders the AI Text Humanizer tool page."""
    return render_template('ai_text_to_humanize/index.html')

@route_with_language('/ai-email-generator')
def ai_email_generator_page(lang_code=None):
    """Renders the AI Email Generator tool page."""
    return render_template('ai_email_generator/index.html')

@route_with_language('/grammar-checker')
def grammar_checker_page(lang_code=None):
    """Renders the Grammar Checker tool page."""
    return render_template('grammar_checker/index.html')

@route_with_language('/ai-story-generator')
def ai_story_generator_page(lang_code=None):
    """Renders the AI Story Generator tool page."""
    return render_template('ai_story_generator/index.html')

@route_with_language('/ai-product-description-generator')
def ai_product_description_generator_page(lang_code=None):
    """Renders the AI Product Description Generator tool page."""
    return render_template('ai_product_description_generator/index.html')

@route_with_language('/essay-generator')
def essay_generator_page(lang_code=None):
    """Renders the Essay Generator tool page."""
    return render_template('essay_generator/index.html')

@route_with_language('/trending-news-generator')
def trending_news_generator_page(lang_code=None):
    """Renders the Trending News Generator tool page."""
    return render_template('trending_news_generator/index.html')

@route_with_language('/acronym-generator')
def acronym_generator_page(lang_code=None):
    """Renders the Acronym Generator tool page."""
    return render_template('acronym_generator/index.html')

@route_with_language('/abstract-generator')
def abstract_generator_page(lang_code=None):
    """Renders the Abstract Generator tool page."""
    return render_template('abstract_generator/index.html')

@route_with_language('/adjective-generator')
def adjective_generator_page(lang_code=None):
    """Renders the Adjective Generator tool page."""
    return render_template('adjective_generator/index.html')

@route_with_language('/hook-generator')
def hook_generator_page(lang_code=None):
    """Renders the Hook Generator tool page."""
    return render_template('hook_generator/index.html')

@route_with_language('/title-generator')
def title_generator_page(lang_code=None):
    """Renders the Title Generator tool page."""
    return render_template('title_generator/index.html')

@route_with_language('/conclusion-generator')
def conclusion_generator_page(lang_code=None):
    """Renders the Conclusion Generator tool page."""
    return render_template('conclusion_generator/index.html')

@route_with_language('/business-name-generator')
def business_name_generator_page(lang_code=None):
    """Renders the Business Name Generator tool page."""
    return render_template('business_name_generator/index.html')

@route_with_language('/email-subject-line-generator')
def email_subject_line_generator_page(lang_code=None):
    """Renders the Email Subject Line Generator tool page."""
    return render_template('email_subject_line_generator/index.html')

# --- Static Pages Routes ---
@route_with_language('/about-us')
def about_us_page(lang_code=None):
    """Renders the About Us page."""
    return render_template('pages/about_us.html')

@route_with_language('/contact')
def contact_page(lang_code=None):
    """Renders the Contact Us page."""
    return render_template('pages/contact.html')

@route_with_language('/privacy-policy')
def privacy_policy_page(lang_code=None):
    """Renders the Privacy Policy page."""
    return render_template('pages/privacy_policy.html')

@route_with_language('/terms-conditions')
def terms_conditions_page(lang_code=None):
    """Renders the Terms & Conditions page."""
    return render_template('pages/terms_conditions.html')

@route_with_language('/tools/')
def tools_index(lang_code=None):
    """Renders the main tools listing page."""
    return render_template('tools/index.html')
# --- End Static Pages Routes ---

# --- Blog Routes ---
@route_with_language('/blogs/')
def blogs_index(lang_code=None):
    """Renders the main blog listing page."""
    return render_template('blogs/index.html')

# Individual blog post routes also need to handle optional language code
@route_with_language('/blogs/<string:slug>.html')
def blog_post(slug, lang_code=None):
    """Renders individual blog post based on slug."""
    try:
        # Construct path dynamically, assuming blogs templates are inside a 'blogs' folder
        # and blog slug matches filename (e.g., 'how_to_write_better_summaries_with_ai.html')
        return render_template(f'blogs/{slug}.html')
    except Exception as e:
        logging.error(f"Error rendering blog post {slug}: {e}")
        return render_template('404.html'), 404 # Assuming you have a 404.html template
# --- End Blog Routes ---

# ==============================================================================
# API Endpoints: Define routes for handling API requests from the frontend
# ==============================================================================

@app.route('/api/summarize', methods=['POST'])
def summarize_api():
    """API endpoint for text summarization."""
    data = request.get_json()
    text = data.get('text', '')
    length_ratio_str = data.get('length', '0.5')

    try:
        length_ratio = float(length_ratio_str)
    except (ValueError, TypeError):
        logging.warning(f"Invalid length_ratio received: {length_ratio_str}. Defaulting to 0.5.")
        length_ratio = 0.5

    if not text:
        return jsonify({"summary": "", "error": "Please provide text to summarize."}), 400

    detected_language = get_request_language(text) # Language Detection

    try:
        # Assuming summarize_text accepts 'language' as a parameter
        summary = summarize_text(text, length_ratio, detected_language)
        if str(summary).startswith("Error:"):
            logging.error(f"Summarization API call failed: {summary}")
            return jsonify({"summary": "", "error": summary}), 500

        logging.info("Summarization successful.")
        return jsonify({"summary": str(summary).strip()})
    except Exception as e:
        error_message = f"An unexpected error occurred during summarization: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"summary": "", "error": error_message}), 500


@app.route('/api/rewrite', methods=['POST'])
def rewrite_api():
    """API endpoint for article rewriting."""
    logging.info("Received /api/rewrite POST request.")
    data = request.get_json()
    text = data.get('text', '')
    creativity = data.get('creativity', 0.5)

    detected_language = get_request_language(text) # Language Detection

    if not text:
        return jsonify({"rewritten_text": "", "error": "Please provide text to rewrite."}), 400

    try:
        # Assuming rewrite_article accepts 'language' as a parameter
        rewritten_text = rewrite_article(text, creativity, detected_language)
        if str(rewritten_text).startswith("Error:"):
            logging.error(f"Rewriting API call failed: {rewritten_text}")
            return jsonify({"rewritten_text": "", "error": rewritten_text}), 500

        logging.info("Rewriting successful.")
        return jsonify({"rewritten_text": str(rewritten_text).strip()})
    except Exception as e:
        error_message = f"An unexpected error occurred during rewriting: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"rewritten_text": "", "error": error_message}), 500


@app.route('/api/humanize', methods=['POST'])
def humanize_api():
    """API endpoint for humanizing AI-generated text."""
    logging.info("Received /api/humanize POST request.")
    data = request.get_json()
    text = data.get('text', '')
    creativity = data.get('creativity', 0.7)

    detected_language = get_request_language(text) # Language Detection

    if not text:
        return jsonify({"humanized_text": "", "error": "Please provide text to humanize."}), 400

    try:
        # Assuming humanize_text accepts 'language' as a parameter
        humanized_text = humanize_text(text, creativity, detected_language)
        if str(humanized_text).startswith("Error:"):
            logging.error(f"Humanization API call failed: {humanized_text}")
            return jsonify({"humanized_text": "", "error": humanized_text}), 500

        logging.info("Humanization successful.")
        return jsonify({"humanized_text": str(humanized_text).strip()})
    except Exception as e:
        error_message = f"An unexpected error occurred during humanization: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"humanized_text": "", "error": error_message}), 500


@app.route('/api/generate_email', methods=['POST'])
def generate_email_api():
    """API endpoint for generating email content."""
    logging.info("Received /api/generate_email POST request.")
    data = request.get_json()
    subject = data.get('subject', '')
    purpose = data.get('purpose', '')
    recipient = data.get('recipient', '')
    
    # Using 'subject' and 'purpose' for language detection
    text_for_detection = f"{subject} {purpose}".strip()
    detected_language = get_request_language(text_for_detection) # Language Detection

    if not subject and not purpose:
        return jsonify({"generated_email": "", "error": "Please provide either a subject or purpose for the email."}), 400

    try:
        # Assuming generate_email accepts 'language' as a parameter
        email_content = generate_email(subject, purpose, recipient, detected_language)
        if str(email_content).startswith("Error:"):
            logging.error(f"Email generation API call failed: {email_content}")
            return jsonify({"generated_email": "", "error": email_content}), 500

        logging.info("Email generation successful.")
        return jsonify({"generated_email": str(email_content).strip()})
    except Exception as e:
        error_message = f"An unexpected error occurred during email generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"generated_email": "", "error": error_message}), 500


@app.route('/api/generate_content_ideas', methods=['POST'])
def generate_content_ideas_api():
    """API endpoint for generating content ideas."""
    logging.info("Received /api/generate_content_ideas POST request.")
    data = request.get_json()
    keywords = data.get('keywords', '')

    detected_language = get_request_language(keywords) # Language Detection (using keywords)

    if not keywords:
        return jsonify({"content_ideas": [], "error": "Please provide keywords for content ideas."}), 400

    try:
        # Assuming generate_content_ideas accepts 'language' as a parameter
        content_ideas = generate_content_ideas(keywords, detected_language)
        if isinstance(content_ideas, str) and content_ideas.startswith("Error:"):
            logging.error(f"Content idea generation API call failed: {content_ideas}")
            return jsonify({"content_ideas": [], "error": content_ideas}), 500

        logging.info("Content idea generation successful.")
        if isinstance(content_ideas, str):
            return jsonify({"content_ideas": content_ideas.strip().split('\n')})
        return jsonify({"content_ideas": content_ideas})
    except Exception as e:
        error_message = f"An unexpected error occurred during content idea generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"content_ideas": [], "error": error_message}), 500


@app.route('/api/paraphrase', methods=['POST'])
def paraphrase_api():
    """API endpoint for paraphrasing text."""
    logging.info("Received /api/paraphrase POST request.")
    data = request.get_json()
    text = data.get('text', '')

    detected_language = get_request_language(text) # Language Detection

    if not text:
        return jsonify({"paraphrased_text": "", "error": "Please provide text to paraphrase."}), 400

    try:
        # Assuming paraphrase_text accepts 'language' as a parameter
        paraphrased_text = paraphrase_text(text, detected_language)
        if str(paraphrased_text).startswith("Error:"):
            logging.error(f"Paraphrasing API call failed: {paraphrased_text}")
            return jsonify({"paraphrased_text": "", "error": paraphrased_text}), 500

        logging.info("Paraphrasing successful.")
        return jsonify({"paraphrased_text": str(paraphrased_text).strip()})
    except Exception as e:
        error_message = f"An unexpected error occurred during paraphrasing: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"paraphrased_text": "", "error": error_message}), 500

@app.route('/api/check_grammar', methods=['POST'])
def check_grammar_api():
    """API endpoint for checking grammar."""
    logging.info("Received /api/check_grammar POST request.")
    data = request.get_json()
    text = data.get('text', '')

    detected_language = get_request_language(text) # Language Detection

    if not text:
        return jsonify({"corrected_text": "", "error": "Please provide text to check grammar."}), 400

    try:
        # Assuming check_grammar accepts 'language' as a parameter
        corrected_text = check_grammar(text, detected_language)
        if str(corrected_text).startswith("Error:"):
            logging.error(f"Grammar check API call failed: {corrected_text}")
            return jsonify({"corrected_text": "", "error": corrected_text}), 500

        logging.info("Grammar check successful.")
        return jsonify({"corrected_text": str(corrected_text).strip()})
    except Exception as e:
        error_message = f"An unexpected error occurred during grammar check: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"corrected_text": "", "error": error_message}), 500

@app.route('/api/generate_slogan', methods=['POST'])
def generate_slogan_api():
    """API endpoint for generating slogans."""
    logging.info("Received /api/generate_slogan POST request.")
    data = request.get_json()
    keywords = data.get('keywords', '')
    num_slogans = data.get('num_slogans', 5)

    detected_language = get_request_language(keywords) # Language Detection (using keywords)

    if not keywords:
        return jsonify({"slogans": [], "error": "Please provide keywords for slogan generation."}), 400

    try:
        num_slogans = int(num_slogans)
        num_slogans = max(1, min(num_slogans, 10))
    except (ValueError, TypeError):
        logging.warning(f"Invalid num_slogans received: {num_slogans}. Defaulting to 5.")
        num_slogans = 5

    try:
        # Assuming generate_slogans accepts 'language' as a parameter
        slogans = generate_slogans(keywords, num_slogans, detected_language)
        if isinstance(slogans, list) and slogans and str(slogans[0]).startswith("Error: Gemini API"):
            logging.error(f"Gemini slogan generation failed: {slogans[0]}")
            return jsonify({"slogans": [], "error": slogans[0]}), 500

        logging.info("Slogan generation successful.")
        return jsonify({"slogans": slogans})
    except Exception as e:
        error_message = f"An unexpected error occurred during slogan generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"slogans": [], "error": error_message}), 500


@app.route('/api/check_plagiarism_ai', methods=['POST'])
def check_plagiarism_ai_api():
    """API endpoint for checking plagiarism and AI content."""
    logging.info("Received /api/check_plagiarism_ai POST request.")
    data = request.get_json()
    text = data.get('text', '')

    detected_language = get_request_language(text) # Language Detection

    if not text:
        return jsonify({"error": "Please provide text to check."}), 400

    try:
        # Assuming check_plagiarism_and_ai accepts 'language' as a parameter
        results = check_plagiarism_and_ai(text, detected_language)
        logging.info("Plagiarism and AI check processed.")
        return jsonify(results)
    except Exception as e:
        error_message = f"An unexpected error occurred during plagiarism/AI check: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"error": error_message}), 500


@app.route('/api/generate_story', methods=['POST'])
def generate_story_api():
    """API endpoint for generating stories."""
    logging.info("Received /api/generate_story POST request.")
    data = request.get_json()
    topic = data.get('topic', '')
    genre = data.get('genre', '')
    characters = data.get('characters', '')

    # Use topic for language detection
    text_for_detection = topic
    detected_language = get_request_language(text_for_detection) # Language Detection

    if not topic:
        return jsonify({"story": "", "error": "Please provide a story topic or keywords."}), 400

    try:
        # Assuming generate_story accepts 'language' as a parameter
        story = generate_story(topic, genre, characters, detected_language)
        if str(story).startswith("Error:"):
            logging.error(f"Story generation API call failed: {story}")
            return jsonify({"story": "", "error": story}), 500

        logging.info("Story generation successful.")
        return jsonify({"story": str(story).strip()})
    except Exception as e:
        error_message = f"An unexpected error occurred during story generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"story": "", "error": error_message}), 500


@app.route('/api/generate_product_description', methods=['POST'])
def generate_product_description_api():
    """API endpoint for generating product descriptions."""
    logging.info("Received /api/generate_product_description POST request.")
    data = request.get_json()
    product_name = data.get('productName', '')
    product_keywords = data.get('keywords', '')
    target_audience = data.get('targetAudience', '')
    tone = data.get('tone', 'informative')

    # Use product_name or product_keywords for language detection
    text_for_detection = f"{product_name} {product_keywords}".strip()
    detected_language = get_request_language(text_for_detection) # Language Detection

    if not product_name and not product_keywords:
        return jsonify({"description": "", "error": "Please enter a product name or keywords to generate a description."}), 400

    try:
        # Assuming generate_product_description accepts 'language' as a parameter
        description = generate_product_description(product_name, product_keywords, target_audience, tone, detected_language)
        if str(description).startswith("Error:"):
            logging.error(f"Product description generation API call failed: {description}")
            return jsonify({"description": "", "error": description}), 500

        logging.info("Product description generation successful.")
        return jsonify({"description": str(description).strip()})
    except Exception as e:
        error_message = f"An unexpected error occurred during product description generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"description": "", "error": error_message}), 500

@app.route('/api/generate_essay', methods=['POST'])
def generate_essay_api():
    """API endpoint for generating essays."""
    logging.info("Received /api/generate_essay POST request.")
    data = request.get_json()
    topic = data.get('topic', '')
    length = data.get('length', 'medium')
    style = data.get('style', 'formal')
    keywords = data.get('keywords', '')

    # Use topic or keywords for language detection
    text_for_detection = f"{topic} {keywords}".strip()
    detected_language = get_request_language(text_for_detection) # Language Detection

    if not topic:
        return jsonify({"essay": "", "error": "Please provide a topic for the essay."}), 400

    try:
        # Assuming generate_essay accepts 'language' as a parameter
        essay = generate_essay(topic, length, style, keywords, detected_language)
        if str(essay).startswith("Error:"):
            logging.error(f"Essay generation API call failed: {essay}")
            return jsonify({"essay": "", "error": essay}), 500

        logging.info("Essay generation successful.")
        return jsonify({"essay": str(essay).strip()})
    except Exception as e:
        error_message = f"An unexpected error occurred during essay generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"essay": "", "error": error_message}), 500

@app.route('/api/generate_trending_news', methods=['POST'])
def generate_trending_news_api():
    logging.info("Received /api/generate_trending_news POST request.")
    data = request.get_json()
    keywords = data.get('keywords', '')
    category = data.get('category', '')
    num_articles = data.get('num_articles', 1)

    # Use keywords or category for language detection
    text_for_detection = f"{keywords} {category}".strip()
    detected_language = get_request_language(text_for_detection) # Language Detection

    if not keywords and not category:
        return jsonify({"news_summary": "", "error": "Please enter a news topic/keywords or select a category."}), 400

    try:
        num_articles = int(num_articles) if isinstance(num_articles, str) and num_articles.isdigit() else 1

        # Assuming generate_trending_news accepts 'language' as a parameter
        news_summary = generate_trending_news(keywords, category, num_articles, detected_language)
        if isinstance(news_summary, str) and str(news_summary).startswith("Error:"):
            logging.error(f"Trending news generation API call failed: {news_summary}")
            return jsonify({"news_summary": "", "error": news_summary}), 500

        logging.info("Trending news generation successful.")
        return jsonify({"news_summary": str(news_summary).strip()})
    except Exception as e:
        error_message = f"An unexpected error occurred during trending news generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"news_summary": "", "error": error_message}), 500

@app.route('/api/generate_acronym', methods=['POST'])
def generate_acronym_api():
    """API endpoint for generating acronyms."""
    logging.info("Received /api/generate_acronym POST request.")
    data = request.get_json()
    text = data.get('text', '')

    detected_language = get_request_language(text) # Language Detection

    if not text:
        return jsonify({"acronym": "", "error": "Please enter a phrase or text to generate an acronym."}), 400

    try:
        # Assuming generate_acronym accepts 'language' as a parameter
        acronym = generate_acronym(text, detected_language)
        if str(acronym).startswith("Error:"):
            logging.error(f"Acronym generation API call failed: {acronym}")
            return jsonify({"acronym": "", "error": acronym}), 500

        logging.info("Acronym generation successful.")
        return jsonify({"acronym": str(acronym).strip()})
    except Exception as e:
        error_message = f"An unexpected error occurred during acronym generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"acronym": "", "error": error_message}), 500

@app.route('/api/generate_abstract', methods=['POST'])
def generate_abstract_api():
    """API endpoint for generating abstracts."""
    logging.info("Received /api/generate_abstract POST request.")
    data = request.get_json()
    text = data.get('text', '')

    detected_language = get_request_language(text) # Language Detection

    if not text:
        return jsonify({"abstract": "", "error": "Please paste your main text to generate an abstract."}), 400

    try:
        # Assuming generate_abstract accepts 'language' as a parameter
        abstract = generate_abstract(text, detected_language)
        if str(abstract).startswith("Error:"):
            logging.error(f"Abstract generation API call failed: {abstract}")
            return jsonify({"abstract": "", "error": abstract}), 500

        logging.info("Abstract generation successful.")
        return jsonify({"abstract": str(abstract).strip()})
    except Exception as e:
        error_message = f"An unexpected error occurred during abstract generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"abstract": "", "error": error_message}), 500

@app.route('/api/generate_adjectives', methods=['POST'])
def generate_adjectives_api():
    logging.info("Received /api/generate_adjectives POST request.")
    data = request.get_json()
    text = data.get('text', '')

    detected_language = get_request_language(text) # Language Detection

    if not text:
        return jsonify({"adjectives": [], "error": "Please enter a noun or sentence to get adjectives."}), 400

    try:
        # Assuming generate_adjectives accepts 'language' as a parameter
        adjectives = generate_adjectives(text, detected_language)
        if isinstance(adjectives, list) and adjectives and str(adjectives[0]).startswith("Error:"):
            logging.error(f"Adjective generation API call failed: {adjectives[0]}")
            return jsonify({"adjectives": [], "error": adjectives[0]}), 500

        logging.info("Adjective generation successful.")
        return jsonify({"adjectives": adjectives})
    except Exception as e:
        error_message = f"An unexpected error occurred during adjective generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"adjectives": [], "error": error_message}), 500


@app.route('/api/generate_hooks', methods=['POST'])
def generate_hooks_api():
    logging.info("Received /api/generate_hooks POST request.")
    data = request.get_json()
    topic = data.get('topic', '')
    tone = data.get('tone', 'Intriguing')

    detected_language = get_request_language(topic) # Language Detection (using topic)

    if not topic:
        return jsonify({"hooks": [], "error": "Please describe your content topic to generate hooks."}), 400

    try:
        # Assuming generate_hooks accepts 'language' as a parameter
        hooks = generate_hooks(topic, tone, detected_language)
        if isinstance(hooks, list) and hooks and str(hooks[0]).startswith("Error:"):
            logging.error(f"Hook generation API call failed: {hooks[0]}")
            return jsonify({"hooks": [], "error": hooks[0]}), 500

        logging.info("Hook generation successful.")
        return jsonify({"hooks": hooks})
    except Exception as e:
        error_message = f"An unexpected error occurred during hook generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"hooks": [], "error": error_message}), 500


@app.route('/api/generate_titles', methods=['POST'])
def generate_titles_api():
    logging.info("Received /api/generate_titles POST request.")
    data = request.get_json()
    topic = data.get('topic', '')

    detected_language = get_request_language(topic) # Language Detection (using topic)

    if not topic:
        return jsonify({"titles": [], "error": "Please describe your content to generate titles."}), 400

    try:
        # Assuming generate_titles accepts 'language' as a parameter
        titles = generate_titles(topic, detected_language)
        if isinstance(titles, list) and titles and str(titles[0]).startswith("Error:"):
            logging.error(f"Title generation API call failed: {titles[0]}")
            return jsonify({"titles": [], "error": titles[0]}), 500

        logging.info("Title generation successful.")
        return jsonify({"titles": titles})
    except Exception as e:
        error_message = f"An unexpected error occurred during title generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"titles": [], "error": error_message}), 500


@app.route('/api/generate_conclusion', methods=['POST'])
def generate_conclusion_api():
    logging.info("Received /api/generate_conclusion POST request.")
    data = request.get_json()
    text = data.get('text', '')

    detected_language = get_request_language(text) # Language Detection

    if not text:
        return jsonify({"conclusion": "", "error": "Please paste your main text to generate a conclusion."}), 400

    try:
        # Assuming generate_conclusion accepts 'language' as a parameter
        conclusion = generate_conclusion(text, detected_language)
        if str(conclusion).startswith("Error:"):
            logging.error(f"Conclusion generation API call failed: {conclusion}")
            return jsonify({"conclusion": "", "error": conclusion}), 500

        logging.info("Conclusion generation successful.")
        return jsonify({"conclusion": str(conclusion).strip()})
    except Exception as e:
        error_message = f"An unexpected error occurred during conclusion generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"conclusion": "", "error": error_message}), 500


@app.route('/api/generate_business_names', methods=['POST'])
def generate_business_names_api():
    logging.info("Received /api/generate_business_names POST request.")
    data = request.get_json()
    keywords = data.get('keywords', '')
    style = data.get('style', 'Creative')

    detected_language = get_request_language(keywords) # Language Detection (using keywords)

    if not keywords:
        return jsonify({"names": [], "error": "Please enter keywords about your business to generate names."}), 400

    try:
        # Assuming generate_business_names accepts 'language' as a parameter
        names = generate_business_names(keywords, style, detected_language)
        if isinstance(names, list) and names and str(names[0]).startswith("Error:"):
            logging.error(f"Business name generation API call failed: {names[0]}")
            return jsonify({"names": [], "error": names[0]}), 500

        logging.info("Business name generation successful.")
        return jsonify({"names": names})
    except Exception as e:
        error_message = f"An unexpected error occurred during business name generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"names": [], "error": error_message}), 500


@app.route('/api/generate_email_subjects', methods=['POST'])
def generate_email_subjects_api():
    logging.info("Received /api/generate_email_subjects POST request.")
    data = request.get_json()
    content = data.get('content', '')
    tone = data.get('tone', 'Professional')

    detected_language = get_request_language(content) # Language Detection (using content)

    if not content:
        return jsonify({"subjects": [], "error": "Please describe what your email is about."}), 400

    try:
        # Assuming generate_email_subjects accepts 'language' as a parameter
        subjects = generate_email_subjects(content, tone, detected_language)
        if isinstance(subjects, list) and subjects and str(subjects[0]).startswith("Error:"):
            logging.error(f"Email subject generation API call failed: {subjects[0]}")
            return jsonify({"subjects": [], "error": subjects[0]}), 500

        logging.info("Email subject generation successful.")
        return jsonify({"subjects": subjects})
    except Exception as e:
        error_message = f"An unexpected error occurred during email subject generation: {str(e)}"
        logging.error(error_message, exc_info=True)
        return jsonify({"subjects": [], "error": error_message}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
