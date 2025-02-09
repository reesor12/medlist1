import streamlit as st
import wikipediaapi
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import requests
import urllib.parse
from googletrans import Translator  # For translation

# Set up Wikipedia API with a proper user-agent
wiki_api = wikipediaapi.Wikipedia(
    language="en",
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent="MyMedicalBot/1.0 (contact: youremail@example.com)"  # Replace with your info
)

# Example medical dictionary (you can expand this)
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
    "have", "has", "was", "were", "will", "would", "should", "could", "about",
    "from", "their", "there", "what", "which", "when", "where", "why", "how",
    "who", "whom", "whose", "into", "over", "under", "after", "before", "between",
    "through", "during", "without", "within", "along", "among", "because", "since",
    "until", "while", "though", "although", "even", "much", "many", "few", "little",
    "more", "most", "less", "least", "only", "just", "also", "too", "very", "really",
    "quite", "some", "any", "no", "not", "none", "nothing", "something", "anything",
    "everything", "everyone", "everybody", "someone", "somebody", "anyone", "anybody",
    "no one", "nobody", "each", "both", "either", "neither", "other", "another",
    "such", "as", "so", "if", "then", "else", "whether", "either", "neither", "nor",
    "or", "but", "yet", "however", "therefore", "thus", "hence", "nevertheless",
    "meanwhile", "otherwise", "instead", "besides", "moreover", "furthermore",
    "although", "though", "even", "if", "unless", "until", "while", "when", "where",
    "why", "how", "what", "which", "who", "whom", "whose", "because", "since", "so",
    "that", "these", "those", "this", "those", "them", "they", "he", "she", "it",
    "we", "us", "our", "ours", "you", "your", "yours", "me", "my", "mine", "him",
    "his", "her", "hers", "its", "our", "ours", "their", "theirs", "myself",
    "yourself", "himself", "herself", "itself", "ourselves", "yourselves",
    "themselves", "a", "an", "the", "and", "but", "if", "or", "because", "as",
    "until", "while", "of", "at", "by", "for", "with", "about", "against", "between",
    "into", "through", "during", "before", "after", "above", "below", "to", "from",
    "up", "down", "in", "out", "on", "off", "over", "under", "again", "further",
    "then", "once", "here", "there", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can",
    "will", "just", "don", "should", "now"
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

# Initialize translator
translator = Translator()

# Function to translate text while skipping common words
def translate_text(text, dest_language):
    try:
        # Split the text into words
        words = text.split()
        translated_words = []
        for word in words:
            # Skip common words
            if word.lower() in common_english_words:
                translated_words.append(word)
            else:
                # Translate non-common words
                translated = translator.translate(word, dest=dest_language)
                translated_words.append(translated.text)
        # Join the words back into a sentence
        return " ".join(translated_words)
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text  # Return original text if translation fails


# Function to fetch a simple Wikipedia explanation
def get_wikipedia_summary(term):
    page = wiki_api.page(term)
    if page.exists():
        summary = page.summary.split(".")[0]  # Get only the first sentence for simplicity
        return summary if summary else None
    return None


# Function to fetch medical information from MedlinePlus API
def get_medlineplus_info(term):
    url = f"https://wsearch.nlm.nih.gov/ws/query?db=healthTopics&term={urllib.parse.quote(term)}"
    try:
        response = requests.get(url, headers={"User-Agent": "MyMedicalBot/1.0"})
        if response.status_code == 200:
            data = response.text
            if "<title>" in data:
                title_start = data.find("<title>") + len("<title>")
                title_end = data.find("</title>", title_start)
                title = data[title_start:title_end]
                return title
        return None
    except Exception as e:
        st.error(f"Error fetching MedlinePlus info: {e}")
        return None


# Function to check if a term is a valid medical term
def is_medical_term(term):
    # Skip terms that are too short or common English words
    if len(term) <= 2 or term.lower() in common_english_words:
        return False
    # Check if the term is in the predefined medical dictionary
    if term.lower() in medical_dictionary:
        return True
    # Check if MedlinePlus has information about the term
    if get_medlineplus_info(term):
        return True
    # Check if Wikipedia has information about the term
    if get_wikipedia_summary(term):
        return True
    return False


