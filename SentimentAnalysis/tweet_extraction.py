# Databricks notebook source
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor

consumer_key = '' #twitter app’s API Key
consumer_secret = '' #twitter app’s API secret Key
access_token = '' #twitter app’s Access token
access_token_secret = '' #twitter app’s access token secret

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
auth_api = API(auth)

IBMacess_tweets = auth_api.user_timeline(screen_name = "IBMAccess", count = 1000, include_rts = False, tweet_mode = "extended")
final_tweets = [each_tweet.full_text for each_tweet in IBMacess_tweets]

with open('/dbfs/IBMAccess.txt', 'w') as f:
  for item in final_tweets:
    f.write("%s\n" % item)

# COMMAND ----------

read_tweets = []
with open('/dbfs/IBMAccess.txt','r') as f:
  read_tweets.append(f.read())
  
for x in read_tweets:
  print(x)
