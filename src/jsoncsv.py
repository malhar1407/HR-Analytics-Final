import pandas as pd
import pymongo
import pickle

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Project"]
collection = db["Feedback_answers"]

# Retrieve data from MongoDB
data = list(collection.find())

# Convert JSON data to DataFrame
df = pd.DataFrame(data)

# Preprocess DataFrame
# Drop the "_id" column
df.drop("_id", "emp_id", "department", axis=1, inplace=True)

# Rename columns
df.rename(columns={'question4': 'summary', 'question1': 'pros', 'question2': 'cons', 'question3': 'advice-to-mgmt', 'question5': 'overall-ratings', 'question6': 'work-balance-stars', 'question7': 'culture-values-stars', 'question8': 'carrer-opportunities-stars', 'question9': 'comp-benefit-stars', 'question10': 'senior-mangemnet-stars' }, inplace=True)

# Rearrange columns
df = df[['summary', 'pros', 'cons', 'advice-to-mgmt', 'overall-ratings', 'work-balance-stars', 'culture-values-stars', 'carrer-opportunities-stars', 'comp-benefit-stars', 'senior-mangemnet-stars']]


