from pymongo import MongoClient
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer
import io

client = MongoClient('mongodb://localhost:27017/')
db = client['Project']
plots_collection = db['Plots_Promotion']
collection = db['Employee_Promotion']

def get_data_from_mongo():
    collection = db['Employee_Promotion']
    cursor = collection.find({})
    data = pd.DataFrame(list(cursor))
    return data

def read_csv(file_promotion):
    data = pd.read_csv(file_promotion)
    return data

def rename_columns(data):
    cols = ['_id','employee_id', 'department', 'region', 'education', 'gender',
            'recruitment_channel', 'no_of_trainings', 'age', 'previous_year_rating',
            'length_of_service', 'KPIs_met', 'awards_won',
            'avg_training_score']
    data.columns = cols
    return data

def preprocess_csv(data):
    # Fill missing values in 'education' column with mode value corresponding to each department
    depts = data.department.unique()
    for dept in depts:
        edu_mode = data[data.department == dept].education.mode()[0]
        data.loc[data.department == dept, 'education'] = data.loc[data.department == dept, 'education'].fillna(edu_mode)
    # Create 'performance' column
    data['performance'] = data[['KPIs_met', 'awards_won']].any(axis=1, skipna=False)
    # Create 'total_score' column
    data['total_score'] = (data.no_of_trainings * data.avg_training_score)
    return data

def data_binning(data):
        
        # Binning for 'total_score_label'
        data['total_score_label'] = pd.cut(data.total_score, bins=[0, 65, 145, 1000], labels=['Low', 'Mediocre', 'High']).astype(str)

        # Binning for 'service_catg'
        data['service_catg'] = pd.cut(data.length_of_service, bins=[0, 2, 7, 10, 37],
                                     labels=['New', 'Established', 'Experienced', 'Veteran']).astype(str)
        
        # Binning for 'age_label'
        data['age_label'] = pd.cut(data.age, bins=[0, 25, 40, 50, 100], labels=['Young', 'Middle', 'Senior', 'Elder']).astype(str)
        
        # Label encoding for 'rating_label'
        def decode(val):
            if val == 0:
                return 'New'
            elif val == 1:
                return 'Minimum'
            elif val == 2:
                return 'Fair'
            elif val == 3:
                return 'Improving'
            elif val == 4:
                return 'Good'
            else:
                return 'Very good'

        data['rating_label'] = data.previous_year_rating.apply(decode)
        
        return data

def plot_graphs(data):
    
    plot_ids = {}  # Dictionary to store plot IDs

    # Check if the plots collection is empty
    if plots_collection.count_documents({}) > 0:
        # If the collection is not empty, delete all documents
        plots_collection.delete_many({})
    
    # Plot count of awards won
    awards_won_plot = plt.figure()
    sns.countplot(data=data, x='awards_won')
    plt.title('Count of Awards Won')
    plt.xlabel('Awards Won')
    plt.ylabel('Count')
    plt.tight_layout()
    awards_won_bytes = io.BytesIO()
    plt.savefig(awards_won_bytes, format='png')
    plt.close(awards_won_plot)
    # Insert plot into MongoDB and store its ID
    awards_won_id = plots_collection.insert_one({'image': awards_won_bytes.getvalue()}).inserted_id
    plot_ids['awards_won'] = str(awards_won_id)

    # Plot count of KPIs met
    kpis_met_plot = plt.figure()
    sns.countplot(data=data, x='KPIs_met')
    plt.title('Count of KPIs Met')
    plt.xlabel('KPIs Met')
    plt.ylabel('Count')
    plt.tight_layout()
    kpis_met_bytes = io.BytesIO()
    plt.savefig(kpis_met_bytes, format='png')
    plt.close(kpis_met_plot)
    # Insert plot into MongoDB and store its ID
    kpis_met_id = plots_collection.insert_one({'image': kpis_met_bytes.getvalue()}).inserted_id
    plot_ids['kpis_met'] = str(kpis_met_id)

    # Plot count data from binning
    for column in ['total_score_label', 'service_catg', 'rating_label']:
        plot = plt.figure()
        sns.countplot(data=data, x=column, order=data[column].value_counts().index)
        plt.ylabel('Count')
        plt.xlabel(column.replace('_', ' '))
        plt.tight_layout()
        plot_bytes = io.BytesIO()
        plt.savefig(plot_bytes, format='png')
        plt.close(plot)
        # Insert plot into MongoDB and store its ID
        column_id = plots_collection.insert_one({'image': plot_bytes.getvalue()}).inserted_id
        plot_ids[column] = str(column_id)

    # Plot department-wise promotion
    department_plot = plt.figure()
    sns.set_style('whitegrid')
    data.department.value_counts().plot.bar(color='#ff9933', align='edge')
    plt.title('Department-wise Employees')
    plt.ylabel('Number of Employees')
    plt.xlabel('Department')
    plt.tight_layout()
    department_promotion_bytes = io.BytesIO()
    plt.savefig(department_promotion_bytes, format='png')
    plt.close(department_plot)
    # Insert plot into MongoDB and store its ID
    department_promotion_id = plots_collection.insert_one({'image': department_promotion_bytes.getvalue()}).inserted_id
    plot_ids['department_promotion'] = str(department_promotion_id)
    
    return plot_ids


