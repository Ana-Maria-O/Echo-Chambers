import pandas as pd
import json

def df_append(comment, post, is_reply=False, replyee=None):
    df = pd.DataFrame()
    if comment['kind'] != "t1":
        #print(comment)
        return

    d = pd.DataFrame({
        'id':comment['data']['id'],
        'full id':comment['data']['name'],
        'author':comment['data']['author'],
        'post id':None,
        'created_utc':comment['data']['created_utc'],
        'controversial':comment['data']['controversiality'],
        'body':comment['data']['body'],
        'score':comment['data']['score'],
        'crosspost id':None,
        'reply to comment':None,
        'reply to user':None
        }, index=[0])

    df = pd.concat([df, d], ignore_index=True)

    # check if comment is on a crosspost
    if 'crosspost_parent' in post['data']:
        df.at[len(df) - 1, 'post id'] = post['data']['crosspost_parent'][3:]
        df.at[len(df) - 1, 'crosspost id'] = post['data']['id']
    else:
        df.at[len(df) - 1, 'post id'] = post['data']['id']
    
    # check if comment is reply
    if is_reply:
        id = comment['data']['parent_id'][3:]
        df.at[len(df) - 1, 'reply to comment'] = id
        df.at[len(df) - 1, 'reply to user'] = replyee
    else:
        df.at[len(df) - 1, 'reply to user'] = post['data']['author']
        
    # check if comment has replies
    if len(comment['data']['replies']) != 0:
        replies = comment['data']['replies']
        user = comment['data']['author']
        for reply in replies['data']['children']:
            df = pd.concat([df, df_append(reply, post, True, user)], ignore_index=True)
    
    return df

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

def get_sort(num):
    if num == 0:
        return '_hot'
    if num == 1:
        return '_new'
    return '_controversial'

def imp(type, sort):
    typ = get_type(type)
    sor = get_sort(sort)
    path = 'Data\\' + typ + sor + '.csv'
    
    return pd.read_csv(path)

def export(df, path):
    df.to_csv(path)

df = pd.DataFrame()
for i in range(1, 12):
    typ = get_type(i)
    comm = pd.DataFrame()
    print(typ)
    for j in range(3):
        sor = get_sort(j)
        try:
            df = imp(i, j)
            check = True
        except:
            check = False

        for post in df['id']:
            pst =open(typ + sor + '_' + post + '_comments.txt', 'r')
            pst = pst.read()
            pst = json.loads(pst)

            for cmt in pst[1]['data']['children']:
                app = df_append(cmt, pst[0]['data']['children'][0])
                comm = pd.concat([comm, app])

    comm.to_csv('Data\\Comments\\' + typ + '.csv')
    print(comm)