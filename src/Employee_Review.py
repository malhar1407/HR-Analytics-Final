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

# def get_data_from_mongo():
#     collection = db['Employee_Review']
#     cursor = collection.find({})
#     df = pd.DataFrame(list(cursor))
#     return df

def read_csv_file(file):
    df = pd.read_csv(file, delimiter=',', nrows=70000)
    return df

def plotPerColumnDistribution(df, nGraphShown):
    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()
    nCol = len(numeric_columns)
    plot_ids = []
    colors = ['#e9724d', '#d6d727', '#92cad1', '#79ccb3', '#868686', '#b33c6a', '#00a2c7', '#f3af42', '#5e6f64']
    
    for i, column in enumerate(numeric_columns):
        plt.figure(figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
        df[column].hist(color=colors[i % len(colors)])  # Use modulo to cycle through colors
        plt.ylabel('Counts')
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
def plotDepartmentWiseDistribution(df, department_column, nGraphShown):
    unique_departments = df[department_column].unique()
    department_plots = []
    colors = ['#e9724d', '#d6d727', '#92cad1', '#79ccb3', '#868686', '#b33c6a', '#00a2c7', '#f3af42', '#5e6f64']
    
    for i, department in enumerate(unique_departments):
        department_plot_ids = []  # Store plot IDs for each department
        data = df[df[department_column] == department]
        numeric_columns = data.select_dtypes(include=np.number).columns.tolist()
        nCol = len(numeric_columns)
        for j, column in enumerate(numeric_columns):
            plt.figure(figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
            data[column].hist(color=colors[j % len(colors)])  # Use modulo to cycle through colors
            plt.ylabel('Counts')
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
            department_plot_ids.append(plot_id)
            plt.close()  # Close the current plot to avoid overlapping plots
        
        # Append the plot IDs for the department to the overall list
        department_plots.append(department_plot_ids)
    
    return unique_departments, department_plots

def get_department_wise_plots(df, department_column):
    # Get department-wise distribution plots
    department_names, department_plot_ids = plotDepartmentWiseDistribution(df, department_column, 6)
    # Assuming department_plot_ids is a list of lists, each inner list contains plot IDs for a specific department
    return department_names, department_plot_ids

def get_department_names(df, department_column):
    # Get unique department names from the DataFrame
    department_names = df[department_column].unique().tolist()
    return department_names



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

def get_plots(df):
    # Get data from MongoDB
    df = df
    
    # Plot per column distribution
    plot_ids =plotPerColumnDistribution(df, 6)
    return plot_ids


def analyze_sentiments(df):
    # Get data from MongoDB
    df = df
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




# import pandas as pd
# from textblob import TextBlob
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem import PorterStemmer
# import plotly.graph_objs as go
# import plotly.express as px
# from wordcloud import WordCloud
# import re
# import json
# import plotly.utils

# from pymongo import MongoClient

# # Assuming you have already connected to MongoDB
# client = MongoClient('mongodb://localhost:27017/')
# db = client['Project']
# plots_collection = db['Plots_Review']

# def merge_and_drop_columns(df):
#     # Merge specified columns into 'emp_summary'
#     df['emp_summary'] = df['summary'] + df['pros'] + df['cons'] + df['advice-to-mgmt']
    
#     # Drop original columns
#     df.drop(['summary', 'pros', 'cons', 'advice-to-mgmt'], axis=1, inplace=True)
    
#     return df

# def preprocess_text(text):
#     # Tokenization
#     tokens = word_tokenize(text)
#     # Lowercase conversion
#     tokens = [token.lower() for token in tokens]
#     # Remove numeric values
#     tokens = [token for token in tokens if not token.isnumeric()]
#     # Remove unnecessary data like usernames
#     tokens = [re.sub(r'@[^\s]+', '', token) for token in tokens]
#     # Remove punctuation
#     tokens = [token for token in tokens if token.isalpha()]
#     # Remove stop words
#     stop_words = set(stopwords.words('english'))
#     tokens = [token for token in tokens if token not in stop_words]
#     # Stemming
#     stemmer = PorterStemmer()
#     tokens = [stemmer.stem(token) for token in tokens]
#     return ' '.join(tokens)

# def get_sentiment(text):
#     blob = TextBlob(text)
#     sentiment_score = blob.sentiment.polarity
#     if sentiment_score > 0:
#         sentiment = "Positive"
#     elif sentiment_score < 0:
#         sentiment = "Negative"
#     else:
#         sentiment = "Neutral"
#     return sentiment

# def preprocess_and_get_sentiment(df):
#     # Merge and drop columns
#     df = merge_and_drop_columns(df)
#     # Preprocess text and get sentiment
#     df['preprocessed_text'] = df['emp_summary'].apply(preprocess_text)
#     df['sentiment'] = df['preprocessed_text'].apply(get_sentiment)
#     return df

# def analyze_sentiments(df):
#     # Merge columns and preprocess text
#     df = preprocess_and_get_sentiment(df)
#     # Calculate sentiment analysis results
#     positive_reviews = df[df['sentiment'] == 'Positive'].shape[0]
#     negative_reviews = df[df['sentiment'] == 'Negative'].shape[0]
#     neutral_reviews = df[df['sentiment'] == 'Neutral'].shape[0]
#     return positive_reviews, negative_reviews, neutral_reviews

# def plot_sentiment_distribution(df):
#     sentiment_counts = df['overall-ratings'].value_counts()
#     fig = go.Figure(data=[go.Pie(labels=sentiment_counts.index, values=sentiment_counts.values)])
#     fig.update_layout(title='Sentiment Distribution')
#     return fig

# def plot_department_ratings(df):
#     fig = px.box(df, x='department', y='overall-ratings', title='Department-wise Ratings Distribution')
#     return fig

# def plot_correlation_heatmap(df):
#     # Select numeric columns
#     numeric_df = df.select_dtypes(include=['float64', 'int64'])
    
#     # Calculate correlation matrix
#     corr = numeric_df.corr()
    
#     # Plot heatmap
#     fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.index, y=corr.columns))
#     fig.update_layout(title='Correlation Heatmap')
#     return fig

# def plot_interactive_scatter(df):
#     # Ensure 'emp_summary' column is present
#     if 'emp_summary' not in df.columns:
#         raise ValueError("DataFrame does not contain 'emp_summary' column")

#     # Create scatter plot
#     fig = px.scatter(df, x='work-balance-stars', y='career-opportunities-stars', hover_name='emp_summary',
#                      title='Work-Balance vs Career Opportunities')
#     return fig

# def plot_word_cloud(df, column):
#     text = ' '.join(df[column].dropna())
#     wordcloud = WordCloud(width=800, height=400).generate(text)
#     return wordcloud

# def store_plot_data(plot_data):
#     # Serialize the Plotly figure into JSON format
#     serialized_plot_data = json.dumps(plot_data, cls=plotly.utils.PlotlyJSONEncoder)
    
#     # Store the serialized plot data in the MongoDB collection
#     plot_id = plots_collection.insert_one({'plot_data': serialized_plot_data}).inserted_id
#     return plot_id

# def fetch_plot_data_from_mongodb(plot_id):
#     # Retrieve serialized plot data from MongoDB
#     plot_data = plots_collection.find_one({'_id': plot_id})

#     # Deserialize the plot data into a Plotly figure object
#     plot_data = json.loads(plot_data['plot_data'])
#     return plot_data

# def get_plots(df):
#     plots = []
#     # Generate plots and store them in MongoDB
#     plots.append(plot_sentiment_distribution(df))
#     plots.append(plot_department_ratings(df))
#     plots.append(plot_correlation_heatmap(df))
#     plots.append(plot_interactive_scatter(df))

#     # Store the plot data in MongoDB and retrieve their plot IDs
#     plot_ids = [store_plot_data(plot_data) for plot_data in plots]
#     return plot_ids
