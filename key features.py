import pandas as pd
import numpy as np

# returns a string with the name of the file
# correspondimng to the numth timeslice
# returns 'Invalid' if num is not a valid number
def getTime(num):
    switcher = {
        0: '02.01.2022',
        1: '09.01.2022',
        2: '16.01.2022',
        3: '26.01.2022',
        4: '30.01.2022',
        5: '07.02.2022'
    }

    return switcher.get(num, 'Invalid')

# returns a dictionary with all the post dataframes
def importPosts(time):
    path = 'D:\\test\\Sent\\' + time + '\\Reddit Data\\Posts\\'
    postDF = {
        'atheism': None,
        'christianity': None,
        'conservative': None,
        'conspiracy': None,
        'exchristian': None,
        'flatearth': None,
        'liberal': None,
        'lockdownskepticism': None,
        'news': None,
        'politics': None,
        'science': None
    }

    for sub in postDF.keys():
        postDF[sub] = {
            'hot': None,
            'new': None,
            'controversial': None
        }

        for sect in postDF[sub].keys():
            path2 = path + sub + '_' + sect + '.csv'
            postDF[sub][sect] = pd.read_csv(path2)
    return postDF

def importComments(time):
    path = 'D:\\test\\Sent\\' + time + '\\Reddit Data\\Comments\\'

    commentDF = {
        'atheism': None,
        'christianity': None,
        'conservative': None,
        'conspiracy': None,
        'exchristian': None,
        'flatearth': None,
        'liberal': None,
        'lockdownskepticism': None,
        'news': None,
        'politics': None,
        'science': None
    }

    for sub in commentDF.keys():
            path2 = path + sub + '.csv'
            commentDF[sub] = pd.read_csv(path2)
    return commentDF

# returns a list of all users in a comment and a post dictionaries
# takes as inout a post dictionary of dataframes and a comment dictionary of dataframes
# returns a list of all users in those dictionaries
def allUsers(posts, comments):
    users = []
    for sub in posts.keys():
        cmments = comments[sub]
        users.extend(cmments['author'].unique().tolist())
        users.extend(cmments['reply to user'].unique().tolist())

        for sect in posts[sub].keys():
            psts = posts[sub][sect]
            users.extend(psts['author'].unique().tolist())

    uset = set(users)
    users = list(uset)
    return users

# returns a dictionary with the number of replies from each user to every other user on a certain subreddit at a certain timeslice
# takes as input the string represting the name of the subreddit and a dictionary of comment dataframes
# returns a dictionary replies which has usernames as keys. Each key is associated with a different dictionary which also has usernames as keys
# replies[user1][user2] represents the number of replies by user1 to user2
def repliesBetweenUsers(sub, comments):
    # list of all
    subUsers = comments[sub]['author'].unique().tolist()
    subUsers.extend(comments[sub]['reply to user'].unique().tolist())
    subUsers = set(subUsers)

    replies = {} 

    for user in subUsers:
        replies[user] = {}

        userComments = comments[sub].loc[comments[sub]['author'] == user]
        repliees = userComments['reply to user'].tolist()

        for user2 in repliees:
            if user2 in replies[user]:
                replies[user][user2] = replies[user][user2] + 1
            else:
                replies[user][user2] = 1
    
    return replies


def main():
    # time slice that the program processes
    time = getTime(0)

    if time == 'Invalid':
        raise KeyError('The requested timeslice file does not exist.')

    # import post and comment dataframes
    postDataFrames = importPosts(time)
    commentDataFrames = importComments(time)
    
    # lits of all users
 #   users = allUsers(postDataFrames, commentDataFrames)
  #  print(users)

    # number of replies from one user to another
    sub = 'atheism'

    replies = repliesBetweenUsers(sub, commentDataFrames)
    #print(replies)

# in degree

# out degree

# total score

# average score

# controversiality

# sorted list of subreddits active on

# distribution of subreddits active on

# most used words

# tree depth & width

# average score of posts/comments per subreddit

# distribution of posts/comments per subreddit

# most active users per subreddi

if __name__ == "__main__":
    main()