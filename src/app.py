from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session, make_response, send_file
from pymongo import MongoClient
import os
import subprocess
from resume_parsing import parse_resume
from Cover_Letter import final_cover_letter
from datetime import datetime
from bson.binary import Binary
from io import BytesIO
from tempfile import NamedTemporaryFile


def update_user_password(user_id, new_password):
    # MongoDB connection
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client['Project']  # Replace 'Project' with your actual database name
    designation = session.get('designation')
    print('UPDATE PASSWORD DESIGNATION ', designation)

    if designation == 'Candidate':
        login_collection = db['candidate']
        # Update the user's password in the database
        login_collection.update_one({'cand_id': user_id}, {'$set': {'password': new_password}})
        mongo_client.close()  # Close MongoDB connection
    else:
        login_collection = db['Login_Details']
        # Update the user's password in the database
        login_collection.update_one({'emp_id': user_id}, {'$set': {'password': new_password}})
        mongo_client.close()  # Close MongoDB connection
    
    

def get_user_password(user_id):
    # MongoDB connection
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client['Project'] 
    designation = session.get('designation') 
    print('GET PASSWORD DESIGNATION ', designation)
    
    if designation == 'Candidate':
        login_collection = db['candidate']
        user_data = login_collection.find_one({'cand_id' : user_id})
        if user_data:
            user_password = user_data.get('password')
            mongo_client.close()
            return user_password
    else:
        login_collection = db['Login_Details']
        user_data = login_collection.find_one({'emp_id' : user_id})
        if user_data:
            user_password = user_data.get('password')
            mongo_client.close()
            return user_password 
    
def generate_candidate_id():
    # Fetch the latest candidate ID from the database and increment it by 1
    latest_candidate = login_collection_candidate.find_one(sort=[("cand_id", -1)])
    if latest_candidate:
        latest_candidate_id = int(latest_candidate['cand_id'][1:])
        new_candidate_id = 'C' + str(latest_candidate_id + 1).zfill(5)  # Increment and pad with zeros
    else:
        new_candidate_id = 'C00001'  # Initial candidate ID if no candidates exist yet
    return new_candidate_id

# Function to generate a sequential employee ID
def generate_emp_id():
    # Fetch the latest employee ID from the database and increment it by 1
    latest_emp = login_collection.find_one(sort=[("emp_id", -1)])
    if latest_emp:
        latest_emp_id = int(latest_emp['emp_id'])
        new_emp_id = str(latest_emp_id + 1).zfill(5)  # Increment and pad with zeros
    else:
        new_emp_id = '00001'  # Initial employee ID if no employees exist yet
    return new_emp_id



app = Flask(__name__)

# Set a secret key
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client['Project']  # Replace 'Project' with your actual database name
resume_collection = db['resume']  # Collection to store resume data
login_collection = db['Login_Details']  # Collection to store login details
past_employees_collection = db['past_employees']  # Collection to store past employees
login_collection_candidate = db['candidate'] # Collection to store candidates
feedback_collection = db['Feedback']  # Collection to store feedback

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

                # Read the file contents
                with open(resume_file_path, 'rb') as resume_f, open(cover_letter_file_path, 'rb') as cover_letter_f:
                    resume_content = resume_f.read()
                    cover_letter_content = cover_letter_f.read()

                
                # Parse resume and cover letter, and store information in MongoDB
                pdf_name, name, contact_info, email, main_domain, years_experience, skills, upload_date = parse_resume(resume_file_path)
                cultural_fit = final_cover_letter(cover_letter_file_path)
                
                # Insert resume and cover letter data into MongoDB
                resume_data = {
                    'candidate_id':session.get('emp_id'),
                    'resume_name': pdf_name,
                    'resume_content': Binary(resume_content),
                    'cover_letter_name': cover_letter_file.filename,
                    'cover_letter_content': Binary(cover_letter_content),
                    'name': name,
                    'contact_info': contact_info,
                    'email': email,
                    'skills': list(skills),
                    'cultural_fit': cultural_fit,
                    'upload_date': upload_date,
                    'main_domain': main_domain,  
                    'years_experience': years_experience
                }
                resume_collection.insert_one(resume_data)

                # Update or insert candidate data into MongoDB
                candidate_data = {
                    'name': name,
                    'contact_info': contact_info,
                    'email': email,
                    'upload_date': upload_date
                }
                login_collection_candidate.update_one(
                    {'cand_id': session.get('emp_id')},
                    {'$set': candidate_data}
                    
                )

        #return redirect(url_for('candidate_dashboard'))
        return render_template('candash.html', upload_date=upload_date)

        
               

    return redirect(url_for('candidate_dashboard')) 

