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

import tweet_creds   #twitter authentication credentials
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 

# twitter clients 

class TwitterClient():
    
    def __init__(self,twitter_user = None):

#None defaults to our own profile if we dont specifiy an account other than ours
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

#function to if the data we want is from a different users timeline 
        self.twitter_user = twitter_user
      
    def get_twitter_client_api(self):
        return self.twitter_client
    
        
    def get_tweets(self,num_tweets):
        tweets = []
#cursor allows us to get the user timeline tweets , .items tells us how many tweets to get from timeline
        for tweet in Cursor(self.twitter_client.user_timeline, id = self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets            

# get friend_list ~    
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
        
        #create authentitcation for tweet_creds objects
        auth = OAuthHandler(tweet_creds.API_KEY, tweet_creds.API_SECRETE_KEY)
        auth.set_access_token(tweet_creds.ACCESS_TOKEN, tweet_creds.ACCESS_TOKEN_SECRETE)
        return auth 
    
    
#cr8 a class that allows us to print the tweets
class TwitterListener(StreamListener):
    """
    This is a basic listener class that prints received tweets to stdout
    
    """
#create an object associated with the filename the tweets will be written to 
    def __init__(self, fetched_tweets_filename):
        
        self.fetched_tweets_filename = fetched_tweets_filename    
    
#on_data lets us get data from twitter and print if true
    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e: 
             print("Error on_data: %s" % str(e))
        return True       
            
            
#prints out error if we encounter any error    
    def on_error(self, status):
        if status == 420:
            return False 
        print(status)

#create a more precise code for streaming 
class TwitterStreamer():
    """
    This class is a class for streaming and processing lives streams
    
    """
    def __init__(self):
        self.Twitter_authenticator = TwitterAuthenticator()
    
    def stream_tweets(self,fetched_tweets_filename,hash_tag_list):
#this handles tt authentitcation and the connection to the tt streaming API

#object 1, listener object which is responsible for how to deal with the data and the errors        
        listener = TwitterListener(fetched_tweets_filename)
        auth    = self.Twitter_authenticator.authenticate_twitter_app()
#create stream variable 
        stream = Stream(auth,listener)

#filter stream based on keywords defined in track 
        stream.filter(track=hash_tag_list)
     
#create class responsible for analyzing and categorizing the tweets content from twitter
class tweetAnalyzer():

    def tweets_to_df(self, tweets):
#looping through all coded text to extract the tweet from the tweets and create a list for it
#columns specifies column where tweets should be extracted to in file 
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])
#give us the id of the tweet, store in an array, convert the array to a np array and create a column in the df        
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
#create an object from the srtdoutlistener and start streaming tweets 
if __name__ == "__main__": 
    
#function to get api info for tweets 
    twitter_client = TwitterClient()
    tweet_analyzer = tweetAnalyzer()
    
    api = twitter_client.get_twitter_client_api()
      
    #define a variable to be able to specify user we want to extract tweets from and the number of tweets needed.
    tweets = api.user_timeline(screen_name = "sarkodie", count=5)

    #converting the tweets into a dataframe 
    df = tweet_analyzer.tweets_to_df(tweets)
#    print(df.head(5)) 
    
    #shows us what info we can extract from tweets
    # print(dir(tweets[0]))
    
    # use this code syntax type to generate relative info from particular tweet
    # print(tweets[0].id) gives us the id of the first tweet

    #get average lenght of over all tweets
#   print(np.mean(df['len']))

    #get the number of tweets for the most liked tweets
#    print(np.max(df['likes']))

#time series 
    time_likes = pd.Series(data = df['likes'].values, index =df['date'])
    time_likes.plot(figsize=(16,4), label="likes", legend=True)
    time_retweets = pd.Series(data = df['retweets'].values, index =df['date'])
    time_retweets.plot(figsize=(16,4), label="retweets", legend=True)
    plt.show()
    

#all graphongs can take this form 
