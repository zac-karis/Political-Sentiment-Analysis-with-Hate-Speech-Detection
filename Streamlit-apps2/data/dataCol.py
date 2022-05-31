# IMPORTS
import tweepy
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup
import time
import streamlit as st

# class for twitter data collection functions
class TwitterData():
    def __init__(self) -> None:
        pass
    # read the keys from the file 
    def authorize_twitter(self):
        keys = []
        with open('../Keys.txt') as f:
            for line in f:
                keys.append(line.strip())

        API_KEY = keys[1]
        API_KEY_SECRET = keys [4]
        ACCESS_TOKEN = keys[10]
        ACCESS_TOKEN_SECRET = keys[13]
        
        # initialize the api
        auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)
        
        return (api)


    def get_replies(self, url):
        name = url.split("/")[-3]
        tweet_id = url.split("/")[-1]

        #empty list for the replies
        replies = []
        
        api = self.authorize_twitter()
        # get replies from the tweet
        for tweet in tweepy.Cursor(api.search_tweets,q='to:'+name, result_type='recent', tweet_mode = "extended").items(1000):
            if hasattr(tweet, 'in_reply_to_status_id_str'):
                if (tweet.in_reply_to_status_id_str==tweet_id):
                    replies.append(tweet)
        
        #master list to hold all the data needed
        master_list = []
        for reply in replies:
            data_dict = {}
            data_dict["User"] = reply.author.screen_name
            data_dict["Data"] = reply.full_text

            master_list.append(data_dict)
            
        return master_list

    @st.cache
    def get_topic_tweets(self, topic, items_returned):
        api = self.authorize_twitter()
        tweets = tweepy.Cursor(
            api.search_tweets, q=topic, lang='en', tweet_mode="extended").items(items_returned)

        master_list = []
        for tweet in tweets:
            #remove the retweet tag from the text
            final_text = tweet.full_text.replace('RT', '')
            data_dict = {}
            data_dict["User"] = tweet.author.screen_name
            data_dict['Data'] = final_text
            master_list.append(data_dict)

        return master_list

# FACEBOOK CLASS
class FacebookData():
    def __init__(self, url) -> None:
        self.url = url

    # scroll down
    def scroll(self, driver):
        pop_out_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "popup_xout")))
        pop_out_btn.click()


    # funtion to click the view more button
    def view_more_click(self, driver):
        try:
            view_more_comments = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "View more comments…")))
            view_more_comments.click()

        except TimeoutException:
            view_more_comments = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.LINK_TEXT, "View previous comments…")))
            view_more_comments.click()

        except ElementClickInterceptedException:
            self.scroll(driver)

        except (NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException) as es:
            print(es)
        html = driver.page_source
        return html

    
    # function to click the button 50 times
    def view_more_comm(self, driver):
        i = 0
        my_bar = st.progress(0)
        while i < 25:
            html = self.view_more_click(driver)
            time.sleep(3)
            i += 1
            my_bar.progress(i * 4)
        return html

# function to get a list of all the comment elements
    # function to get a list of all the comment elements

    def get_comments(self):
         # install webdriver and selenium navigation
        st.info('Installing webdriver')
        options = webdriver.ChromeOptions()
        #options.add_argument("headless")
        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=options)
        driver.get(self.url)

        st.info("Getting facebook comments...")
        html = self.view_more_comm(driver)
        soup = BeautifulSoup(html, 'html.parser')
        comment_section = soup.find("div", {"class": "_59e9 _1-ut _2a_g _34oh"})
        comment_els = comment_section.find_all("div", {"class": "_2a_i"})

        master_list = []
        for c in comment_els:
            data_dict = {}
            data_dict["User"] = c.find("div", {"class": "_2b05"}).text
            data_dict["Data"] = c.find(
                "div", {"data-sigil": "comment-body"}).text
            master_list.append(data_dict)
        return master_list
