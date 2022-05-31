import spacy
from collections import Counter
from fuzzywuzzy import fuzz
import streamlit as st
import spacy
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# visualise extracted NER count and extract NERs
def plot_named_entity_barchart(text):
    nlp = spacy.load("political_ner_model")

    def _get_ner(text):
        doc = nlp(text)
        return [X.label_ for X in doc.ents]

    ent = text.apply(lambda x: _get_ner(x))
    ent = [x for sub in ent for x in sub]
    counter = Counter(ent)
    count = counter.most_common()

    x, y = map(list, zip(*count))

    # get unique list elements to pass to
    # streamlit app for dropdown options
    ent = set(ent)

    return ent, x, y


def get_ruto_similarity_ratio(name):
    """ This is a method to determine how similar a name mentioned is to the name of Ruto. 
    For example someone might write Rutot by mistake hence we need to record this mention"""

    ruto = 'william ruto'
    ratio = 0
    if name != 'Raila':
        ratio = fuzz.partial_ratio(ruto.lower(), name.lower())
    return int(ratio)

def get_raila_similarity_ratio(name):
    """ This is a method to determine how similar a name mentioned is to the name of Raila. 
    For example someone might write Railal by mistake hence we need to record this mention"""
    
    raila = 'raila amolo odinga'
    ratio = 0
    if name != 'Ruto':
        ratio = fuzz.partial_ratio(raila.lower(), name.lower())
    return int(ratio)


def get_similar_candidate_names(names):
    """
    This is a method to get get the different names of politicians and return only one common name. 
    For example Raila may be known as Baba, Odinga, etc. We convert all these names to Raila.
    """

    ruto = ["ruto", 'william', "deputy", "wSR", "william samoei ruto", 'dp', "samoei", 'arap', 'willi', 'willy']
    raila = ["raila amolo odinga", "raila", "odinga", "baba", "rao", "kitendawili"]
    uhuru = ['uhuru muigai kenyatta', 'uhuru kenyatta', 'uhuru', 'kenyatta', 'jayden']
    for i in range(len(names)):
        if (names[i].lower() in ruto) or (get_ruto_similarity_ratio(names[i].lower()) > 50):
            names[i] = 'Ruto'

        elif (names[i].lower() in raila) or (get_raila_similarity_ratio(names[i].lower()) > 50):
            names[i] = 'Raila'

        elif (names[i].lower() in uhuru):
            names[i] = 'Uhuru'
    return names

# visualise tokens per entity
def plot_most_common_named_entity_barchart(text, entity):
   
    nlp = spacy.load("political_ner_model")
    
    #get the text mentioning the entity
    def _get_ner(text,ent):
        doc=nlp(text)
        return [X.text for X in doc.ents if X.label_ == ent]
    
    entity_filtered=text.apply(lambda x: _get_ner(x,entity))
    entity_filtered=[i for x in entity_filtered for i in x]
    entity_filtered = get_similar_candidate_names(entity_filtered)
    
    #get the number of times the name is mentioned
    counter=Counter(entity_filtered)
    
    #separate into name and the number of mentions for plotting
    x,y=map(list,zip(*counter.most_common(10)))
    
    return (x, y)


def vaderSentimentAnalysis(text):
    analyzer = SentimentIntensityAnalyzer()
    vs = analyzer.polarity_scores(text)
    return vs['compound']

# function to analyse


def vader_analysis(compound):
    if compound > 0:
        return 'Positive'
    elif compound < 0:
        return 'Negative'
    else:
        return 'Neutral'

    
def get_politician_names(names):
    '''
    This method gets the politicians mentioned in each comments and puts them in a separate column
    it returns alist of all the politicians mentioned in each comment. 
    The set method is used to remove repetitive mentions
    '''
    pol_names = []
    for i in range(len(names)):
        if names[i][1] == 'POLITICIAN':
            pol_names.append(names[i][0])

    pol_names = get_similar_candidate_names(pol_names)
    pol_names = list(set(pol_names))
    return pol_names


def get_politician_sentiment(politician, sentiment, df):
    '''
    Gets the number of sentiments for a particular politician. 
    Pass in the name of the politician and the sentiment you want to identify
    '''
    count = 0
    for i in range(len(df)):
        for n in df['Politicians'].iloc[i]:
            if n == politician and df['Vader_Analysis'].iloc[i] == sentiment:
                count += 1

    return count


def get_sentiment_count(sentiment, df, top3):
    '''
    get the number of sentiments for the top 3 politicians.
    pass in the sentiment you want to count.
    returns a list of the count of sentiments you passed in for all the politicians
    '''
    sentiment_count = []
    for pol in top3:
        counts = get_politician_sentiment(pol, sentiment, df)
        sentiment_count.append(counts)
    return sentiment_count


def plot_sentiment_analysis(sentiment, title, top3):
    '''
    Plot the graphs for the top 3 candidates with their sentiment variations
    '''
    y = np.array(sentiment)
    myexplode = [0.1, 0, 0]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.grid(False)
    plt.style.use('ggplot')
    plt.pie(y, labels=top3, explode=myexplode, shadow=True, autopct='%1.0f%%')
    plt.legend()
    fig.set_facecolor('white')
    plt.title(title)

    st.pyplot(fig)
