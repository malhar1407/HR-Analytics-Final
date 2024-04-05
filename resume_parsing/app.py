from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient # type: ignore
import os
from resume_parsing import parse_resume
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client['Project']  # Replace 'Project' with your actual database name
resume_collection = db['resume']  # Collection to store resume data

# Route for uploading resumes
@app.route('/upload', methods=['GET', 'POST'])
def upload_resumes():
    if request.method == 'POST':
        # Get the list of files uploaded
        uploaded_files = request.files.getlist('resumes')

        # Process each uploaded file
        for file in uploaded_files:
            if file.filename != '':
                # Save the uploaded file to the uploads directory
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)

                # Parse the resume and store information in MongoDB
                pdf_name, name, contact_info, email, skills, upload_date = parse_resume(file_path)
                upload_date = datetime.now()
                resume_data = {
                    'pdf_name': pdf_name,
                    'name': name,
                    'contact_info': contact_info,
                    'email': email,
                    'skills': list(skills),
                    'upload_date': upload_date
                }
                resume_collection.insert_one(resume_data)

        return redirect(url_for('candidate_dashboard'))

# Route for candidate dashboard
@app.route('/candidate')
def candidate_dashboard():
    return render_template('Candash.html')

# Route for HR dashboard
@app.route('/hr')
def hr_dashboard():
    # Fetch parsed resume data from MongoDB
    resumes = resume_collection.find({})
    return render_template('hrdash.html', resumes=resumes)

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = r'D:\HR-Analytics-Final\resume_parsing\uploads'  # Define upload folder path
    app.run(debug=True)
