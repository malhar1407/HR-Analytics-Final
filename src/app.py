from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session, make_response, send_file
from pymongo import MongoClient
import os
import subprocess
from resume_parsing import parse_resume
from Cover_Letter import final_cover_letter
from datetime import datetime
import pandas as pd
from io import StringIO
from Employee_Review import get_plots, analyze_sentiments
from Employee_Promotion import generate_graphs, Promotion_predictions
from bson.binary import Binary
from bson import ObjectId
from io import BytesIO
from tempfile import NamedTemporaryFile

import io
import base64

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

def generate_candidate_id():
    # Fetch the latest candidate ID from the database and increment it by 1
    latest_candidate = login_collection_candidate.find_one(sort=[("cand_id", -1)])
    if latest_candidate:
        latest_candidate_id = int(latest_candidate['cand_id'][1:])
        new_candidate_id = 'C' + str(latest_candidate_id + 1).zfill(5)  # Increment and pad with zeros
    else:
        new_candidate_id = 'C00001'  # Initial candidate ID if no candidates exist yet
    return new_candidate_id





app = Flask(__name__)

# Set a secret key
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# MongoDB connection
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client['Project']  # Replace 'Project' with your actual database name
resume_collection = db['resume']  # Collection to store resume data
review_collection = db['Employee_Review']
login_collection = db['Login_Details']  # Collection to store login details
past_employees_collection = db['past_employees']  # Collection to store past employees
login_collection_candidate = db['candidate'] # Collection to store candidates
plots_collection = db['Plots_Review']
promotion_collection = db['Employee_Promotion']
graph_collection = db['Plots_Promotion']
predicted_collection = db['Predicted_Promotions']

