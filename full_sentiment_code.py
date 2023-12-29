#---
#imports and setup
#---
import pandas as pd #reading files
import json #importing data
import timeit #checking time taken
import os #reading files
from os import listdir #listdir imported separetely for convenience
import nltk #sentiment model
from nltk import classify #sentiment model
from nltk import NaiveBayesClassifier #sentiment model

import random #for shuffeling

import matplotlib.pyplot as plt #plotting data
import seaborn as sns #plotting data

#all the below is for sentiment analysis
from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()


from google.colab import drive #our data is stored in the drive

drive.mount('/content/drive')
reddits = ['The_Donald', 'Changemyview', 'AMA', 'politicaldiscussion', 'enoughtrumpspam', 'fuckthealtright'] #list of reddits to analyze

path = '/content/drive/MyDrive/Top 3%/Year 2/PCN Data/'
path2 = path + 'sentdicts/' #this is the path we've saved the sentiment analysis values to
                            #computing them takes very long, so this was done for efficiency



#---
#sentiment analysis
#---
#NOTE: running this section will take very long
#as such to do the plots we have already saved the output to files
#and simply load them. In this code we skip the part where we
#save the files to csv's however, for convenience.

def longer_sentiment(sent: str):
    #SIA score only works well for shorter sentences
    #so for longer ones we split the sentence in smaller
    #sentences, and we take the 'average' sentiment overall
    #takes as input a string, returns a dictionary
    #details in the rudimentary_sentiment() function as they're the same
    jump = 0 #
    meancntr = 1
    count = 144 #SA algorithm trained on twitter posts -> 144 chrs!
    out = {'neg': 0, 'neu': 0, 'pos': 0, 'compound': 0}
    temps = None
    smallsent = None
    while count <= len(sent):
        added = False
        try:
            while sent[count] != ' ':
                count -= 1
                temps = sent[jump:count]
        except IndexError:
            temps = sent[jump:len(sent)]
        finally:
            if temps:
                smallsent = sia.polarity_scores(temps)
            else:
                smallsent = {'neg': 0, 'neu': 0, 'pos': 0, 'compound': 0}
        for i in out.keys():
            if smallsent[i] != 0:
                added = True
            out[i] += (smallsent[i])
        jump += count
        count += 144
        if added:
            meancntr += 1
    for i in out:
        out[i] = out[i] / meancntr
    return out



def clean_stuff(inn):
  #this function takes a list of reddit posts (strings)
  #and returns the same list, with only non-deleted/removed,
  #non-URL posts remaining, so SA can be applied to them
    out = [i for i in inn if i != '[removed]']
    out = [i for i in out if i != '[deleted]']
    out = [i for i in out if type(i) == str]
    out = [i for i in out if 'Your post has been removed' not in i]
    return out


def rudimentary_sentiment(string):
  #this function takes as input a string and returns
  #its SA scores divided (as per the sia package)
  #in negative|neutral|positive|compound
  #(in that order) as a dictionary
    string = str(string)
    for i in '.,;:[{()}]`-~=+_?!\'': #erase punctuation, it has no useful info
        string = string.replace(i, '')
    out = None
    wordlen = len(string.split(' '))
    wordchr = len(string)
    if wordlen > 10 and wordchr > 144: #dataset trained on twitter posts, hence 144 characters
      return longer_sentiment(string)
    else:
      return sia.polarity_score(string)


red_sents = {} #this will be the final dictionary of reddit sentiments
for red in reddits:
  curr_csv = pd.read_csv(path + red + '_comments.csv')
  sents = {}
  text_df = clean_stuff(curr_csv['body']) #we extract the actually analyzable posts
                                          #and store them in a list
  cntr = 0
  for sentence in text_df: #and here is where we actually analyze each post
    sents[cntr] = rudimentary_sentiment(sentence)
    cntr += 1
  red_sents[red] = sents

#---
#Loading the already saved sentiment values dataset
#And putting them into usable data files
#---
just_df = {}
for csv in [i for i in os.listdir(path2) if i.endswith('.csv')]:
  df = pd.read_csv(path2+csv)
  df = df[['neg', 'neu', 'pos', 'compound']]
  just_df[csv] = []
  just_df[csv].append(df)


#below we will plot the sentiment value plots
#note that we chose to exclude the code to save them 

#---
#Plots (non-tails)
#---
title = {
    'neu': 'Neutral',
    'pos': 'Positive',
    'neg': 'Negative',
    'compound': 'Compound'
}


for redit in just_df.keys():
  for data in just_df[redit]:
    for sentiment in data.keys():
      plt.figure()
      plt.xlim([-1, 1]) if sentiment == 'compound' else plt.xlim([0, 1])
      plt.ylim([0, 5])
      plt.title('{} sentiment in r/{}'.format(title.get(sentiment), redit[:-9]))
      plt.xlabel('{} sentiment score'.format(title.get(sentiment)))
      sns.histplot(data[sentiment], bins = 24, stat = 'density')#, fit = None)
    
#---
#Plots (tails)
#---

for redit in just_df.keys():
  for data in just_df[redit]:
    for sentiment in data.keys():
      if sentiment != 'compound':
        plt.figure()
        plt.xlim([0, 0.4]) if sentiment == 'neu' else plt.xlim([0.4, 1])
        plt.ylim([0, 0.6])
        
        sns.histplot(data[sentiment], bins = 24, stat = 'density')
