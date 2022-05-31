import streamlit as st
from helper_methods import *
from data import dataCol, political_pred, hatespeech_categ
import pandas as pd
import preprocessor as p
import seaborn as sns
import matplotlib.pyplot as plt
from selenium.common.exceptions import TimeoutException
import spacy


def main_app():
    st.set_page_config(page_title="PolPredict", page_icon="🖖")
    st.markdown("<h1 style='text-align: center; color: cyan;'>Political Prediction and Hate Speech Analysis</h1>",
                unsafe_allow_html=True)
    st.write("Welcome to the political Prediction and hate speech analysis app. The system utilizes Facebook and Twitter data to make an analysis of the comments from specifi users. You can be able to conduct analysis to determine who is the most prefered candidate for the upcoming elections. You can as well determine the number of hatespeech related comments in the posts ")

    # Side Panel setup
    display_app_header(main_txt="Step 1", sub_txt="Get data", is_sidebar=True)
    data_source = st.sidebar.radio(
        "Please select the source of data collection", ('Facebook', "Twitter"))
    if data_source == "Facebook":
        url = st.text_input("Copy and Paste the Mobile Facebook Url:")

    #TWITTER
    else:
        st.markdown("<h2 style='text-align: center; color: #c7f0db;'> You can either copy the url of a tweet and get the comments or search twitter for a specific topic to analyze.</h2", unsafe_allow_html=True)

        twitter_option = st.selectbox("Select an option.", ("Paste URL", "Search Topic"))
        if twitter_option == "Paste URL":
            url = st.text_input("Copy and paste the Twitter Url:")
        else:
            col1, col2 = st.columns(2)
            with col1:
                topic = st.text_input("Enter a topic you want to search")
            with col2:
                elements = st.text_input("Number of results")

     # get comments by pressing the button
    df = pd.DataFrame()
    replies = []
    if st.button("Get Data"):
        #TWITTER DATA COLLECTION
        if data_source == "Twitter":
            # create a twitter object for collection of comments and tweets
            obj = dataCol.TwitterData()

            # Getting replies from a post
            if twitter_option == "Paste URL":
                url_conf= check_twitter_url(url)
                # if url is invalid
                if url_conf is None:
                    st.warning("Invalid url!! Please paste a valid twitter url")

                # if url is valid
                else:
                    try:
                        st.info("Getting comments")
                        replies = obj.get_replies(url)
                    except Exception as e:
                        st.error("Sorry we could not find comments. Please retry or paste a new link!")
            
            # Searching for a topic
            else:
                st.info("Getting tweets. Please wait...")
                replies = obj.get_topic_tweets(topic, int(elements))

        # FACEBOOK DATA COLLECTION
        else:
            url_conf = check_facebook_url(url)
            # if url is invalid
            if url_conf is None:
                st.warning("Invalid url!! Please paste a valid Mobile Facebook url")
            else:
                try:
                    obj = dataCol.FacebookData(url)
                    replies = obj.get_comments()
                except TimeoutException:
                    st.error("Sorry we could not find comments. Please retry or paste a new Facebook url")

        st.success(str(len(replies)) + " comments collected")

        # create a dataframe for the data
        st.markdown("## Below are the comments collected")
        df = pd.DataFrame(replies)
        st.dataframe(df)

    # STEP 2 DATA ANALYSIS
        display_app_header(main_txt="Step 2", sub_txt="Data Analyis", is_sidebar=True)


        st.sidebar.write('The next processes you want performed are: \n Popularity Analysis \n Hate Speech Analyis')

        #POLITICAL PREDICTION
        df["clean_tweets"] = df["Data"].apply(lambda x: p.clean(x))

        st.subheader("Entity Recognition")
        st.write('We use a Natural Language Processing module to identify politicians and political parties being metioned in the data. \n Below is a graph of how they vary in our data.')
        ent, x, y = political_pred.plot_named_entity_barchart(df["clean_tweets"])

        fig, ax = plt.subplots()

        sns.barplot(x=y,y=x)
        ax.set_xlabel('Mentions')
        ax.set_ylabel('NER')

        ax.set_title('Politicians and Political Parties Mentioned\n\n', 
            fontweight ="bold")

        # show plot in streamlit
        st.pyplot(fig)


        st.subheader("Individual entity Mentions")
        entity_selected = st.selectbox("Please select the entity to analyze", ("POLITICIAN", "POLITICAL_PARTY"))
        st.write("Getting results...")


        x, y = political_pred.plot_most_common_named_entity_barchart(df['clean_tweets'], "POLITICAL_PARTY")

        #graph plotting
        fig, ax = plt.subplots()
        sns.barplot(y,x).set_title('POLITICAL_PARTY')

        ax.set_xlabel('Mentions')
        ax.set_ylabel('Name')
        
            
        st.pyplot(fig) 

        x, y = political_pred.plot_most_common_named_entity_barchart(df['clean_tweets'], "POLITICIAN")
        #graph plotting
        fig, ax = plt.subplots()
        sns.barplot(y,x).set_title('POLITICIAN')

        ax.set_xlabel('Mentions')
        ax.set_ylabel('Name')
        
            
        st.pyplot(fig)

        top3 = x[:3]

        st.info("Analyzing your data")
        my_bar = st.progress(0)

        # work with a clean database
        fin_data = pd.DataFrame(df[['Data']])

        #IDENTIFY THE ENTITIES IN EACH TEXT
        nlp = spacy.load("political_ner_model")
        fin_data["tags"] = df["Data"].apply(lambda x: [(tag.text, tag.label_) for tag in nlp(x).ents])

        #get politicians mentioned
        fin_data["Politicians"] = fin_data["tags"].apply(lambda x: political_pred.get_politician_names(x))
        
        my_bar.progress(50)
        #perform sentiment analysis
        fin_data['Vader_Sentiment'] = fin_data['Data'].apply(lambda x: political_pred.vaderSentimentAnalysis(x))
        fin_data['Vader_Analysis'] = fin_data['Vader_Sentiment'].apply(lambda x: political_pred.vader_analysis(x))

        negative_sentiments = political_pred.get_sentiment_count('Negative', fin_data, top3)
        positive_sentiments = political_pred.get_sentiment_count('Positive', fin_data, top3)
        neutral_sentiments = political_pred.get_sentiment_count('Neutral', fin_data, top3)
        my_bar.progress(100)

        st.subheader("Below is a distribution of the polarity of the comments towards the top 3 candidates")
        political_pred.plot_sentiment_analysis(negative_sentiments, 'NEGATIVE SENTIMENT ANALYSIS', top3)
        political_pred.plot_sentiment_analysis(positive_sentiments, 'POSITIVE SENTIMENT ANALYSIS', top3)
        political_pred.plot_sentiment_analysis(neutral_sentiments, 'NEUTRAL SENTIMENT ANALYSIS', top3)


        #political prediction
        
        # work with a clean database
        st.markdown("<h2 style='text-align: center; color: #c7f0db;'> HATESPEECH ANALYSIS </h2", unsafe_allow_html=True)
        st.write('The comments are analyzed and categorized into hateful and not hateful comments using a Machine Learning Algorithm. Below is a summary of the analysis performed.')
        fin_data = pd.DataFrame(df[['Data']])
        fin_data['Hatespeech Category'] = fin_data['Data'].apply(lambda x: hatespeech_categ.detect_hatespeech(x))
        harm = len(fin_data.loc[(fin_data['Hatespeech Category'] == "hateful and offensive")])
        not_harm = len(fin_data.loc[(fin_data['Hatespeech Category'] == "not hateful")])

        hatespeech_categ.Hate_speech_and_offensive_language_analysis(harm, not_harm)






            






    # style the buttons
    m = st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: rgb(52, 131, 235);
    }

    </style>""", unsafe_allow_html=True)


app = main_app()
