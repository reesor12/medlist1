import os
import streamlit as st
import wikipediaapi
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import requests
import urllib.parse
from deep_translator import GoogleTranslator
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set Tesseract data path
os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/4.00/tessdata'

# Set up Wikipedia API
wiki_api = wikipediaapi.Wikipedia(
    language="en",
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent="MyMedicalBot/1.0 (contact: youremail@example.com)"
)

# Example medical dictionary
medical_dictionary = {
    "diabetes": "A chronic condition that affects how your body turns food into energy.",
    "aspirin": "A medication used to reduce pain, fever, or inflammation.",
    "paracetamol": "A common pain reliever and fever reducer.",
    "hypertension": "High blood pressure, a condition that increases the risk of heart disease.",
    "antibiotic": "A type of medicine used to treat bacterial infections.",
}

# List of common English words to skip
common_english_words = {
    "the", "and", "can", "for", "with", "this", "that", "are", "you", "your",
    # Add more words as needed
}

# Supported languages for translation and OCR
supported_languages = {
    "English": {"ui": "en", "ocr": "eng"},
    "Spanish": {"ui": "es", "ocr": "spa"},
    "French": {"ui": "fr", "ocr": "fra"},
    "German": {"ui": "de", "ocr": "deu"},
    "Chinese (Simplified)": {"ui": "zh-cn", "ocr": "chi_sim"},
    "Hindi": {"ui": "hi", "ocr": "hin"},
    "Arabic": {"ui": "ar", "ocr": "ara"},
    "Russian": {"ui": "ru", "ocr": "rus"},
    "Portuguese": {"ui": "pt", "ocr": "por"},
    "Japanese": {"ui": "ja", "ocr": "jpn"},
}

# Function to translate text
def translate_text(text, dest_language):
    try:
        translator = GoogleTranslator(source='auto', target=dest_language)
        return translator.translate(text)
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text

# Streamlit App
st.set_page_config(page_title="Medical Term Explainer", page_icon="💊", layout="centered")

# Sidebar for language selection
st.sidebar.title("Settings")
language = st.sidebar