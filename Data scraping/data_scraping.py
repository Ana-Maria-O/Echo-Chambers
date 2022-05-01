from unittest import skip
from numpy.testing._private.utils import IgnoreException
import requests
import json
import pandas as pd

def up_downs(score, ratio):
    try:
        upvotes = (score * ratio) // (2 * ratio - 1)
        downvotes = upvotes - score
    except:
        upvotes = None
        downvotes = None
    return upvotes, downvotes
            
# def df_append(comment, post, is_reply=False, replyee=None):
#     df = pd.DataFrame()
#     if comment['kind'] != "t1":
#         #print(comment)
#         return
#     df = pd.DataFrame()
#     d = pd.DataFrame({
#         'id':comment['data']['id'],
#         'full id':comment['data']['name'],
#         'author':comment['data']['author'],
#         'post id':None,
#         'created_utc':comment['data']['created_utc'],
#         'controversial':comment['data']['controversiality'],
#         'body':comment['data']['body'],
#         'score':comment['data']['score'],
#         'crosspost id':None,
#         'reply to comment':None,
#         'reply to user':None
#         }, index=[0])

#     # check if comment is on a crosspost
#     if 'crosspost_parent' in post['data']:
#         df.at[len(df) - 1, 'post id'] = post['data']['crosspost_parent'][3:]
#         df.at[len(df) - 1, 'crosspost id'] = post['data']['id']
#     else:
#         df.at[len(df) - 1, 'post id'] = post['data']['id']
    
#     # check if comment is reply
#     if is_reply:
#         id = comment['data']['parent_id'][3:]
#         df.at[len(df) - 1, 'reply to comment'] = id
#         df.at[len(df) - 1, 'reply to user'] = replyee
#     else:
#         df.at[len(df) - 1, 'reply to user'] = post['data']['author']
        
#     # check if comment has replies
#     if len(comment['data']['replies']) != 0:
#         replies = comment['data']['replies']
#         user = comment['data']['author']
#         for reply in replies['data']['children']:
#             df = df.append(df_append(reply, post, True, user))
    
#     return df

def get_comments(limit, link, file, id):
    #df = pd.DataFrame()
    
    #print(limit)
    try:
        comm = requests.get(link, headers = headers, params={'limit':str(limit)}).json()
        out = open('Dumped Data//' + file +'_' + id + '_comments.txt', 'w')
        json.dump(comm, out)
        out.close()
    except: skip
    

    #post = comm[0]['data']['children'][0]

    #while curr > prev:
    #print('comment batch')
    #prev = curr
    #comments = comm[1]
   
    #for comment in comments['data']['children']:
     #   df = df.append(df_append(comment, post))
        
    #print(df)
    #print(last_name)
    #curr = len(df)
    
    #return df
        
def make_dataframe(bas, typ, file):
    print("start " + file)

    # open dump file
    out = open('Dumped Data//' + file + '.txt', 'w')

    prev = -1
    curr = 0
    link = bas + typ

    df = pd.DataFrame()
    d = pd.DataFrame()
    subreddit_type = requests.get(link, headers = headers, params={'limit':'100'})
    json.dump(subreddit_type.json(), out)

    while curr > prev:
        prev = curr
        for post in subreddit_type.json()['data']['children']:

            score = int(post['data']['score'])
            ratio = float(post['data']['upvote_ratio'])
            id = post['data']['id']
            is_crosspost = 'crosspost_parent' in post['data']
            comments = post['data']['num_comments']

            # compute an approximation of upvotes and downvotes
            upvotes, downvotes = up_downs(score, ratio)

            # collect post data into a dataframe 
            d = pd.DataFrame({
                'id':id,
                'full id':post['data']['name'],
                'title':post['data']['title'],
                'author':post['data']['author'],
                'up-down ratio':ratio,
                'score':score,
                '# comments':comments,
                'created_utc':post['data']['created_utc'],
                '# crossposts':post['data']['num_crossposts'],
                'upvotes':upvotes,
                'downvotes':downvotes,
                'is crosspost':is_crosspost,
                'crosspost_parent':None
            }, index=[0])

            df = pd.concat([df, d], ignore_index=True)

            # if crosspost, insert the ID of the original post
            if is_crosspost:
                df.at[len(df) - 1, 'crosspost_parent'] = post['data']['crosspost_parent'][3:]

            # scrape and export all comment data from this post
            clink = bas + '/comments/' + id
            get_comments(comments, clink, file, id)
        
        curr = len(df)
        last_name = df.iloc[-1:]['full id']
        subreddit_type = requests.get(link, headers = headers, params={'limit':'100', 'after':last_name})
        try:
            json.dump(subreddit_type.json(), out)
        except:
            continue

        print(len(df))

    print(file + ' ' + str(len(df)))
    out.close()
    return df

def export(df, path):
    df.to_csv(path)

def get_type(num):
    switcher = {
        1: 'atheism',
        2: 'christianity',
        3: 'conservative',
        4: 'conspiracy',
        5: 'exchristian',
        6: 'flatearth',
        7: 'liberal',
        8: 'lockdownskepticism',
        9: 'news',
        10: 'politics',
        11: 'science'
    }
    return switcher.get(num, 'fuckoff')

def make_dfs():
    for i in range(11, 12):
        type = get_type(i)

        print(type + " hot")
        hot = make_dataframe(base + type, '/hot', type + '_hot')
        print(type + " new")

        new = make_dataframe(base + type, '/new', type + '_new')
        print(type + " controversial")
        con = make_dataframe(base + type, '/controversial', type + '_controversial')

        export(hot, 'Reddit Data//Posts//' + type + '_hot.csv')
        export(new, 'Dumped Data//Posts//' + type + '_new.csv')
        export(con, 'Dumped Data//Posts//' + type + '_controversial.csv')

#authentication data
client_id = 'RxgO9SK7EgvWg9-KZmgTgw'
secret_key = 'IZ_G3NNOyx1qJnIrAfefMwNAK275Og'

auth = requests.auth.HTTPBasicAuth(client_id, secret_key)

#read the password from txt file
with open('//home//aoltenicea//Documents//pw.txt', 'r') as f:
    pw = f.read()

#prepare arguments to pass to the connection request
base_url = 'https://www.reddit.com/api/v1/access_token'
data = {'grant_type': 'password', 'username': 'analeep', 'password': pw}
headers = {'User-Agent' : 'HonorsData/0.0.1'}

#make connection request
res = requests.post(base_url, auth=auth, data=data, headers=headers)
con = res.json()
#print(con)

token = con['access_token']
headers['Authorization'] = f'bearer {token}'
#print(headers)
base = 'https://oauth.reddit.com/r/'

make_dfs()