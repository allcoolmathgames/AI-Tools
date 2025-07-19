import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Import specific functions from the new modular tool files
# Ensure these files exist in your 'tools_logic' folder.
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
# ==============================================================================

@app.route('/')
def index():
    """Renders the main index page (AI Summarizer tool)."""
    return render_template('summarizer/index.html')

@app.route('/summarizer')
def summarizer_page():
    """Renders the AI Summarizer tool page."""
    return render_template('summarizer/index.html')

@app.route('/article-rewriter')
def article_rewriter_page():
    """Renders the Article Rewriter tool page."""
    return render_template('article_rewriter/index.html')

@app.route('/plagiarism-checker')
def plagiarism_checker_page():
    """Renders the Plagiarism Checker tool page."""
    return render_template('plagiarism_checker/index.html')

@app.route('/paraphrasing-tool')
def paraphrasing_tool_page():
    """Renders the Paraphrasing Tool page."""
    return render_template('paraphrasing_tool/index.html')

@app.route('/content-idea-generator')
def content_idea_generator_page():
    """Renders the Content Idea Generator tool page."""
    return render_template('content_idea_generator/index.html')

@app.route('/slogan-generator')
def slogan_generator_page():
    """Renders the Slogan Generator tool page."""
    return render_template('slogan_generator/index.html')

@app.route('/ai-text-to-humanize')
def ai_humanizer_page():
    """Renders the AI Text Humanizer tool page."""
    return render_template('ai_text_to_humanize/index.html')

@app.route('/ai-email-generator')
def ai_email_generator_page():
    """Renders the AI Email Generator tool page."""
    return render_template('ai_email_generator/index.html')

@app.route('/grammar-checker')
def grammar_checker_page():
    """Renders the Grammar Checker tool page."""
    return render_template('grammar_checker/index.html')

@app.route('/ai-story-generator')
def ai_story_generator_page():
    """Renders the AI Story Generator tool page."""
    return render_template('ai_story_generator/index.html')

@app.route('/ai-product-description-generator')
def ai_product_description_generator_page():
    """Renders the AI Product Description Generator tool page."""
    return render_template('ai_product_description_generator/index.html')

@app.route('/essay-generator')
def essay_generator_page():
    """Renders the Essay Generator tool page."""
    return render_template('essay_generator/index.html')

@app.route('/trending-news-generator')
def trending_news_generator_page():
    """Renders the Trending News Generator tool page."""
    return render_template('trending_news_generator/index.html')

@app.route('/acronym-generator')
def acronym_generator_page():
    """Renders the Acronym Generator tool page."""
    return render_template('acronym_generator/index.html')

@app.route('/abstract-generator')
def abstract_generator_page():
    """Renders the Abstract Generator tool page."""
    return render_template('abstract_generator/index.html')

@app.route('/adjective-generator')
def adjective_generator_page():
    """Renders the Adjective Generator tool page."""
    return render_template('adjective_generator/index.html')

@app.route('/hook-generator')
def hook_generator_page():
    """Renders the Hook Generator tool page."""
    return render_template('hook_generator/index.html')

@app.route('/title-generator')
def title_generator_page():
    """Renders the Title Generator tool page."""
    return render_template('title_generator/index.html')

@app.route('/conclusion-generator')
def conclusion_generator_page():
    """Renders the Conclusion Generator tool page."""
    return render_template('conclusion_generator/index.html')

@app.route('/business-name-generator')
def business_name_generator_page():
    """Renders the Business Name Generator tool page."""
    return render_template('business_name_generator/index.html')

@app.route('/email-subject-line-generator')
def email_subject_line_generator_page():
    """Renders the Email Subject Line Generator tool page."""
    return render_template('email_subject_line_generator/index.html')

# --- New Static Pages Routes ---
@app.route('/about-us')
def about_us_page():
    """Renders the About Us page."""
    return render_template('pages/about_us.html')

@app.route('/contact')
def contact_page():
    """Renders the Contact Us page."""
    return render_template('pages/contact.html')

@app.route('/privacy-policy')
def privacy_policy_page():
    """Renders the Privacy Policy page."""
    return render_template('pages/privacy_policy.html')

@app.route('/terms-conditions')
def terms_conditions_page():
    """Renders the Terms & Conditions page."""
    return render_template('pages/terms_conditions.html')
# --- New Static Pages Routes End ---

# --- Blog Routes (Yeh routes aapki app.py mein pehle se maujood hain aur sahi hain) ---
@app.route('/blogs/')
def blogs_index():
    """Renders the main blog listing page."""
    return render_template('blogs/index.html')