# Function to explain a medical word or drug
def explain_word(word):
    word = word.lower()
    medline_info = get_medlineplus_info(word)
    if medline_info:
        return medline_info
    return get_wikipedia_summary(word)


# Function to preprocess and scan text from an image
def scan_text_from_image(image_path, ocr_language):
    try:
        # Open the image using Pillow
        image = Image.open(image_path)
        # Convert to grayscale
        image = image.convert("L")
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        # Sharpen the image
        image = image.filter(ImageFilter.SHARPEN)
        # Resize the image for better OCR accuracy
        new_size = (image.width * 2, image.height * 2)
        image = image.resize(new_size, Image.LANCZOS)
        # Use pytesseract to extract text
        text = pytesseract.image_to_string(image, lang=ocr_language)
        return text.strip()
    except Exception as e:
        return f"Error scanning image: {e}"


# Function to get simple definitions from scanned text
def get_definitions_from_scanned_text(scanned_text):
    words = list(set([word.strip() for word in scanned_text.split() if word.strip()]))
    definitions = []
    not_found = []

    for word in words:
        # Check if the word is a valid medical term
        if is_medical_term(word):
            definition = explain_word(word)
            if definition:
                definitions.append(f"{word}: {definition}")
            else:
                not_found.append(word)
        else:
            not_found.append(word)

    return definitions, not_found


# Streamlit App
st.set_page_config(page_title="Medical Term Explainer", page_icon="💊", layout="centered")

# Sidebar for language selection
st.sidebar.title("Settings")
language = st.sidebar.selectbox("Select Language", list(supported_languages.keys()))

# Get the selected language's UI and OCR codes
ui_language = supported_languages[language]["ui"]
ocr_language = supported_languages[language]["ocr"]

# Translate all static text
def get_translated_text(ui_language):
    translations = {
        "title": translate_text("💊 Medical Term Explainer", ui_language),
        "description": translate_text("Hi! I can explain medical words and drugs in a simple way. Enter a term or upload an image to get started.", ui_language),
        "input_label": translate_text("Enter a medical word or drug:", ui_language),
        "upload_label": translate_text("Upload an image file (PNG, JPG, JPEG):", ui_language),
        "scanning_text": translate_text("Scanning image...", ui_language),
        "definitions_header": translate_text("📖 Definitions", ui_language),
        "not_listed_header": translate_text("🚫 Not Listed", ui_language),
        "footer": translate_text("Made with ❤️ by [Your Name]", ui_language),
    }
    return translations


# Get translated text
translations = get_translated_text(ui_language)

# Title and description
st.title(translations["title"])
st.write(translations["description"])

# Main input section
user_input = st.text_input(translations["input_label"]).strip()

if user_input:
    if user_input.lower() == "scan":
        st.write(translate_text("Please upload an image below.", ui_language))
    else:
        if is_medical_term(user_input):
            explanation = explain_word(user_input)
            if explanation:
                # Translate the explanation while skipping common words
                translated_explanation = translate_text(explanation, ui_language)
                st.success(f"**{user_input}:** {translated_explanation}")
            else:
                st.warning(translate_text(f"**Not Listed:** '{user_input}' is not a medical term.", ui_language))
        else:
            st.warning(translate_text(f"**Not a Medical Term:** '{user_input}' is not a medical term.", ui_language))

# Image upload section
st.write("---")
st.subheader(translations["upload_label"])
uploaded_file = st.file_uploader("", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.write(translations["scanning_text"])
    scanned_text = scan_text_from_image(uploaded_file, ocr_language)
    st.write(f"**{translate_text('Scanned Text:', ui_language)}** {scanned_text}")

    definitions, not_found = get_definitions_from_scanned_text(scanned_text)
    if definitions:
        st.subheader(translations["definitions_header"])
        for definition in definitions:
            term, explanation = definition.split(":", 1)
            translated_explanation = translate_text(explanation.strip(), ui_language)
            st.info(f"{term}: {translated_explanation}")
    if not_found:
        st.subheader(translations["not_listed_header"])
        for term in not_found:
            st.warning(term)

# Footer
st.write("---")
st.write(translations["footer"])