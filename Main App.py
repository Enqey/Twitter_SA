# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 06:35:31 2021

@author: Enqey De-Ben Rockson
"""

from tweepy import API
from tweepy import Cursor 
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import tweet_creds
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt


from textblob import TextBlob
import re

class TwitterClient():
    def __init__(self,twitter_user = None):

        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user     
        
    def get_twitter_client_api(self):
        return self.twitter_client
    
    def get_tweets(self,num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id = self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets            

class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        
        auth = OAuthHandler(tweet_creds.API_KEY, tweet_creds.API_SECRETE_KEY)
        auth.set_access_token(tweet_creds.ACCESS_TOKEN, tweet_creds.ACCESS_TOKEN_SECRETE)
        return auth 
    
class TwitterListener(StreamListener):
    def __init__(self, fetched_tweets_filename):
        
        self.fetched_tweets_filename = fetched_tweets_filename    
    
    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e: 
             print("Error on_data: %s" % str(e))
        return True       
            
    def on_error(self, status):
        if status == 420:
            return False 
        print(status)

class TwitterStreamer():
    def __init__(self):
        self.Twitter_authenticator = TwitterAuthenticator()
    
    def stream_tweets(self,fetched_tweets_filename,hash_tag_list):
        listener = TwitterListener(fetched_tweets_filename)
        auth    = self.Twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth,listener)
        stream.filter(track=hash_tag_list)
        
class tweetAnalyzer():
    
    def clean_tweet(self,tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)"," ", tweet).split())

    def analyze_sentiment(self,tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        
        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else: 
            return -1 


    def tweets_to_df(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        return df
        
if __name__ == "__main__":
    
    twitter_client = TwitterClient()
    tweet_analyzer = tweetAnalyzer()
    
    api = twitter_client.get_twitter_client_api()
      
    tweets = api.user_timeline(screen_name = "sarkodie", count=5)

    df = tweet_analyzer.tweets_to_df(tweets)
    print(df.head(5)) 
    
    time_likes = pd.Series(data = df['likes'].values, index =df['date'])
    time_likes.plot(figsize=(16,4), label="likes", legend=True)
    time_retweets = pd.Series(data = df['retweets'].values, index =df['date'])
    time_retweets.plot(figsize=(16,4), label="retweets", legend=True)
    plt.show()
    
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['Tweets']])
    print(df.head(5))