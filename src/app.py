from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
import os
from resume_parsing import parse_resume
from Cover_Letter import final_cover_letter
from datetime import datetime

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client['Project']  # Replace 'Project' with your actual database name
resume_collection = db['resume']  # Collection to store resume data
login_collection = db['Login_Details'] # Collection to store login data

# Route for uploading resumes
@app.route('/upload', methods=['POST'])
def upload_files():
    if request.method == 'POST':
        # Get the list of uploaded resumes and cover letters
        uploaded_resumes = request.files.getlist('resumes')
        uploaded_cover_letters = request.files.getlist('cover_letter')

        # Process uploaded resumes and cover letters
        for resume_file, cover_letter_file in zip(uploaded_resumes, uploaded_cover_letters):
            if resume_file.filename != '' and cover_letter_file.filename != '':
                # Save resume file
                resume_file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
                resume_file.save(resume_file_path)
                # Save cover letter file
                cover_letter_file_path = os.path.join(app.config['UPLOAD_FOLDER'], cover_letter_file.filename)
                cover_letter_file.save(cover_letter_file_path)
                
                # Parse resume and cover letter, and store information in MongoDB
                pdf_name, name, contact_info, email, skills, upload_date = parse_resume(resume_file_path)
                cultural_fit = final_cover_letter(cover_letter_file_path)
                
                # Insert resume and cover letter data into MongoDB
                resume_data = {
                    'pdf_name': pdf_name,
                    'name': name,
                    'contact_info': contact_info,
                    'email': email,
                    'skills': list(skills),
                    'cultural_fit': cultural_fit,
                    'upload_date': upload_date
                }
                resume_collection.insert_one(resume_data)


               

        return redirect(url_for('candidate_dashboard'))


# Route for candidate dashboard
@app.route('/candidate')
def candidate_dashboard():
    return render_template('Candash.html')

#Route for login page
@app.route('/login')
def login():
    return render_template('login.html')



@app.route('/validate', methods=['POST'])
def validate():
    print('Reached validation')
    if request.method == 'POST':
        candidate_id = int(request.form['candidate-id'])
        password = request.form['password']

        print(type(candidate_id))
        print(password)
        login_data = login_collection.find_one({'id': candidate_id, 'Password': password})
        print(login_data)

        if login_data:
            designation = login_data.get('Designation')
            print(designation)

            if(designation == 'HR'):
                return redirect(url_for('hr_dashboard'))
            elif(designation == 'Candidate'):
                return redirect(url_for('candidate_dashboard'))
        else:
            flash('Invalid Login Credentials. Please try again')
        
        return redirect(url_for('login'))
        


# Route for HR dashboard
@app.route('/hr')
def hr_dashboard():
    # Fetch parsed resume data from MongoDB
    resumes = resume_collection.find({})
    return render_template('hrdash.html', resumes=resumes)

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = r'D:\HR-Analytics-Final\src\uploads'  # Define upload folder path
    app.run(debug=True)
