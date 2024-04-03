# import os
# import fitz  # PyMuPDF
# import pandas as pd
# from itertools import combinations
# from gensim.models import Word2Vec
# from gensim.utils import simple_preprocess
# from gensim.models.callbacks import CallbackAny2Vec
# from datetime import datetime
# import re

# # Preprocess the Skills Data
# skills_csv_path = r"C:\Users\kahan.jash\Desktop\check\skills2.csv"  # Path to your skills dataset CSV file
# skills_df = pd.read_csv(skills_csv_path)
# skills_set = set(skills_df["SKILLS"].str.lower())  # Convert to lowercase and create a set for faster lookup
# skills_df.drop_duplicates(inplace=True)     # Remove duplicate rows
# skills_df.dropna(subset=["SKILLS"], inplace=True)   # Remove empty rows

# # Train the Word2Vec Model
# class EpochLogger(CallbackAny2Vec):
#     def __init__(self):
#         self.epoch = 0

#     def on_epoch_end(self, model):
#         self.epoch += 1

# epoch_logger = EpochLogger()

# word2vec_model = Word2Vec(
#     sentences=[simple_preprocess(skill) for skill in skills_df["SKILLS"]],
#     vector_size=300,  # Dimensionality of the word vectors
#     window=10,        # Maximum distance between the current and predicted word
#     min_count=1,      # Ignore words with a frequency lower than this
#     workers=4,        # Number of worker threads for training
#     sg=1,             # Use Skip-gram model
#     callbacks=[epoch_logger]
# )

# # Function to extract text from PDF
# def extract_text_from_pdf(pdf_file):
#     doc = fitz.open(pdf_file)
#     text = ""
#     for page in doc:
#         text += page.get_text()
#     return text.lower()  # Convert text to lowercase for case-insensitive matching

# # Function to generate bi-grams and tri-grams
# def generate_ngrams(words):
#     ngrams = []
#     for i in range(2, 4):  # Considering bi-grams and tri-grams
#         ngrams.extend([' '.join(combo) for combo in combinations(words.split(), i)])
#     return ngrams

# # Function to extract skills from resume using Word2Vec model
# def extract_skills_with_word2vec(resume_text):
#     extracted_skills = set()
#     tokens = simple_preprocess(resume_text)
#     for token in tokens:
#         if token in word2vec_model.wv.key_to_index:
#             similar_skills = word2vec_model.wv.most_similar(token, topn=1)
#             for skill, _ in similar_skills:
#                 if skill.lower() in skills_set:
#                     extracted_skills.add(skill.lower())
#     return extracted_skills

# # Function to extract skills from resume
# def extract_skills_from_resume(resume_text):
#     extracted_skills = set()

#     # Using Word2Vec model for skill extraction
#     extracted_skills.update(extract_skills_with_word2vec(resume_text))

#     # Search for skills directly in the resume text
#     for skill in skills_set:
#         # Check if the entire skill word is present in the resume text
#         if re.search(r'\b{}\b'.format(skill), resume_text, re.IGNORECASE):
#             extracted_skills.add(skill.lower())

#     return extracted_skills

# # Function to extract text, name, contact info, email, and skills from PDF
# def extract_info_from_resume(pdf_path):
#     pdf_name = os.path.basename(pdf_path)  # Extract the PDF file name
#     resume_text = extract_text_from_pdf(pdf_path)

#     # Extract skills from resume text
#     skills = extract_skills_from_resume(resume_text)

#     # Ensure that skills are only displayed if they are present in the PDF
#     skills.intersection_update(skills_set)

#     # Extract name
#     name_match = re.match(r'^\s*(\S+\s+\S+)', resume_text)
#     name = name_match.group(1) if name_match else None

#     # Extract contact info
#     contact_match = re.search(r'(\b\d{10}\b|\b\d{5} \d{5}\b)', resume_text)
#     contact_info = contact_match.group(0) if contact_match else None

#     # Extract email address
#     email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
#     email = email_match.group(0) if email_match else None

#     # Search for the occurrence of the words "skill" or "skills"
#     skill_index = resume_text.lower().find("skill")
#     if skill_index == -1:
#         skill_index = resume_text.lower().find("skills")
#     if skill_index != -1:
#         # Extract surrounding text (500 characters) after the occurrence of "skill" or "skills"
#         surrounding_text = resume_text[skill_index:skill_index + 500]
#         # Extract skills from the surrounding text
#         skills.update(extract_skills_from_resume(surrounding_text))

#     upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current date-time stamp
#     return pdf_name, name, contact_info, email, skills, upload_date

