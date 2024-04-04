from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L12-v2')
from nltk.tokenize import sent_tokenize 
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import torch
from nltk.corpus import stopwords
import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
import nltk
import pandas as pd
nltk.download('punkt') 
import PyPDF2 as pdf
from PyPDF2 import PdfReader, PdfWriter