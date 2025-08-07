release: python -c "import nltk; nltk.download('punkt', download_dir='/app/nltk_data'); nltk.download('stopwords', download_dir='/app/nltk_data')"
web: gunicorn app:app --bind 0.0.0.0:$PORT