def remove_columns(data):
    rm_cols = ['department', 'region','education', 'gender',
    'recruitment_channel','KPIs_met','awards_won','total_score_label',
    'service_catg','age_label','rating_label']

    data.drop(rm_cols,axis=1,inplace=True)
    return data


def promotion_predictions(file_promotion):
    # Drop rows with missing values
    # file_promotion.dropna(inplace=True)
    result = []
    
    # Load the saved model
    model = joblib.load("D:\HR-Analytics-Final\models\employee_promotion.pkl")

    # Convert performance to binary
    file_promotion['performance'] = file_promotion['performance'].apply(lambda x: 1 if x else 0)
    
    # Separate features (X) and employee_id
    employee_ids = file_promotion['employee_id']
    X = file_promotion.drop(['_id','employee_id'], axis=1)  # Assuming 'employee_id' is not a feature
    
    # Handle missing values using SimpleImputer
    imputer = SimpleImputer(strategy='mean')
    X_imputed = imputer.fit_transform(X)
    
    # Scale the features
    scaler = MinMaxScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X_imputed), columns=X.columns)
    
    # Make predictions
    predictions = model.predict(X_scaled)

    for i in predictions:
        if i == 1:
            result.append("Promoted")
        else:
            result.append("Not Promoted")

    # Create a DataFrame with employee_id and predicted_promotion
    predictions_df = pd.DataFrame({'employee_id': employee_ids, 'predicted_promotion': result})

    
    return predictions_df

def save_to_mongodb(predictions_df):
    # Convert DataFrame to dictionary
    documents = predictions_df.to_dict(orient='records')

    # Connect to the target collection
    target_collection = db['Predicted_Promotions']  # Assuming 'Predicted_Promotions' is the target collection

    # Update documents in the target collection
    for doc in documents:
        # Create a new document with only employee_id and predicted_promotion fields
        new_doc = {'employee_id': doc['employee_id'], 'predicted_promotion': doc['predicted_promotion']}
        # Insert or update the document in the target collection
        target_collection.update_one({'employee_id': doc['employee_id']}, {'$set': new_doc}, upsert=True)


    #client.close()


def generate_graphs():
    data = get_data_from_mongo()
    # Perform necessary data preprocessing
    renamed_csv = rename_columns(data)
    preprocessed_csv = preprocess_csv(renamed_csv)
    binned_csv = data_binning(preprocessed_csv)
    # Generate plots
    plots = plot_graphs(binned_csv)
    return plots

def Promotion_predictions():
    data = get_data_from_mongo()

    # Perform necessary data preprocessing
    renamed_csv = rename_columns(data)
    preprocessed_csv = preprocess_csv(renamed_csv)
    binned_csv = data_binning(preprocessed_csv)
    prediction_csv = remove_columns(binned_csv)

    # Perform promotion predictions
    predictions = promotion_predictions(prediction_csv)
    save_to_mongodb(predictions)
    return predictions