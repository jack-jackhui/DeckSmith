import fitz  # PyMuPDF
import docx
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from vector_db import add_to_vector_db

model = SentenceTransformer('all-MiniLM-L6-v2')
index = faiss.IndexFlatL2(384)

def process_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def process_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text
    return text

def process_and_store_documents(uploaded_files):
    for file in uploaded_files:
        if file.type == "application/pdf":
            text = process_pdf(file)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = process_docx(file)
        add_to_vector_db(text)