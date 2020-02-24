# Databricks notebook source
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor
from textblob import TextBlob
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import tweepy as tw
import pandas as pd
import re
import numpy as np
import csv

consumer_key = '' #twitter app’s API Key
consumer_secret = '' #twitter app’s API secret Key
access_token = '' #twitter app’s Access token
access_token_secret = '' #twitter app’s access token secret

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
auth_api = API(auth)

IBMacess_tweets = auth_api.user_timeline(screen_name = "IBMAccess", q="#a11y",count = 1000, include_rts = False, tweet_mode = "extended", lang="en", since="2018-11-16")
final_tweets = [each_tweet.full_text for each_tweet in IBMacess_tweets]

def cleanTxt(text):
  text = re.sub('@[A-Za-z0–9]+', '', text)  # Removing @mentions
  text = re.sub('https?:\/\/\S+', '', text)  # Removing hyperlink

  return text


df = pd.DataFrame([tweet.full_text for tweet in IBMacess_tweets], columns=['Tweets'])
df['Tweets']= df['Tweets'].apply(cleanTxt)


def getSubjectivity(text):
  return TextBlob(text).sentiment.subjectivity


# Create a function to get the polarity
def getPolarity(text):
  return TextBlob(text).sentiment.polarity


# Create two new columns 'Subjectivity' & 'Polarity'
df['Subjectivity'] = df['Tweets'].apply(getSubjectivity)
df['Polarity'] = df['Tweets'].apply(getPolarity)


#Creating a worldcloud to check what words appear the most
allWords = ' '.join([twts for twts in df['Tweets']])
wordCloud = WordCloud(width=500, height=300, random_state=21, max_font_size=110).generate(allWords)


plt.imshow(wordCloud, interpolation="bilinear")
plt.axis('off')

#Analysis of sentiment score
def getAnalysis(score):
 if score < 0:
  return 'Negative'
 elif score == 0:
  return 'Neutral'
 else:
  return 'Positive'


df['Analysis'] = df['Polarity'].apply(getAnalysis)


# Printing positive tweets
print('Printing positive tweets:\n')
j=1
sortedDF = df.sort_values(by=['Polarity']) #Sort the tweets
for i in range(0, sortedDF.shape[0] ):
  if( sortedDF['Analysis'][i] == 'Positive'):
    print(str(j) + ') '+ sortedDF['Tweets'][i])
    print()
    j= j+1


# Printing negative tweets
print('Printing negative tweets:\n')
j=1
sortedDF = df.sort_values(by=['Polarity'],ascending=False)
for i in range(0, sortedDF.shape[0] ):
  if( sortedDF['Analysis'][i] == 'Negative'):
    print(str(j) + ') '+sortedDF['Tweets'][i])
    print()
    j=j+1

#plot polarity and subjectivity
plt.figure(figsize=(8, 6))
for i in range(0, df.shape[0]):
    plt.scatter(df["Polarity"][i], df["Subjectivity"][i], color='Blue')

plt.title('Sentiment Analysis')
plt.xlabel('Polarity')
plt.ylabel('Subjectivity')
plt.show()