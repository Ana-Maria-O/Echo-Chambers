import datetime
import requests
import json
import pandas as pd
from sympy import false
import os

def convertTimes():
    times = []
    
    # first 2016
    monthDays = [32, 30, 32] # days in each month + 1 because Python
    for month in range(1, 4): 
        for day in range(1, monthDays[month-1]): # for each month
            times.append(int(datetime.datetime(2016, month, day, 0, 0, 0).timestamp()))
    # then 2017
    #monthDays = [32, 29, 32, 31, 32, 31, 32, 32, 31, 32, 31, 32] # days in each month + 1 because Python
    #for month in range(1, 13): 
    #    for day in range(1, monthDays[month-1]): # for each month
    #        times.append(int(datetime.datetime(2017, month, day, 0, 0, 0).timestamp()))
 
    return times

def getSubs():
    return ['explainlikeimfive', 'askscience']
    #return ['Changemyview']

timestamps = convertTimes()
subs = getSubs()

def getRequest(link):
    done = False
    while not done:
        try:
            req = requests.get(link)
            done = True
        except: 
            print("Request denied. Trying to connect......")
    
    return req

def loadRequest(link):
    req = getRequest(link)
    done = False
    
    while not done:
        try:
            req = json.loads(req.content)
            done = True
        except:
            #print("Could not load request content. Trying again.........") #commented for speed
            req = getRequest(link)
    
    return req

def pullPosts():
    for sub in subs:
        posts = pd.DataFrame()
        base_posts = 'https://api.pushshift.io/reddit/search/submission/?sort=asc&size=500&subreddit=' + sub
        for index in range(90): # was `range(7)`
            link = base_posts + '&after=' + str(timestamps[index]) + '&before=' + str(timestamps[index + 1])
            time = timestamps[index]
            size = len(posts) -1
            while size != len(posts) and time <= timestamps[index + 1]:
                size = len(posts)
                req =  loadRequest(link)
                #print(len(req['data']))

                for post in req['data']:
                    score = int(post['score'])
                    id = post['id']
                    cmments = post['num_comments']

                    d = pd.DataFrame({
                    'id':id,
                    'full_id':'t3_' + id,
                    'title':post['title'],
                    'author':post['author'],
                    'score':score,
                    '# comments':cmments,
                    'created_utc':post['created_utc']
                    }, index=[0])

                    posts = pd.concat([posts, d], ignore_index=True)
                
                try:
                    time = posts['created_utc'].iloc[-1]
                except:
                    break # out of while loop since no posts during this first timeslice
                link = base_posts + '&after=' + str(time) + '&before=' + str(timestamps[index + 1])
        path = 'Pushshift//' + sub + '//'
        fil = path + sub + '_posts.csv'
        existsPath = os.path.exists(path)

        if not existsPath:
            # Create a new directory because it does not exist 
            os.makedirs(path)
        posts.to_csv(fil)

def getComments():
    for sub in subs:
        comments = pd.DataFrame()
        base_comments = 'https://api.pushshift.io/reddit/search/comment/?size=500&sort=asc&subreddit=' + sub
        
        posts = pd.DataFrame()
        posts= pd.read_csv('Pushshift//' + sub + '//' + sub + '_posts.csv')

        for index in range(90): # was `range(7)`
            link = base_comments + '&after=' + str(timestamps[index]) + '&before=' + str(timestamps[index + 1])
            old_created = 0
            created = -1
            
            #keyerrors = 0

            while old_created != created:
                old_created = created
                req = loadRequest(link)

                for comment in req['data']:
                    created = comment['created_utc']
                    if comment['link_id'] in posts['full_id'].values:
                        try:
                            d = pd.DataFrame({
                            'id':comment['id'],
                            'full_id':'t1_' + comment['id'],
                            'author':comment['author'],
                            'post id':comment['link_id'],
                            'created_utc':comment['created_utc'],
                            'controversial':comment['controversiality'],
                            'body':comment['body'],
                            'score':comment['score'],
                            'reply to':comment['parent_id'],
                            }, index=[0])
                        except Exception as e:
                            #print(e)
                            #keyerrors += 1
                            #print(f"Now at {keyerrors} KeyErrors")
                            #print(created)
                            d = pd.DataFrame({
                            'id':comment['id'],
                            'full_id':'t1_' + comment['id'],
                            'author':comment['author'],
                            'post id':comment['link_id'],
                            'created_utc':comment['created_utc'],
                            'controversial': 'Not available',
                            'body':comment['body'],
                            'score':comment['score'],
                            'reply to':comment['parent_id'],
                            }, index=[0])

                        comments = pd.concat([comments, d], ignore_index=True)

                comments = comments.drop_duplicates(subset=['id'])

                link = base_comments + '&after=' + str(created) + '&before=' + str(timestamps[index + 1])
        path = 'Pushshift//' + sub + '//'
        fil = path + sub + '_comments.csv'
        existsPath = os.path.exists(path)

        if not existsPath:
            # Create a new directory because it does not exist 
            os.makedirs(path)
        comments.to_csv(fil)

def main():
    pullPosts()
    getComments()

        
if __name__ == "__main__":
    main()