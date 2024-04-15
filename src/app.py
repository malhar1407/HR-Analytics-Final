from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response, send_file, jsonify
from pymongo import MongoClient
import os
import subprocess
from resume_parsing import parse_resume
from Cover_Letter import final_cover_letter
from datetime import datetime
from bson.binary import Binary
from io import BytesIO

def update_user_password(user_id, new_password):
    # MongoDB connection
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client['Project']  # Replace 'Project' with your actual database name
    login_collection = db['Login_Details'] # Collection to store login data
    
    # Update the user's password in the database
    login_collection.update_one({'id': user_id}, {'$set': {'Password': new_password}})
    mongo_client.close()  # Close MongoDB connection

def get_user_password(user_id):
    # MongoDB connection
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client['Project']  
    login_collection = db['Login_Details'] 
    
    # Query the database to get the user's password
    user_data = login_collection.find_one({'id': user_id})
    if user_data:
        user_password = user_data.get('Password')
        mongo_client.close()  # Close MongoDB connection
        return user_password
    else:
        mongo_client.close()  # Close MongoDB connection
        return None

def generate_emp_id():
    # MongoDB connection
    mongo_client = MongoClient("mongodb://localhost:27017")
    db = mongo_client['Project']  
    login_collection = db['Login_Details'] 

    # Get the count of existing employees
    count = login_collection.count_documents({})

    # Generate a new employee ID with 5 digits
    emp_id = str(count + 1).zfill(5)
    mongo_client.close()  # Close MongoDB connection

    return emp_id

app = Flask(__name__)
# Set a secret key
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client['Project']  # Replace 'Project' with your actual database name
resume_collection = db['resume']  # Collection to store resume data
login_collection = db['Login_Details']  # Collection to store login details
past_employees_collection = db['past_employees']  # Collection to store past employees


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
                pdf_name, name, contact_info, email, skills, upload_date = parse_resume(resume_file_path)
                cultural_fit = final_cover_letter(cover_letter_file_path)
                
                # Insert resume and cover letter data into MongoDB
                resume_data = {
                    'emp_id': session.get('emp_id'),
                    'resume_name': pdf_name,
                    'resume_content': Binary(resume_content),
                    'cover_letter_name': cover_letter_file.filename,
                    'cover_letter_content': Binary(cover_letter_content),
                    'name': name,
                    'contact_info': contact_info,
                    'email': email,
                    'skills': list(skills),
                    'cultural_fit': cultural_fit,
                    'upload_date': upload_date
                }
                resume_collection.insert_one(resume_data)

        return redirect(url_for('candidate_dashboard'))

               

        return redirect(url_for('candidate_dashboard')) 


# Route for candidate dashboard
@app.route('/candidate')
def candidate_dashboard():
    response = make_response(render_template('Candash.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

#Route for login page
@app.route('/login')
def login():
    return render_template('login.html')


# Route to download resume
@app.route('/download_resume/<emp_id>', methods=['GET'])
def download_resume(emp_id):
    # Find the resume document in MongoDB based on emp_id
    resume_document = resume_collection.find_one({'emp_id': emp_id})
    if resume_document:
        resume_content = resume_document['resume_content']
        resume_filename = resume_document['resume_name']
        
        # Create a BytesIO object to send the file contents
        resume_file = BytesIO(resume_content)
        resume_file.seek(0)
        
        # Return the file as a downloadable attachment
        return send_file(resume_file, attachment_filename=resume_filename, as_attachment=True)
    else:
        return 'Resume not found for employee ID: {}'.format(emp_id), 404


# Route to download cover letter
@app.route('/download_cover_letter/<emp_id>', methods=['GET'])
def download_cover_letter(emp_id):
    # Find the cover letter document in MongoDB based on employee_id
    cover_letter_document = resume_collection.find_one({'emp_id': emp_id})
    if cover_letter_document:
        cover_letter_content = cover_letter_document['cover_letter_content']
        cover_letter_filename = cover_letter_document['cover_letter_name']
        
        # Create a BytesIO object to send the file contents
        cover_letter_file = BytesIO(cover_letter_content)
        cover_letter_file.seek(0)
        
        # Return the file as a downloadable attachment
        return send_file(cover_letter_file, attachment_filename=cover_letter_filename, as_attachment=True)
    else:
        return 'Cover letter not found for employee ID: {}'.format(emp_id), 404


@app.route('/validate', methods=['POST'])
def validate():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        password = request.form['password']
        print(type(emp_id))
        print(type(password))
        login_data = login_collection.find_one({'emp_id': emp_id, 'password': password})
        print(login_data)
        if login_data:
            session['emp_id'] = emp_id
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
        
        # Get the user's current password from the database (you need to implement this)
        # For demonstration purposes, I'll assume you have a function called `get_user_password`
        user_id = session.get('emp_id')
        user_password = get_user_password(user_id)  # Implement this function
        
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
            return redirect(url_for('admin_dashboard'))

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

if __name__ == '__main__':
    streamlit_process = subprocess.Popen(["streamlit", "run", "cygi.py", "--server.enableCORS", "false"])
    app.config['UPLOAD_FOLDER'] = r'D:\HR-Analytics-Final\src\uploads'  # Define upload folder path
    app.run(debug=True)