# Route for candidate dashboard
@app.route('/candidate')
def candidate_dashboard():
    # Check if the candidate has uploaded documents
    uploaded_documents = resume_collection.find_one({'candidate_id': session.get('emp_id')})
    
    if uploaded_documents:
        upload_date = uploaded_documents['upload_date']
    else:
        upload_date = None

    response = make_response(render_template('Candash.html', upload_date=upload_date))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response
#Route for employees login page
@app.route('/login')
def login():
    return render_template('login.html')


# Route to download resume
@app.route('/download_resume/<candidate_id>', methods=['GET'])
def download_resume(candidate_id):
    # Find the resume document in MongoDB based on candidate_id
    resume_document = resume_collection.find_one({'cand_id': candidate_id})
    if resume_document:
        resume_content = resume_document['resume_content']
        resume_filename = resume_document['resume_name']
        
        # Create a BytesIO object to send the file contents
        resume_file = BytesIO(resume_content)
        resume_file.seek(0)
        
        # Return the file as a downloadable attachment
        return send_file(resume_file, download_name=resume_filename, as_attachment=True)
    else:
        return 'Resume not found for employee ID: {}'.format(candidate_id), 404


# Route to download cover letter
@app.route('/download_cover_letter/<candidate_id>', methods=['GET'])
def download_cover_letter(candidate_id):
    # Find the cover letter document in MongoDB based on candidate_id
    cover_letter_document = resume_collection.find_one({'cand_id': candidate_id})
    if cover_letter_document:
        cover_letter_content = cover_letter_document['cover_letter_content']
        cover_letter_filename = cover_letter_document['cover_letter_name']
        
        # Create a BytesIO object to send the file contents
        cover_letter_file = BytesIO(cover_letter_content)
        cover_letter_file.seek(0)
        
        # Return the file as a downloadable attachment
        return send_file(cover_letter_file, as_attachment=True, download_name=cover_letter_filename)
    else:
        return 'Cover letter not found for employee ID: {}'.format(candidate_id), 404

# Route for candidate login page
@app.route('/login_candidate')
def login_candidate():
    return render_template('login_candidate.html')

# Route for employee validation
@app.route('/validate', methods=['POST'])
def validate():
    if request.method == 'POST':
        candidate_id = request.form['candidate-id']
        password = request.form['password']
        
        login_data = login_collection.find_one({'emp_id': candidate_id, 'password': password})
        
        if login_data:
            session['emp_id'] = candidate_id
            session['designation'] = login_data.get('designation')
            session['name'] = login_data.get('name')
            print(session['emp_id'])
            print(session['designation'])
            print(session['name'])
            
            if session['designation'] == 'HR':
                return redirect(url_for('hr_dashboard'))
            elif session['designation'] == 'Candidate':
                return redirect(url_for('candidate_dashboard'))
            elif session['designation'] == 'Admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Login Credentials. Please try again')
        
        return redirect(url_for('login'))
    

# Route for Candidate Validation
@app.route('/validate_candidate', methods=['POST'])
def validate_candidate():
    if request.method == 'POST':
        candidate_id = request.form['candidate-id']
        password = request.form['password']
        
        login_data = login_collection_candidate.find_one({'cand_id': candidate_id, 'password': password})
        
        if login_data:
            session['emp_id']=candidate_id
            session['designation'] = login_data.get('designation')
            session['name'] = login_data.get('name')
            print(session['emp_id'])
            return redirect(url_for('candidate_dashboard'))
        else:
            flash('Invalid Login Credentials. Please try again')
        
        return redirect(url_for('login_candidate'))
    

