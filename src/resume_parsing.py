#IN THE BELOW CODE I AM JUST TAKING THE SKILLS THAT ARE PRESENT IN THE DATASET

import os
import fitz  # PyMuPDF # type: ignore
import pandas as pd
from datetime import datetime
import re

# Preprocess the Skills Data
skills_csv_path = r"D:\HR-Analytics-Final\resume_parsing\skills2.csv"  # Path to your skills dataset CSV file
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

# Main function to parse resume and extract information
def parse_resume(pdf_path):
    # Parse resume and extract relevant information
    pdf_name, name, contact_info, email, skills, upload_date = extract_info_from_resume(pdf_path)

    # Get the current date and time as the upload date
    upload_date = datetime.now()

    # Return all extracted information
    return pdf_name, name, contact_info, email, skills, upload_date