rejected_candidate = db['rejected_candidate'] # Collection to store rejected candidates

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
                pdf_name, domain, name, contact_info, email, experience_category, skills, upload_date = parse_resume(resume_file_path)
                cultural_fit = final_cover_letter(cover_letter_file_path)
                
                name = name.upper()
                # Insert resume and cover letter data into MongoDB
                resume_data = {
                    'cand_id':session.get('emp_id'),
                    'resume_name': pdf_name,
                    'resume_content': Binary(resume_content),
                    'cover_letter_name': cover_letter_file.filename,
                    'cover_letter_content': Binary(cover_letter_content),
                    'name': name,
                    'contact_info': contact_info,
                    'email': email,
                    'domain': domain,
                    'experience_category': experience_category,
                    'skills': list(skills),
                    'domain': domain,
                    'cultural_fit': cultural_fit,
                    'upload_date': upload_date
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
    uploaded_documents = resume_collection.find_one({'cand_id': session.get('emp_id')})
    
    if uploaded_documents:
        application_status = 0
        
        if 'status' in uploaded_documents:
            application_status = 3
        elif 'link' in uploaded_documents:
            application_status = 2
        else:
            application_status = 1

        upload_date = uploaded_documents.get('upload_date', None)
        
        # Fetch Meeting Details
        meeting_info = {
            'link': uploaded_documents.get('link'),
            'description': uploaded_documents.get('description'),
            'time': uploaded_documents.get('time')
        }
    else:
        application_status = 0
        upload_date = None
        meeting_info = None

    # Sending the Status if the result is announced
    if application_status == 3:
        status = uploaded_documents.get('status')
        response = make_response(render_template('Candash.html', upload_date=upload_date, meeting_info=meeting_info, application_status=application_status, status=status))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    else:
        response = make_response(render_template('Candash.html', upload_date=upload_date, meeting_info=meeting_info, application_status=application_status))
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

# Route to accept candidates
@app.route('/accept_candidate/<candidate_id>')
def accept_candidate(candidate_id):
    print(candidate_id)
    data = {
        'status': 'Congratulations! You have been accepted. The HR will contact you soon regarding the details of joining.'
    }
    resume_collection.update_one(
        {'cand_id': candidate_id},
        {'$set': data}
    )
    return redirect(url_for('hr_dashboard'))
    

# Route to reject candidates
@app.route('/reject_candidate/<candidate_id>')
def reject_candidate(candidate_id):
    candidate_id = candidate_id
    reason = request.args.get('reason')
    data = {
        'status': 'Sorry! We have decided not to continue forward with you. We will contact you if a position opens up in the future.',
        'reason': reason
    }
    resume_collection.update_one(
        {'cand_id': candidate_id},
        {'$set': data}
    )
    return redirect(url_for('hr_dashboard'))
        

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

def read_csv_file(file):
    df = pd.read_csv(file, delimiter=',', nrows=70000, encoding='latin1')
    return df

def convert_encoding_to_utf8(file):
    # Read the content of the file and decode it from Latin1 to UTF-8
    content = file.read().decode('latin1')
    return content

def get_plot_data(plot_id):
    plot_data = plots_collection.find_one({'_id': plot_id})['plot_data']
    plot_base64 = base64.b64encode(plot_data).decode()
    return plot_base64

@app.route('/upload_HR', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        
        if file:
            try:
                df = read_csv_file(StringIO(convert_encoding_to_utf8(file)))
                # Save data to MongoDB
                records = df.to_dict(orient='records')
                review_collection.insert_many(records)
                return jsonify({'message': 'File uploaded successfully'})
            except Exception as e:
                return jsonify({'error': str(e)})
    
    # If GET request, render the upload.html template
    return render_template('test.html')

@app.route('/analyze', methods=['POST','GET'])
def analyze():
    # Call the analyze_sentiments function from code.py
    plot_ids = get_plots()
    positive_reviews, negative_reviews, neutral_reviews= analyze_sentiments()

    # Get plot data from MongoDB
    plots = [get_plot_data(plot_id) for plot_id in plot_ids]

    # Render the HTML template with analysis results
    return render_template('test1.html', 
                           positive_reviews=positive_reviews, 
                           negative_reviews=negative_reviews, 
                           neutral_reviews=neutral_reviews,
                           plots=plots)


def read_csv(file_promotion):
    data = pd.read_csv(file_promotion)
    return data


def get_plot_ids_from_mongo():
    # Fetch plot IDs from MongoDB
    plot_ids = {}
    plots = graph_collection.find()  # Use 'plots_collection' instead of 'graph_collection'
    for plot in plots:
        plot_id = str(plot.get('_id'))
        plot_ids[plot_id] = plot_id  # Assuming you want to use plot ID as both key and value
    return plot_ids

def get_predictions_from_mongo():
    # Fetch predictions from MongoDB
    predictions = []
    prediction_docs = predicted_collection.find()  # Assuming 'collection' is your MongoDB collection for predictions
    for doc in prediction_docs:
        employee_id = doc.get('employee_id')
        predicted_promotion = doc.get('predicted_promotion')
        predictions.append({'employee_id': employee_id, 'predicted_promotion': predicted_promotion})
    return predictions

@app.route('/upload_HR_AVP', methods=['GET', 'POST'])
def upload_file_avp():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        
        if file:
            try:
                # Read the content of the file
                file_content = file.read().decode('utf-8')
                data = read_csv(StringIO(file_content))
                # Save data to MongoDB
                records = data.to_dict(orient='records')
                promotion_collection.insert_many(records)
                return jsonify({'message': 'File uploaded successfully'})
            except Exception as e:
                return jsonify({'error': str(e)})
    
    # If GET request, render the upload.html template
    return render_template('test3.html')



@app.route('/AVP', methods=['POST','GET'])
def analyze_AVP():
    plot_id = generate_graphs()  # Generate plots and get their IDs
    prediction = Promotion_predictions()
    # Fetch plot IDs and predictions from MongoDB
    plot_ids = get_plot_ids_from_mongo()
    predictions = get_predictions_from_mongo()
    
    # Render a template to display the generated plots and predictions
    return render_template('test2.html', plot_ids=plot_ids, predictions=predictions)

@app.route('/AVP/plot/<plot_id>')
def plot(plot_id):
    plot = graph_collection.find_one({'_id': ObjectId(plot_id)})
    if plot:
        return send_file(io.BytesIO(plot['image']), mimetype='image/png')
    else:
        return 'Plot not found', 404



# Define route for scheduling a meeting
@app.route('/schedule_meeting/<candidate_id>', methods=['GET', 'POST'])
def schedule_meeting(candidate_id):
    print("Candidate ID:", candidate_id)  # Debugging statement
    
    if request.method == 'POST':
        # Get meeting details from the form
        link = request.form['link']
        time = request.form['time']
        description = request.form['description']

        data = {
            'link' : link,
            'description' : description,
            'time' : time
        }

        resume_collection.update_one(
            {'cand_id': candidate_id},
            {'$set': data}
        ) 
       
        return redirect(url_for('hr_dashboard'))
    else:
        # Fetch candidate data from MongoDB based on the candidate ID
        candidate = resume_collection.find_one({'cand_id': candidate_id})
        previous_meeting = {
            'link': candidate.get('link'),
            'description': candidate.get('description'),
            'time': candidate.get('time')
        }
        if candidate:
            return render_template('schedule_meeting.html', candidate=candidate, candidate_id=candidate_id,previous_meeting=previous_meeting)
        else:
            flash('Candidate not found')
            return redirect(url_for('hr_dashboard'))
if __name__ == '__main__':
    streamlit_process = subprocess.Popen(["streamlit", "run", "cygi.py", "--server.enableCORS", "false"])
    app.config['UPLOAD_FOLDER'] = r'D:\HR-Analytics-Final\src\uploads'  # Define upload folder path  # Define upload folder path
    print(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
