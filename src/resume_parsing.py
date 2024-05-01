#IN THE BELOW CODE I AM JUST TAKING THE SKILLS THAT ARE PRESENT IN THE DATASET

import os
import fitz 
import pandas as pd
from datetime import datetime
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

# Preprocess the Skills Data
skills_csv_path = r"D:\HR-Analytics-Final\src\skills2.csv"  # Path to your skills dataset CSV file
skills_df = pd.read_csv(skills_csv_path)
skills_set = set(skills_df["SKILLS"].str.lower())  # Convert to lowercase and create a set for faster lookup
skills_df.drop_duplicates(inplace=True)     # Remove duplicate rows
skills_df.dropna(subset=["SKILLS"], inplace=True)   # Remove empty rows

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(pdf_file)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.lower()  # Convert text to lowercase for case-insensitive matching

# Function for text preprocessing
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});", " ", text)
    text = re.sub(r"\b(?:\d{3}[-.\s]??\d{3}[-.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-.\s]??\d{4}|\d{3}[-.\s]??\d{4})\b", " ", text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", " ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    preprocessed_text = ' '.join(tokens)
    return preprocessed_text

def remove_phone_numbers(text):
    # Regular expression pattern to match phone numbers
    phone_pattern = r'\b(?:\d{3}[-.\s]|\(\d{3}\)\s*)\d{3}[-.\s]?\d{4}\b'
    return re.sub(phone_pattern, '', text)

# Define the TF-IDF vectorizer
tfidf_vectorizer = TfidfVectorizer()

# Define the Multinomial Naive Bayes classifier with the best parameters
best_nb_classifier = MultinomialNB(alpha=0.1)

# Define the pipeline with the TF-IDF vectorizer and Multinomial Naive Bayes classifier
best_nb_pipeline = Pipeline([
    ('tfidf', tfidf_vectorizer),
    ('clf', best_nb_classifier)
])

# Function to extract skills from resume
def extract_skills_from_resume(resume_text):
    extracted_skills = set()

    # Search for skills directly in the resume text
    for skill in skills_set:
        # Check if the entire skill word is present in the resume text
        if re.search(r'\b{}\b'.format(skill), resume_text, re.IGNORECASE):
            # Check if the skill is also in the skills dataset
            if skill.lower() in skills_set:
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

    upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current date-time stamp
    return pdf_name, name, contact_info, email, skills, upload_date


def extract_domain(pdf_path):
    # Load the label encoder used during model training
    label_encoder = joblib.load(r'D:\HR-Analytics-Final\models\label_encoder_final.pkl')  # Load your label encoder object

    # Load the trained model
    loaded_model = joblib.load(r'D:\HR-Analytics-Final\models\best_nb_pipeline.pkl')

    # Extract text from the PDF
    pdf_text = extract_text_from_pdf(pdf_path)

    # Preprocess the extracted text
    preprocessed_pdf_text = preprocess_text(pdf_text)

    # Make prediction using the loaded model
    predicted_domain_number = loaded_model.predict([preprocessed_pdf_text])

    # Convert the predicted domain number to domain name
    predicted_domain_name = label_encoder.inverse_transform(predicted_domain_number)
    predicted_domain = str(predicted_domain_name)
    domain = re.sub(r"[\[\]']", "", predicted_domain)
    return domain

def extract_work_experience(pdf_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    text = ""

    # Extract text from each page
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()

        # Search for work experience section using multiple keywords
        work_experience_keywords = ['Work Experience', 'Employment History', 'Professional Experience', 'Career History', 'Work History', 'Experience', 'Internships']
        work_experience_section = re.search(r'(' + '|'.join(work_experience_keywords) + ')', text, re.IGNORECASE)

        if work_experience_section:
            work_experience_text = text[work_experience_section.start():]
            
            # Replace 'current' or 'present' with the current year
            current_year = datetime.now().year
            work_experience_text = re.sub(r'\b(current|present)\b', str(current_year), work_experience_text, flags=re.IGNORECASE)
            
            # Extract years and convert them to integers
            years = [int(year[-4:]) for year in re.findall(r'\b(?:\d{2}/)?20\d{2}\b', work_experience_text)]
            #print(years)

            # Calculate years of experience
            total_years = max(years) - min(years) if years else 0
            return total_years

    return 0

def bin_years_of_experience(years):
    if years <= 1:
        return "Fresher"
    elif 2 <= years <= 4:
        return "Beginner"
    elif 5 <= years <= 9:
        return "Mid-level"
    else:
        return "Experienced"

# Main function to parse resume and extract information
def parse_resume(pdf_path):
    # Parse resume and extract relevant information
    pdf_name, name, contact_info, email, skills, upload_date = extract_info_from_resume(pdf_path)
    domain = extract_domain(pdf_path)
    years_of_experience = extract_work_experience(pdf_path)
    experience_category = bin_years_of_experience(years_of_experience)
    # Get the current date and time as the upload date
    upload_date = datetime.now()

    # Return all extracted information
    return pdf_name, domain, name, contact_info, email, experience_category, skills, upload_date