@app.route('/blogs/<string:slug>.html')
def blog_post(slug):
    """Renders individual blog post based on slug."""
    try:
        return render_template(f'blogs/{slug}.html')
    except Exception as e:
        # Agar blog post file na mile, to 404 error page dikha sakte hain
        return render_template('404.html'), 404 # Assuming you have a 404.html template
# --- Blog Routes End ---

# ==============================================================================
# API Endpoints: Define routes for handling API requests from the frontend
# ==============================================================================

@app.route('/api/summarize', methods=['POST'])
def summarize_api():
    """API endpoint for text summarization."""
    data = request.get_json()
    text = data.get('text', '')
    length_ratio = data.get('length', 0.5) 

    if not text:
        return jsonify({"summary": "", "error": "Please provide text to summarize."}), 400
    
    try:
        summary = summarize_text(text, length_ratio)
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

    if not text:
        return jsonify({"rewritten_text": "", "error": "Please provide text to rewrite."}), 400
    
    try:
        rewritten_text = rewrite_article(text, creativity)
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

    if not text:
        return jsonify({"humanized_text": "", "error": "Please provide text to humanize."}), 400
    
    try:
        humanized_text = humanize_text(text, creativity)
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

    if not subject and not purpose: 
        return jsonify({"generated_email": "", "error": "Please provide either a subject or purpose for the email."}), 400
    
    try:
        email_content = generate_email(subject, purpose, recipient)
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

    if not keywords:
        return jsonify({"content_ideas": [], "error": "Please provide keywords for content ideas."}), 400
    
    try:
        content_ideas = generate_content_ideas(keywords)
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

    if not text:
        return jsonify({"paraphrased_text": "", "error": "Please provide text to paraphrase."}), 400
    
    try:
        paraphrased_text = paraphrase_text(text)
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

    if not text:
        return jsonify({"corrected_text": "", "error": "Please provide text to check grammar."}), 400
    
    try:
        corrected_text = check_grammar(text)
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

    if not keywords:
        return jsonify({"slogans": [], "error": "Please provide keywords for slogan generation."}), 400
    
    try:
        num_slogans = int(num_slogans)
        num_slogans = max(1, min(num_slogans, 10))
    except (ValueError, TypeError):
        logging.warning(f"Invalid num_slogans received: {num_slogans}. Defaulting to 5.")
        num_slogans = 5

    try:
        slogans = generate_slogans(keywords, num_slogans)
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

    if not text:
        return jsonify({"error": "Please provide text to check."}), 400

    try:
        results = check_plagiarism_and_ai(text)
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

    if not topic:
        return jsonify({"story": "", "error": "Please provide a story topic or keywords."}), 400
    
    try:
        story = generate_story(topic, genre, characters) 
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

    if not product_name and not product_keywords: 
        return jsonify({"description": "", "error": "Please enter a product name or keywords to generate a description."}), 400
    
    try:
        description = generate_product_description(product_name, product_keywords, target_audience, tone)
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

    if not topic:
        return jsonify({"essay": "", "error": "Please provide a topic for the essay."}), 400
    
    try:
        essay = generate_essay(topic, length, style, keywords)
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

    if not keywords and not category:
        return jsonify({"news_summary": "", "error": "Please enter a news topic/keywords or select a category."}), 400
    
    try:
        num_articles = int(num_articles) if isinstance(num_articles, str) and num_articles.isdigit() else 1

        news_summary = generate_trending_news(keywords, category, num_articles)
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

    if not text:
        return jsonify({"acronym": "", "error": "Please enter a phrase or text to generate an acronym."}), 400

    try:
        acronym = generate_acronym(text)
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

    if not text:
        return jsonify({"abstract": "", "error": "Please paste your main text to generate an abstract."}), 400

    try:
        abstract = generate_abstract(text)
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

    if not text:
        return jsonify({"adjectives": [], "error": "Please enter a noun or sentence to get adjectives."}), 400

    try:
        adjectives = generate_adjectives(text)
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

    if not topic:
        return jsonify({"hooks": [], "error": "Please describe your content topic to generate hooks."}), 400

    try:
        hooks = generate_hooks(topic, tone)
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

    if not topic:
        return jsonify({"titles": [], "error": "Please describe your content to generate titles."}), 400

    try:
        titles = generate_titles(topic)
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

    if not text:
        return jsonify({"conclusion": "", "error": "Please paste your main text to generate a conclusion."}), 400

    try:
        conclusion = generate_conclusion(text)
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

    if not keywords:
        return jsonify({"names": [], "error": "Please enter keywords about your business to generate names."}), 400

    try:
        names = generate_business_names(keywords, style)
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

    if not content:
        return jsonify({"subjects": [], "error": "Please describe what your email is about."}), 400

    try:
        subjects = generate_email_subjects(content, tone)
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