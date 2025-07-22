import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from docx import Document
import os

# --- Set page config ---
st.set_page_config(page_title="Admin Bot", layout="wide")

# --- Custom CSS styling ---
st.markdown("""
    <style>
        .main {
            background-color: #f7f9fc;
        }
        .title {
            font-size: 36px;
            color: white;
            background: linear-gradient(90deg, #007BFF, #FF6F00);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stTextInput > div > div > input {
            background-color: #fffbea;
            border: 2px solid #007BFF;
            padding: 10px;
            font-size: 16px;
        }
        .stTextArea textarea {
            background-color: #fff;
            font-size: 14px;
        }
        .stButton>button {
            background-color: #007BFF;
            color: white;
        }
        .stSpinner {
            color: #FF6F00;
        }
        .answer-box {
            background-color: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Gemini API setup ---
genai.configure(api_key="AIzaSyBX_cYdTx-0wMMufQVY2bijRgVxHirUoos")
model = genai.GenerativeModel("models/gemini-2.0-flash-lite")

# --- Load document text ---
@st.cache_data
def load_document_text():
    text = ""
    file_path = r"D:\worked_projects\Chatbot_ui\Ollama-mistral-ui-mistral\ollama_langchain\source_document\Associate Handbook_edited.pdf"

    if file_path.endswith(".pdf") and os.path.exists(file_path):
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif file_path.endswith(".docx") and os.path.exists(file_path):
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

document_text = load_document_text()

# --- UI layout ---
st.markdown('<div class="title">📄 Admin Assistant Chatbot</div>', unsafe_allow_html=True)
st.markdown("Ask questions based on the company handbook.")

# Optional: Show preview of loaded document
with st.expander("📄 Preview Loaded Document", expanded=False):
    st.text_area("Document Snippet", document_text[:900000], height=200)

# --- Input field for user question ---
question = st.text_input("Ask a question", placeholder="E.g., What is the company's leave policy?")

if question:
    with st.spinner("Thinking..."):
        # Step 1: Try answering using the document
        prompt_with_doc = f"""
You are an AI assistant. Answer the user's question based ONLY on the document provided below.
If the answer is not found in the document, respond with exactly this sentence:
"The document does not contain this information."

Document:
\"\"\"{document_text[:300000]}\"\"\"

Question:
{question}

Answer:
"""
        response = model.generate_content(prompt_with_doc)
        answer = response.text.strip()

        # Step 2: If no relevant answer in document, respond generally
        if answer == "The document does not contain this information.":
            # Ask Gemini normally
            general_response = model.generate_content(question)
            answer = general_response.text.strip()

        # Display the answer
        st.subheader("💬 Answer:")
        st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)
