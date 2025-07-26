import os
import re
import logging
import nltk

try:
    # Newer versions expose this at root. If it fails, we’ll fallback to the attribute on genai.
    from google.generativeai.types import GenerationConfig  # type: ignore
    HAS_GENAI_TYPES = True
except Exception:  # pragma: no cover
    HAS_GENAI_TYPES = False

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def missing_api_key_error_msg(tool_name: str) -> str:
    return (
        f"Error: Gemini API not configured for {tool_name}. "
        "Please ensure GOOGLE_API_KEY environment variable is set."
    )


# -------------------------------------------------------------------
# Gemini API configuration
# -------------------------------------------------------------------
GEMINI_API_AVAILABLE = False
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

try:
    import google.generativeai as genai  # type: ignore

    gemini_api_key = os.environ.get("GOOGLE_API_KEY")
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        GEMINI_API_AVAILABLE = True
        logger.info("Google Generative AI loaded & configured for abstract_generator_tool.")
    else:
        logger.warning(
            "GOOGLE_API_KEY environment variable not set. Gemini functions will not work in abstract_generator_tool."
        )
except ImportError:
    logger.warning(
        "google-generativeai library not found. Gemini functions will not work in abstract_generator_tool."
    )
    GEMINI_API_AVAILABLE = False
except Exception as e:
    logger.error(
        "Error configuring Gemini API for abstract_generator_tool: %s. Gemini functions might not work.", e
    )
    GEMINI_API_AVAILABLE = False


# -------------------------------------------------------------------
# NLTK data path setup
# -------------------------------------------------------------------
NLTK_DATA_DIR = os.path.join("/app", "nltk_data")
os.makedirs(NLTK_DATA_DIR, exist_ok=True)
if NLTK_DATA_DIR not in nltk.data.path:
    nltk.data.path.append(NLTK_DATA_DIR)

logger.info("NLTK data directory ensured at: %s", NLTK_DATA_DIR)

def ensure_nltk_data() -> bool:
    """Ensure that required NLTK resources exist (punkt, stopwords)."""
    try:
        nltk.data.find("tokenizers/punkt")
        logger.info("NLTK 'punkt' tokenizer is available.")

        nltk.data.find("corpora/stopwords")
        logger.info("NLTK 'stopwords' corpus is available.")
        return True
    except LookupError as e:
        logger.error(
            "NLTK data missing: %s. Please pre-download into %s (during build/deploy).",
            e, NLTK_DATA_DIR
        )
        return False
    except Exception as e:  # pragma: no cover
        logger.error("NLTK data check failed: %s", e)
        return False

_NLTK_OK = ensure_nltk_data()
if not _NLTK_OK:
    logger.error("Critical: NLTK data not fully set up. Some functionalities may not work.")


# -------------------------------------------------------------------
# Gemini model helper
# -------------------------------------------------------------------
_gemini_model = None

def _get_gemini_model():
    global _gemini_model
    if not GEMINI_API_AVAILABLE:
        raise RuntimeError("Gemini API is not available. Ensure GOOGLE_API_KEY is set.")

    if _gemini_model is not None:
        return _gemini_model

    # Older/newer versions differ — if GenerationConfig import failed, we still can call without it.
    try:
        _gemini_model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    except Exception as e:
        logger.error("Failed to load Gemini model '%s': %s", GEMINI_MODEL_NAME, e)
        raise
    return _gemini_model


# -------------------------------------------------------------------
# Public function
# -------------------------------------------------------------------
def generate_abstract(text: str, target_language: str = "English") -> str:
    """
    Generate a concise abstract in the given language (target_language) using Gemini.
    """
    if not GEMINI_API_AVAILABLE:
        logger.error(missing_api_key_error_msg("abstract_generator_tool"))
        # -------- OPTIONAL: simple fallback (uncomment if you want) ----------
        # return naive_fallback_abstract(text, target_language)
        return missing_api_key_error_msg("abstract_generator_tool")

    if not text or not text.strip():
        return "Error: Please provide text."

    if not _NLTK_OK:
        logger.warning("NLTK data setup issue detected. Proceeding anyway (Gemini doesn't need it).")

    try:
        model = _get_gemini_model()

        prompt = (
            f"Generate a concise and professional abstract in {target_language} for the following document or text. "
            f"The abstract should summarize the main objectives, methods, results, and conclusions. "
            f"Do not use any markdown formatting like **bold**, *italic*, or ##headings. Provide plain text.\n\n"
            f"Document/Text:\n---\n{text}\n---\n\nAbstract:"
        )

        # Use GenerationConfig only if it's available from the lib version
        if HAS_GENAI_TYPES:
            cfg = GenerationConfig(
                temperature=0.3,
                top_p=0.8,
                top_k=30,
                candidate_count=1,
            )
            response = model.generate_content(prompt, generation_config=cfg)
        else:
            # Older libs accept these via kwargs
            response = model.generate_content(
                prompt,
                temperature=0.3,
                top_p=0.8,
                top_k=30,
                candidate_count=1,
            )

        # Different lib versions expose text differently. Try the common path:
        text_out = None

        # Newer: response.text
        if hasattr(response, "text") and response.text:
            text_out = response.text.strip()

        # Older: response.candidates[0].content.parts[0].text
        if not text_out and getattr(response, "candidates", None):
            try:
                text_out = response.candidates[0].content.parts[0].text.strip()
            except Exception:
                pass

        if not text_out:
            return "Gemini could not generate an abstract. Please try different details."

        # Remove leading "Abstract:" if present
        text_out = re.sub(r"^(Abstract:)?\s*", "", text_out, flags=re.IGNORECASE).strip()
        return text_out

    except Exception as e:
        logger.error("Error generating abstract with Gemini: %s: %s", type(e).__name__, e, exc_info=True)
        return f"Error: {type(e).__name__}: {e}"


# -------------------------------------------------------------------
# (Optional) Naive fallback if you ever want to produce *something* without Gemini
# -------------------------------------------------------------------
def naive_fallback_abstract(text: str, target_language: str = "English", max_sentences: int = 4) -> str:
    """
    Extremely basic extractive fallback (no real language support).
    If you want it, uncomment usage above.
    """
    try:
        from nltk.tokenize import sent_tokenize
    except Exception:
        return text[:600] + "..."

    sentences = sent_tokenize(text)
    return " ".join(sentences[:max_sentences]).strip()


if __name__ == "__main__":
    # Simple quick test (only works if GOOGLE_API_KEY is set)
    sample_text = (
        "This research paper investigates the impact of climate change on coastal ecosystems, "
        "specifically focusing on coral reefs in the Indo-Pacific region. We employed a multi-faceted "
        "approach combining satellite imagery analysis, in-situ temperature monitoring, and biodiversity "
        "surveys conducted over a period of ten years. Our findings indicate a significant correlation "
        "between rising ocean temperatures and increased coral bleaching events, leading to a measurable "
        "decline in reef biodiversity. We also observed changes in fish populations and migration patterns, "
        "suggesting broader ecological disruptions. The study highlights the urgent need for global climate "
        "action and localized conservation efforts to mitigate these impacts."
    )

    print(generate_abstract(sample_text, target_language="English"))
