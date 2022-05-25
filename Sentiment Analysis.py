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
import re     #used to clean tweets unnecessary  contents 

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


"""
              def get_friend_list(self, num_friends):
                  friend_list = []
                  for friend in Cursor(self.twitter_client.friends).items(num_friends):
                      friend_list.append(friend)
                  return friend list
"""
  
# get home_timeline_tweets ~ top tweets on twitter page     
"""
              def home_timeline_tweets(self, num_friends):
                  home_timeline_tweets = []
                  for tweet in Cursor(self.twitter_client.home_timeline).items(num_friends):
                      home_timeline_tweets.append(tweet)
                  return home_timeline_tweets
"""

class TwitterAuthenticator():
    
    def authenticate_twitter_app(self):
        
        auth = OAuthHandler(tweet_creds.API_KEY, tweet_creds.API_SECRETE_KEY)
        auth.set_access_token(tweet_creds.ACCESS_TOKEN, tweet_creds.ACCESS_TOKEN_SECRETE)
        return auth 
    
class TwitterListener(StreamListener):
    """
    This is a basic listener class that prints received tweets to stdout
    
    """
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
    """
    This class is a class for streaming and processing lives streams
    
    """
    def __init__(self):
        self.Twitter_authenticator = TwitterAuthenticator()
    
    def stream_tweets(self,fetched_tweets_filename,hash_tag_list):

        listener = TwitterListener(fetched_tweets_filename)
        auth    = self.Twitter_authenticator.authenticate_twitter_app()

        stream = Stream(auth,listener)

        stream.filter(track=hash_tag_list)
     
class tweetAnalyzer():
    
    def clean_tweet(self,tweet):
#remove special characters from tweet
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
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        return df
    
"""
list of tweet variable or parameters 
    ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__',
     '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__',
     '__init_subclass__', '__le__', '__lt__', '__module__',
     '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
     '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_api',
     '_json', 'author', 'contributors', 'coordinates', 'created_at', 'destroy',
     'entities', 'extended_entities', 'favorite', 'favorite_count', 
     'favorited', 'geo', 'id', 'id_str', 'in_reply_to_screen_name', 
     'in_reply_to_status_id', 'in_reply_to_status_id_str', 'in_reply_to_user_id',
     'in_reply_to_user_id_str', 'is_quote_status', 'lang', 'parse',
     'parse_list', 'place', 'possibly_sensitive', 
     'retweet', 'retweet_count', 'retweeted', 'retweeted_status',
     'retweets', 'source', 'source_url', 'text', 'truncated', 'user']
"""

if __name__ == "__main__": 
    
    twitter_client = TwitterClient()
    tweet_analyzer = tweetAnalyzer()
    
    api = twitter_client.get_twitter_client_api()
    tweets = api.user_timeline(screen_name = "sarkodie", count=5)
    df = tweet_analyzer.tweets_to_df(tweets)

#looping through tweets in the df column named tweets to analyze sentiments
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['Tweets']])
    print(df.head(5))