import streamlit as st
import sympy as sp
import wolframalpha
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from googletrans import Translator

# Initialize Wolfram Alpha (free tier)
wolfram_client = wolframalpha.Client("W3UVEQ-6JAVJQ82R9")  # Get a free App ID from https://wolframalpha.com

# Initialize translator
translator = Translator()

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
        translated = translator.translate(text, dest=dest_language)
        return translated.text
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text

# Function to solve math problems
def solve_math_problem(problem):
    try:
        solution = sp.sympify(problem)
        return f"Solution: {solution}"
    except:
        try:
            res = wolfram_client.query(problem)
            return next(res.results).text
        except:
            return "Sorry, I couldn't solve this math problem."

# Function to explain science concepts
def explain_science_concept(concept):
    try:
        res = wolfram_client.query(concept)
        return next(res.results).text
    except:
        return "Sorry, I couldn't find an explanation for this concept."

# Function to analyze English sentences
def analyze_english_sentence(sentence):
    # Placeholder for grammar/sentence analysis
    return "This is a placeholder for English sentence analysis."

# Function to scan text from an image
def scan_text_from_image(image_path, ocr_language):
    try:
        image = Image.open(image_path)
        image = image.convert("L")
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        image = image.filter(ImageFilter.SHARPEN)
        new_size = (image.width * 2, image.height * 2)
        image = image.resize(new_size, Image.LANCZOS)
        text = pytesseract.image_to_string(image, lang=ocr_language)
        return text.strip()
    except Exception as e:
        return f"Error scanning image: {e}"

# Streamlit App
st.set_page_config(page_title="Homework Assistant", page_icon="📚", layout="centered")

# Sidebar for language selection
st.sidebar.title("Settings")
language = st.sidebar.selectbox("Select Language", list(supported_languages.keys()))
ui_language = supported_languages[language]["ui"]
ocr_language = supported_languages[language]["ocr"]

# Translate static text
def get_translated_text(ui_language):
    translations = {
        "title": translate_text("📚 Homework Assistant", ui_language),
        "description": translate_text("Hi! I can help with math, science, and English homework. Enter a question or upload an image to get started.", ui_language),
        "input_label": translate_text("Enter your question:", ui_language),
        "upload_label": translate_text("Upload an image file (PNG, JPG, JPEG):", ui_language),
        "scanning_text": translate_text("Scanning image...", ui_language),
        "footer": translate_text("Made with ❤️ by [Your Name]", ui_language),
    }
    return translations

# Get translated text
translations = get_translated_text(ui_language)

# Title and description
st.title(translations["title"])
st.write(translations["description"])

# Subject selection
subject = st.selectbox("Select Subject", ["Math", "Science", "English"])

# Main input section
user_input = st.text_input(translations["input_label"]).strip()

if user_input:
    if subject == "Math":
        solution = solve_math_problem(user_input)
        st.success(translate_text(solution, ui_language))
    elif subject == "Science":
        explanation = explain_science_concept(user_input)
        st.success(translate_text(explanation, ui_language))
    elif subject == "English":
        analysis = analyze_english_sentence(user_input)
        st.success(translate_text(analysis, ui_language))

# Image upload section
st.write("---")
st.subheader(translations["upload_label"])
uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.write(translations["scanning_text"])
    scanned_text = scan_text_from_image(uploaded_file, ocr_language)
    st.write(f"**{translate_text('Scanned Text:', ui_language)}** {scanned_text}")

    if subject == "Math":
        solution = solve_math_problem(scanned_text)
        st.success(translate_text(solution, ui_language))
    elif subject == "Science":
        explanation = explain_science_concept(scanned_text)
        st.success(translate_text(explanation, ui_language))
    elif subject == "English":
        analysis = analyze_english_sentence(scanned_text)
        st.success(translate_text(analysis, ui_language))

# Footer
st.write("---")
st.write(translations["footer"])