from pymongo import MongoClient
import pandas as pd
import math
import matplotlib.pyplot as plt
import numpy as np
import re
import base64
import io
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

client = MongoClient('mongodb://localhost:27017/')
db = client['Project']
plots_collection = db['Plots_Review']

def get_data_from_mongo():
    collection = db['Employee_Review']
    cursor = collection.find({})
    df = pd.DataFrame(list(cursor))
    return df

def read_csv_file(file):
    df = pd.read_csv(file, delimiter=',', nrows=70000)
    return df

def plotPerColumnDistribution(df, nGraphShown):
    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
    nCol = len(numeric_columns)
    plot_ids = []
    for i, column in enumerate(numeric_columns):
        plt.figure(figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
        df[column].hist()
        plt.ylabel('counts')
        plt.xlabel(column)
        plt.title(f'Distribution of {column}')
        plt.tight_layout(pad=1.0)
        # Save the plot as binary data
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plot_data = buffer.getvalue()
        buffer.close()
        # Insert the plot data into MongoDB and get the plot ID
        plot_id = plots_collection.insert_one({'plot_data': plot_data}).inserted_id
        # Append the plot ID to the list
        plot_ids.append(plot_id)
        plt.close()  # Close the current plot to avoid overlapping plots
    return plot_ids



def merge_and_drop_columns(df):
    # Define a function to merge columns
    def merge_columns(row):
        return str(row['summary']) + str(row['pros']) + str(row['cons']) + str(row['advice-to-mgmt'])
    
    # Apply the merge_columns function to create a new 'merged' column
    df['emp_summary'] = df.apply(merge_columns, axis=1)
    
    # Drop the original columns
    df.drop(['summary', 'pros', 'cons', 'advice-to-mgmt'], axis=1, inplace=True)
    
    return df

def preprocess_text(text):
    # Tokenization
    tokens = word_tokenize(text)
    
    # Lowercase conversion
    tokens = [token.lower() for token in tokens]
    
    # Remove numeric values
    tokens = [token for token in tokens if not token.isnumeric()]
    
    # Remove unnecessary data like usernames
    tokens = [re.sub(r'@[^\s]+', '', token) for token in tokens]
    
    # Remove punctuation
    tokens = [token for token in tokens if token.isalpha()]
    
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Stemming
    stemmer = PorterStemmer()
    tokens = [stemmer.stem(token) for token in tokens]
    
    return ' '.join(tokens)

def get_sentiment(text):
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    if sentiment_score > 0:
        sentiment = "Positive"
    elif sentiment_score < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    return sentiment

def preprocess_and_get_sentiment(df, text_column):
    # Preprocess text column
    df['preprocessed_text'] = df[text_column].apply(preprocess_text)
    
    # Get sentiment for preprocessed text
    df['sentiment'] = df['preprocessed_text'].apply(get_sentiment)
    
    return df

def get_plots():
    # Get data from MongoDB
    df = get_data_from_mongo()
    
    # Plot per column distribution
    plot_ids =plotPerColumnDistribution(df, 6)
    return plot_ids


def analyze_sentiments():
    # Get data from MongoDB
    df = get_data_from_mongo()
    
    # Merge and drop columns
    df = merge_and_drop_columns(df)
    
    # Preprocess text and get sentiment
    df = preprocess_and_get_sentiment(df, 'emp_summary')
    
    # Calculate sentiment analysis results
    positive_reviews = df[df['sentiment'] == 'Positive'].shape[0]
    negative_reviews = df[df['sentiment'] == 'Negative'].shape[0]
    neutral_reviews = df[df['sentiment'] == 'Neutral'].shape[0]
    
    return positive_reviews, negative_reviews, neutral_reviews

# if __name__ == "__main__":
#     positive_reviews, negative_reviews, neutral_reviews = analyze_sentiments()
#     print(f"Positive Reviews: {positive_reviews}")
#     print(f"Negative Reviews: {negative_reviews}")
#     print(f"Neutral Reviews: {neutral_reviews}")
