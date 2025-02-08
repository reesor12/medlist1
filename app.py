import streamlit as st
import wikipediaapi
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import requests
import urllib.parse

# Set up Wikipedia API with a proper user-agent
wiki_api = wikipediaapi.Wikipedia(
    language="en",
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent="MyMedicalBot/1.0 (contact: youremail@example.com)"  # Replace with your info
)

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


# Function to explain a medical word or drug
def explain_word(word):
    word = word.lower()
    medline_info = get_medlineplus_info(word)
    if medline_info:
        return medline_info
    return get_wikipedia_summary(word)


# Function to preprocess and scan text from an image
def scan_text_from_image(image_path):
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
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"Error scanning image: {e}"


# Function to get simple definitions from scanned text
def get_definitions_from_scanned_text(scanned_text):
    words = list(set([word.strip() for word in scanned_text.split() if word.strip()]))
    definitions = []
    not_found = []

    for word in words:
        # Skip terms that are too short or non-medical
        if len(word) <= 2 or not word.isalpha():
            not_found.append(word)
            continue

        definition = explain_word(word)
        if definition:
            definitions.append(f"{word}: {definition}")
        else:
            not_found.append(word)

    return definitions, not_found


# Streamlit App
st.set_page_config(page_title="Medical Term Explainer", page_icon="💊", layout="centered")

# Title and description
st.title("💊 Medical Term Explainer")
st.write("Hi! I can explain medical words and drugs in a simple way. Enter a term or upload an image to get started.")

# Sidebar for instructions
st.sidebar.title("Instructions")
st.sidebar.write("""
1. **Enter a Medical Term:** Type a medical word or drug in the input box and press Enter.
2. **Upload an Image:** If you have an image with medical terms, upload it using the file uploader.
3. **View Results:** Definitions will be displayed for valid medical terms. Non-medical terms will be listed separately.
""")

# Main input section
user_input = st.text_input("Enter a medical word or drug:").strip()

if user_input:
    if user_input.lower() == "scan":
        st.write("Please upload an image below.")
    else:
        explanation = explain_word(user_input)
        if explanation:
            st.success(f"**{user_input}:** {explanation}")
        else:
            st.warning(f"**Not Listed:** '{user_input}' is not a medical term.")

# Image upload section
st.write("---")
st.subheader("📷 Upload an Image")
uploaded_file = st.file_uploader("Upload an image file (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    st.write("Scanning image...")
    scanned_text = scan_text_from_image(uploaded_file)
    st.write(f"**Scanned Text:** {scanned_text}")

    definitions, not_found = get_definitions_from_scanned_text(scanned_text)
    if definitions:
        st.subheader("📖 Definitions")
        for definition in definitions:
            st.info(definition)
    if not_found:
        st.subheader("🚫 Not Listed")
        for term in not_found:
            st.warning(term)

# Footer
st.write("---")
st.write("Made with ❤️ by [Reesor]")
#streamlit run app.py