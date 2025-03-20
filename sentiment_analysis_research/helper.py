import numpy as np
import pandas as pd
import re
import string
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem import PorterStemmer
ps = PorterStemmer()

with open('static/model/sentiment_model.pickle', 'rb') as f:
    model=pickle.load(f)


with open('static/model/categorization_model.pickle', 'rb') as f:
    modelc=pickle.load(f)

with open('static/model/tfidf_vectorizer.pickle', 'rb') as f:
    vectorizer = pickle.load(f)

def remove_punctuation(text):
    for punctuation in string.punctuation:
        text = text.replace(punctuation, '')
    return text


with open('static/model/corpora/stopwords/english', 'r') as file:
    sw=file.read().splitlines()


vocab=pd.read_csv('static/model/vocabulary.txt',header=None)
tokens=vocab[0].tolist()


def preprocessing(text):
    data=pd.DataFrame([text],columns=['feedback'])
    data["feedback"] = data["feedback"].apply(lambda x: " ".join(re.sub(r'^https?:\/\/.*[\r\n]*', '', x, flags=re.MULTILINE) for x in x.split()))
    data["feedback"] = data["feedback"].apply(lambda x: " ".join(x.lower() for x in x.split()))
    data["feedback"] = data["feedback"].apply(remove_punctuation)
    data["feedback"] = data["feedback"].str.replace(r'\d+', '', regex=True)
    data["feedback"] = data["feedback"].apply(lambda x: " ".join(x for x in x.split() if x not in sw))
    data["feedback"] = data["feedback"].apply(lambda x: " ".join([ps.stem(x) for x in x.split()]))
    return data["feedback"]



def vectorizer_tfidf(text_series):
    return vectorizer.transform(text_series)


def get_prediction(vectorized_txt):
    prediction = model.predict(vectorized_txt)
    if prediction == 1:
        return "negative"
    elif prediction == 10:
        return "neutral"
    else:
        return "positive"


def get_prediction_c(vectorized_txt):
    prediction = modelc.predict(vectorized_txt)
    if prediction == 1:
        return "service"
    elif prediction == 10:
        return "policy"
    else:
        return "claim"



