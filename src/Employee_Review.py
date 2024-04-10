from mpl_toolkits.mplot3d import Axes3D
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt # plotting
import numpy as np # linear algebra
import os # accessing directory structure
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import math
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.utils import shuffle
import joblib

def read_csv_file(file_path):
    df = pd.read_csv(file_path, delimiter=',', nrows=70000, encoding='latin1')
    return df

def plotPerColumnDistribution(df, nGraphShown, nGraphPerRow):
    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
    nCol = len(numeric_columns)
    columnNames = numeric_columns
    nGraphRow = (nCol + nGraphPerRow - 1) // nGraphPerRow  # Integer division using //
    plt.figure(num=None, figsize=(6 * nGraphPerRow, 8 * nGraphRow), dpi=80, facecolor='w', edgecolor='k')
    nGraphShown = min(nCol, math.ceil(nGraphShown))  # Ensure nGraphShown is a positive integer
    for i in range(nGraphShown):
        plt.subplot(nGraphRow, nGraphPerRow, i + 1)
        columnDf = df[numeric_columns[i]]
        columnDf.hist()
        plt.ylabel('counts')
        plt.xticks(rotation=90)
        plt.title(f'{columnNames[i]} (column {i})')
    plt.tight_layout(pad=1.0, w_pad=1.0, h_pad=1.0)
    plt.show()
    #return plotPerColumnDistribution(df, 6, 3)

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
    
    # Spelling correction
   # corrected_tokens = []
    #for token in tokens:
        #corrected_tokens.append(str(TextBlob(token).correct()))
    
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

def analyze_sentiments(file_path, text_column):
    # Read the data from file
    df = read_csv_file(file_path)
    
    # Call plotPerColumnDistribution function
    plotPerColumnDistribution(df, 6, 3)
    
    # Merge and drop columns
    df = merge_and_drop_columns(df)
    
    # Call preprocess_and_get_sentiment function
    df = preprocess_and_get_sentiment(df, text_column)
    
    return df

if __name__ == "__main__":
    # Specify the file path and text column name
    file_path = r"C:\Users\parth.parikh1\Downloads\test.csv"
    text_column = "emp_summary"
    
    # Call the main function
    df = analyze_sentiments(file_path, text_column)
    
    # Print the DataFrame with sentiment values
    print(df['sentiment'])




