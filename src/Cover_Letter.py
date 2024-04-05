from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L12-v2')
from nltk.tokenize import sent_tokenize 
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import torch
from nltk.corpus import stopwords
import re 
import PyPDF2 as pdf
from PyPDF2 import PdfReader





keywords ="""My work adds business value to customers.
             My work adds career value to fellow employees.
             My work adds social value to communities.
             My work shows my integrity.
             My work shows my team work and team spirit.
             My work shows my trustworthy quality.
             My work showcased digital transformation. 
             My work shows my simplicity. 
             My work shows my entrepreneurial spirit. 
             I have good communication skills. 
             I have good interpersonal skills. 
             My work shows innovation. 
             My work shows resilience. 
             I am confident about my work. 
             I have leadership qualities. 
             My work always meets deadlines."""

# Text Extraction
def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file.

    Arguments:
    file_path (str): Path to the PDF file.

    Returns:
    str: Extracted text from the PDF.
    """
    with open(file_path, "rb") as file:
        reader = PdfReader(file)
        length = reader.getNumPages()
        text = ""
        for page_num in range(length):
            text += reader.pages[page_num].extract_text()
    return text


# Cleaning the Data
stop_words = set(stopwords.words('english'))
def clean_text(sentence):
    # Removing URLS
    sentence = re.sub(r"https?://\S+|www\.\S+"," ",sentence)
    
    # Removing html tags
    sentence = re.sub(r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});"," ",sentence)
    
    # Cleaning white spaces
    sentence = re.sub(r"\s+", " ", sentence).strip()

    # Cleaning .com
    sentence = re.sub(r"\.com"," ",sentence)
        
    sentence = sentence.lower()

    #Removing Stop Words
    tokens = ""
    for token in sentence.split():
        if token not in stop_words:
            tokens=tokens+" "+token

    return tokens

def cosine_similarity(embeddings_1,embeddings_2):
    cos_sim = util.cos_sim(embeddings_1,embeddings_2)
    max_values_column = torch.max(cos_sim, dim = 0)
    max_values = max_values_column.values
    cosine_similarity_score = torch.mean(max_values)
    return cosine_similarity_score
    


def final_cover_letter(pdf_path):
    #Extract text from pdf file
    cover_letter = extract_text_from_pdf(pdf_path)

    # Calling the cleaning function
    clean_cover_letter = clean_text(cover_letter)
    clean_keywords = clean_text(keywords)

    #Tokenizing the keywords and cover letter
    tokenize_cover_letter = sent_tokenize(clean_cover_letter)
    tokenize_keywords = sent_tokenize(clean_keywords)

    #Embedding the keywords and cover letter
    embeddings_cover_letter = model.encode(tokenize_cover_letter)
    embeddings_keywords = model.encode(tokenize_keywords)

    #Finding the cosine similarity score
    cosine_similarity_score = cosine_similarity(embeddings_cover_letter,embeddings_keywords)
    similarity = cosine_similarity_score.item()

    return similarity
    
    
    



