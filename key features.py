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

# returns a dictionary with all the comment dataframes
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
def allUsers(posters, commenters, repliees, sub):
    users = []
    # choose which subreddit to pick the comments from
    cmments = comments[sub]
        
    if commenters:
        # get all authors of comments
        users.extend(cmments['author'].unique().tolist())

    if repliees:
        # get all people who were replied to
        users.extend(cmments['reply to user'].unique().tolist())

    if posters:
        # for each section of posts: hot, new, controversial
        for sect in posts[sub].keys():
            psts = posts[sub][sect]

            # get all authors of posts in this section
            users.extend(psts['author'].unique().tolist())

    uset = set(users)
    users = list(uset)
    return users

# returns a dictionary with the number of replies from each user to every other user on a certain subreddit at a certain timeslice
# takes as input a string which is the name of the subreddit
# returns a dictionary replies which has usernames as keys. Each key is associated with a different dictionary which also has usernames as keys
# replies[user1][user2] represents the number of replies by user1 to user2
def repliesBetweenUsers(sub):
    # list of all active users who wrote comments or were replied to
    subUsers = allUsers(False, True, True, sub)
    subUsers = set(subUsers)

    replies = {} 

    # for each user compute the users that they replied to and how many times
    for user in subUsers:
        replies[user] = {}

        # all comments user replied to
        userComments = comments[sub].loc[comments[sub]['author'] == user]

        # log of the users replied to
        repliees = userComments['reply to user'].tolist()

        # for each instance of user repying
        for user2 in repliees:

            # increase number of replies to user2
            if user2 in replies[user]:
                replies[user][user2] = replies[user][user2] + 1
            else:
                # initiate first reply to user2
                replies[user][user2] = 1
    
    return replies

# returns a dictionary of all users and their in-degree or their out-degree
# takes as input a string which is the name of the subreddit and a boolean ind such that
# ind == true => returns in-degree dictionary, else returns out-degree dictionary
# returns a dictionary deg such that deg[user] is the value of user's in-degree/out-degree
def in_out_Degree(sub, ind):

    # the list of all active users in the subreddit
    users = allUsers(True, True, True, sub)

    # dictionary holding the indegrees of users
    deg = dict.fromkeys(users, 0)

    # all instances where a user was replied to/ replied to someone
    if ind:
        r_instances = comments[sub]['reply to user'].tolist()
    else:
        r_instances = comments[sub]['author'].tolist()

    # for every reply update the indegree dictionary
    for reply in r_instances:
        deg[reply] = deg[reply] + 1

    return deg

# returns a dictionary of all users in a subreddit and their total score in that subreddit and a dictionary
# which keeps track of how many posts and comments each user has made
# takes as input a string which is the name of the subreddit
# returns a dictionary t_scores such that t_scores[user] is the total score of user in the subreddit and a dictionary
# n_posts where n_posts[user] is the total number of posts and comments that user has made
def totalScore(sub):
    # list of all active users in the subreddit
    users = allUsers(True, True, True, sub)

    # dictionary with all users' scores
    t_scores = dict.fromkeys(users, 0)

    # dictionary with number of all users' posts and comments
    n_posts = dict.fromkeys(users, 0)

    # gather all posts scores and all number of posts
    for sect in posts[sub].keys():
        for index, row in posts[sub][sect].iterrows():
            auth = row['author']
            t_scores[auth] += row['score']
            n_posts[auth] += 1

    # gather all comment scores
    for index, row in comments[sub].iterrows():
        auth = row['author']
        t_scores[auth] += row['score']
        n_posts[auth] += 1

    return n_posts, t_scores

# returns a dictionary of all users in a subset of users and their average score for the subreddits taken into account
# takes as input a dictionary of all users and their scores and a dictionary of all users and the number of comments and posts they made
# returns dicitonary avg such that avg[user] is the average score of that user
def averageScore(scores, numbers):
    avg = {}
    for user in scores.keys():
        if numbers[user] == 0:
            avg[user] = 0
        else:
            avg[user] = scores[user] / numbers[user]
        
    return avg

# time slice that the program processes
time = getTime(0)

if time == 'Invalid':
    raise KeyError('The requested timeslice file does not exist.')

# import post and comment dataframes
posts = importPosts(time)
comments = importComments(time)

def main():

    # list of all users
    #for subr in comments.keys():
    #    users = allUsers(True, True, True, subr)
    #print(users)

    # subreddit
    sub = 'atheism'

    # number of replies from one user to another
    #replies = repliesBetweenUsers(sub)
    #print(replies)

    # in degree
    #in_degree = in_out_Degree(sub, True)
    #print(in_degree)

    # out degree
    #out_degree = in_out_Degree(sub, False)
    #print(out_degree)

    # total score
    n_posts_comments, t_score = totalScore(sub)
    #print(t_score)
    #print(n_posts_comments)

    # average score
    a_score = averageScore(t_score, n_posts_comments)
    print(a_score)

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