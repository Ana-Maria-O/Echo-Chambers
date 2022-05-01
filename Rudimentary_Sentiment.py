#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd #reading files

# import ijson #imporing data
import timeit
from os import listdir

import nltk #sentiment model
from nltk import classify
from nltk import NaiveBayesClassifier

import random #for shuffeling

import matplotlib.pyplot as plt
import seaborn as sns

from nltk.corpus import stopwords
nltk.download('stopwords')
from nltk.tokenize import word_tokenize

from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('vader_lexicon') #needed for analysis
sia = SentimentIntensityAnalyzer()


def remake_sentence(lis: list):
    #takes a list of tokens and puts them back intro a string
    #I dunno exactly why but it breaks without this 
    out = ""
    for i in lis:
        out = out + "{} ".format(i)
    return out


def longer_sentiment(sent: str):
    #SIA score only works well for shorter sentences
    #so for longer ones we split the sentence in smaller
    #sentences, and we take the 'average' sentiment overall
    #takes as input a string, returns a dictionary
    #details in the rudimentary_sentiment() function as they're the same
    count = 0
    out = {'neg': 0, 'neu': 0, 'pos': 0, 'compound': 0}
    temps = None
    smallsent = None
    while count <= len([i for i in sent]):
        temps = [i for i in sent][count:count+10]
        temps = remake_sentence(temps)
        smallsent = sia.polarity_scores(temps)
        for i in out.keys():
            out[i] += (smallsent[i])
        count += 10
    for i in out:
        out[i] = out[i] / (count / 10)
    return out

def rudimentary_sentiment(string):
    #takes a string as input
    #returns as output a dictionary containing:
    #neg: the percentage of negative sentiment
    #neu: the percentage of neutral sentiment
    #pos: the percentage of positive sentiment
    #compound: the 'overall' sentiment
    
    for i in '.,;:[{()}]`-~=+_?!\'':
        string = string.replace(i, '')
    tokens = string.split(' ')
    out = ''
    sent = remake_sentence(tokens)
    if len([i for i in tokens]) <= 30:
        out = sia.polarity_scores(sent)
    else:
        out = longer_sentiment(tokens)
    return out

