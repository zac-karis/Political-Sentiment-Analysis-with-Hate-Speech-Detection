import pickle
import numpy as np
import preprocessor as p
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

import matplotlib.pyplot as plt

#load classiffiers
with open('models/hatespeech_classifier.pkl', 'rb') as f:
    classifier_np = pickle.load(f)
    
with open('models/hatespeech_vectorizer.pkl', 'rb') as f:
    count = pickle.load(f)


def detect_hatespeech(text):
    text = [p.clean(text)]
    text_vectorizer = count.transform(text)
    tfidf = TfidfTransformer()
    test_tfidf = tfidf.fit_transform(text_vectorizer)
    prediction = classifier_np.predict(test_tfidf)
    category = "none"
    if prediction[0] == 0:
        category = "not hateful"
    else:
        category = "hateful and offensive"
    return category


def Hate_speech_and_offensive_language_analysis(h, nh):
   
    y = np.array([h, nh])
    mylabels = ["Hateful and Offensive", "Not Hateful"]
    myexplode = [0.05, 0]
    Colors = ["red", "green"]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.grid(False)
    plt.style.use('ggplot')

    plt.pie(y, labels=mylabels, explode=myexplode,
            colors=Colors, shadow=True, autopct='%1.0f%%')
    plt.legend()
    fig.set_facecolor('white')
    plt.title("Hatespeech and Offesive language Analysis")
    st.pyplot(fig)