# # Main function to parse resume and extract information
# def parse_resume(pdf_path):
#     # Parse resume and extract relevant information
#     pdf_name, name, contact_info, email, skills, upload_date = extract_info_from_resume(pdf_path)

#     # Get the current date and time as the upload date
#     upload_date = datetime.now()

#     # Return all extracted information
#     return pdf_name, name, contact_info, email, skills, upload_date





import os
import fitz  # PyMuPDF
import pandas as pd
from itertools import combinations
from gensim.models import Word2Vec
from gensim.utils import simple_preprocess
from gensim.models.callbacks import CallbackAny2Vec
from datetime import datetime
import re

# Preprocess the Skills Data
skills_csv_path = r"C:\Users\kahan.jash\Desktop\check\skills2.csv"  # Path to your skills dataset CSV file
skills_df = pd.read_csv(skills_csv_path)
skills_set = set(skills_df["SKILLS"].str.lower())  # Convert to lowercase and create a set for faster lookup
skills_df.drop_duplicates(inplace=True)     # Remove duplicate rows
skills_df.dropna(subset=["SKILLS"], inplace=True)   # Remove empty rows

# Train the Word2Vec Model
class EpochLogger(CallbackAny2Vec):
    def __init__(self):
        self.epoch = 0

    def on_epoch_end(self, model):
        self.epoch += 1

epoch_logger = EpochLogger()

word2vec_model = Word2Vec(
    sentences=[simple_preprocess(skill) for skill in skills_df["SKILLS"]],
    vector_size=300,  # Dimensionality of the word vectors
    window=10,        # Maximum distance between the current and predicted word
    min_count=1,      # Ignore words with a frequency lower than this
    workers=4,        # Number of worker threads for training
    sg=1,             # Use Skip-gram model
    callbacks=[epoch_logger]
)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.lower()  # Convert text to lowercase for case-insensitive matching

# Function to extract skills from resume using Word2Vec model
def extract_skills_with_word2vec(resume_text):
    extracted_skills = set()
    tokens = simple_preprocess(resume_text)
    for token in tokens:
        if token in word2vec_model.wv.key_to_index:
            similar_skills = word2vec_model.wv.most_similar(token, topn=1)
            for skill, _ in similar_skills:
                if skill.lower() in skills_set:
                    extracted_skills.add(skill.lower())
    return extracted_skills

# Function to extract skills from resume
def extract_skills_from_resume(resume_text):
    extracted_skills = set()

    # Using Word2Vec model for skill extraction
    extracted_skills.update(extract_skills_with_word2vec(resume_text))

    # Search for skills directly in the resume text
    for skill in skills_set:
        # Check if the entire skill word is present in the resume text
        if re.search(r'\b{}\b'.format(skill), resume_text, re.IGNORECASE):
            extracted_skills.add(skill.lower())

    return extracted_skills

# Function to extract text, name, contact info, email, and skills from PDF
def extract_info_from_resume(pdf_path):
    pdf_name = os.path.basename(pdf_path)  # Extract the PDF file name
    resume_text = extract_text_from_pdf(pdf_path)

    # Extract skills from resume text
    skills = extract_skills_from_resume(resume_text)

    # Ensure that skills are only displayed if they are present in the PDF
    skills.intersection_update(skills_set)

    # Extract name
    name_match = re.match(r'^\s*(\S+\s+\S+)', resume_text)
    name = name_match.group(1) if name_match else None

    # Extract contact info
    contact_match = re.search(r'(\b\d{10}\b|\b\d{5} \d{5}\b)', resume_text)
    contact_info = contact_match.group(0) if contact_match else None

    # Extract email address
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
    email = email_match.group(0) if email_match else None

    # Search for the occurrence of the words "skill" or "skills"
    skill_index = resume_text.lower().find("skill")
    if skill_index == -1:
        skill_index = resume_text.lower().find("skills")
    if skill_index != -1:
        # Extract surrounding text (500 characters) after the occurrence of "skill" or "skills"
        surrounding_text = resume_text[skill_index:skill_index + 500]
        # Extract skills from the surrounding text
        skills.update(extract_skills_from_resume(surrounding_text))

    upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current date-time stamp
    return pdf_name, name, contact_info, email, skills, upload_date

# Main function to parse resume and extract information
def parse_resume(pdf_path):
    # Parse resume and extract relevant information
    pdf_name, name, contact_info, email, skills, upload_date = extract_info_from_resume(pdf_path)

    # Get the current date and time as the upload date
    upload_date = datetime.now()

    # Return all extracted information
    return pdf_name, name, contact_info, email, skills, upload_date