# Route for logging out
@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session data
    session.clear()
    # Redirect the user to the login page
    return redirect(url_for('login'))
        
# Route for HR dashboard
@app.route('/hr')
def hr_dashboard():
    # Fetch parsed resume data from MongoDB
    resumes = resume_collection.find({})
    return render_template('hrdash.html', resumes=resumes)

# Route for Admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    # Fetch current employees from MongoDB collection 'Login_Details'
    employees = list(db['Login_Details'].find({}))
    return render_template('admindash.html', employees=employees)


# Route for adding employee
@app.route('/admin/dashboard/addemp', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        # Extract employee details from the form
        name = request.form.get('name')
        designation = request.form.get('designation')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = "Admin123@"  # Default password

        # Generate unique employee ID
        emp_id = generate_emp_id()

        # Insert employee details into MongoDB
        employee_data = {
            'emp_id': emp_id,
            'name': name,
            'designation': designation,
            'email': email.lower(),  # Convert email to lowercase
            'phone': phone,
            'password': password,
            'created_at': datetime.now()
        }
        login_collection.insert_one(employee_data)

        return redirect(url_for('admin_dashboard'))

    return render_template('addemp.html', emp_id=generate_emp_id())

# Route for deleting employee
@app.route('/admin/dashboard/delemp', methods=['GET', 'POST'])
def delete_employee():
    if request.method == 'POST':
        emp_id = request.form.get('emp_id')
        employee = login_collection.find_one({'emp_id': emp_id})
        if employee:
            return jsonify({'emp_id': employee['emp_id']})
        else:
            return jsonify({'error': 'Employee not found'})
    else:
        # Fetch current employees from MongoDB collection 'Login_Details'
        employees = list(db['Login_Details'].find({}))
        return render_template('delemp.html', employees=employees)


# Route for handling employee deletion confirmation (AJAX POST request)
@app.route('/admin/dashboard/delete_confirm', methods=['POST'])
def delete_confirm():
    emp_id = request.form.get('emp_id')
    feedback = request.form.get('feedback')

    # Move employee to past employees collection
    employee = login_collection.find_one_and_delete({'emp_id': emp_id})
    if employee:
        # Add the reason for deletion to the employee data
        employee['feedback'] = feedback

        # Insert employee data into past employees collection
        past_employees_collection.insert_one(employee)
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Employee not found'})


@app.route('/change_password', methods=['POST'])
def change_password():
    if request.method == 'POST':
        # Get the submitted form data
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Check if the new password and confirm password match
        if new_password != confirm_password:
            flash('New password and confirm password do not match. Please try again.', 'error')
            return redirect(url_for('change_password_page'))
        
        
        user_id = session.get('emp_id')
        print(user_id)

        # Get current user password
        user_password = get_user_password(user_id)  
        
        # Check if the current password matches the password in the database
        if current_password != user_password:
            flash('Incorrect current password. Please try again.', 'error')
            return redirect(url_for('change_password_page'))
        
        
        update_user_password(user_id, new_password) 
        
        flash('Password updated successfully!', 'success')

        #Get user designation
        designation = session.get('designation')
        if (designation == 'Candidate'):
            return redirect(url_for('candidate_dashboard'))
        elif (designation == 'HR'):
            return redirect(url_for('hr_dashboard'))
        elif(designation == 'Admin'):
            return redirect(url_for('admin_dashboard'))

@app.route('/back', methods=['POST'])
def back():
    user = session.get('designation')

    if user == 'Candidate':
        return redirect(url_for('candidate_dashboard'))
    elif user == 'HR':
        return redirect(url_for('hr_dashboard'))

# Route for rendering the change password page
@app.route('/change_password_page', methods=['POST','GET'])
def change_password_page():
    if request.method == 'POST' or request.method == 'GET':
        return render_template('change_password.html')
    

# Route for rendering the edit employee page
@app.route('/admin/dashboard/editemp', methods=['GET'])
def edit_employee_page():
    return render_template('editemp.html', employee=None)

# Route for handling employee details and saving changes
@app.route('/admin/dashboard/edit_employee', methods=['POST'])
def edit_employee():
    if request.method == 'POST':
        emp_id = request.form.get('emp_id')
        # Fetch employee details from the database based on emp_id
        employee = login_collection.find_one({'emp_id': emp_id})
        if employee:
            return render_template('editemp.html', employee=employee)
        else:
            flash('Employee not found')
            # Render the editemp.html template with the flashed message
            return render_template('editemp.html', flash_message='Employee not found')
    else:
        return render_template('editemp.html', employee=None)


# Route for saving employee changes
@app.route('/admin/dashboard/save_employee_changes', methods=['POST'])
def save_employee_changes():
    if request.method == 'POST':
        # Get the submitted form data
        emp_id = request.form.get('emp_id')
        name = request.form.get('name')
        designation = request.form.get('designation')
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        # Update employee details in the database
        result = login_collection.update_one({'emp_id': emp_id}, {'$set': {'name': name, 'designation': designation, 'email': email, 'phone': phone, 'updated_at': datetime.now()}})
        
        if result.modified_count > 0:
            flash('Changes have been saved successfully', 'success')
        else:
            flash('Failed to save changes. Employee not found or no changes made.', 'error')
        
        return redirect(url_for('admin_dashboard'))
    


# Route for rendering addcand.html and handling candidate addition
@app.route('/admin/dashboard/addcand')
def add_candidate_page():
    candidate_id = generate_candidate_id()  # Generate candidate ID
    return render_template('addcand.html', candidate_id=candidate_id)

from flask import jsonify

# Route for adding candidate
@app.route('/admin/dashboard/add_candidate', methods=['POST'])
def add_candidate():
    if request.method == 'POST':
        # Generate candidate ID
        candidate_id = generate_candidate_id()

        # Add candidate to MongoDB
        candidate_data = {
            'cand_id': candidate_id,
            'designation': 'Candidate',
            'password': 'Admin123@'
        }
        login_collection_candidate.insert_one(candidate_data)

        # Return a JSON response indicating success
        return jsonify({'success': True})

    # Handle other HTTP methods or invalid requests
    return jsonify({'error': 'Invalid request'}), 400

@app.route('/admin/dashboard/edform')
def edit_form():
    # Fetch existing questions from the Feedback collection
    existing_questions = feedback_collection.find_one({}, {'_id': 0})
    return render_template('editform.html', existing_questions=existing_questions)

@app.route('/admin/dashboard/save_questions', methods=['POST'])
def save_questions():
    if request.method == 'POST':
        # Get the submitted form data
        question1 = request.form['question1']
        question2 = request.form['question2']
        question3 = request.form['question3']
        question4 = request.form['question4']
        
        # Update the existing entry in the database
        feedback_collection.update_one({}, {'$set': {'question1': question1, 'question2': question2, 'question3': question3, 'question4': question4, 'timestamp': datetime.now()}})
        
        # Assuming you have saved the questions successfully, display a success message
        flash('Questions have been saved successfully', 'success')
        
        # Redirect the admin back to the admin dashboard
        return redirect(url_for('admin_dashboard'))
    
@app.route('/empfeed', methods=['GET', 'POST'])
def empfeed():
    if request.method == 'POST':
        # Handle form submission
        feedback = {}
        for key, value in request.form.items():
            feedback[key] = value
        
        # Save feedback to MongoDB
        feedback_collection.insert_one(feedback)
        
        # Optionally, redirect to a thank you page
        return render_template('thank_you.html')
    else:
        # Retrieve questions from MongoDB
        questions = feedback_collection.find_one()  # Assuming there's only one document with questions
        
        return render_template('empfeed.html', questions=questions)

if __name__ == '__main__':
    # streamlit_process = subprocess.Popen(["streamlit", "run", "cygi.py", "--server.enableCORS", "false"])
    app.config['UPLOAD_FOLDER'] = r'D:\HR-Analytics-Final\src\uploads'  # Define upload folder path  # Define upload folder path
    print(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
