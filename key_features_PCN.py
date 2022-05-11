import pandas as pd
import pickle
import os
from keyfeatures_2_riccardo import *
from userNetworkFunction import createDirectory
from collections import defaultdict
import pandas as pd
import pickle

time = ''
posts = {}
psts = {}
comments = {}
forest = {}
subs = ['atheism',
        'christianity',
        'conservative',
        'conspiracy',
        'exchristian',
        'flatearth',
        'liberal',
        'lockdownskepticism',
        'news',
        'politics',
        'science']

users = {sub: [] for sub in subs}

timeSlice = 0

path = f"Forests/forest_train_{getTime(timeSlice)}.p"
# read the file

with open(path, 'rb') as pfile:
    # unpickle the file
    forest = pickle.load(pfile)

# Only forest is necessary
setup(time, posts, psts, comments, users, forest)

sub = subs

print("Replies between users started............")
# number of replies from one user to another
replies = repliesBetweenUsers(sub)
print("Replies between users done!")
#print(replies)

print("In degree started............")
# in degree
in_degree = in_out_Degree(sub, replies, True)
print("In degree done!")
#print(in_degree)

print("Out degree started............")
# out degree
out_degree = in_out_Degree(sub, replies, False)
print("Out degree done!")
#print(out_degree)

# print("Total scores started............")
# # total scores
# n_posts, n_comments, t_score_posts, t_score_comments = totalScore(sub)
# print("Total scores done!")
# #print(t_score)
# #print(n_comments)

# print("Average scores started............")
# # average score
# a_score_posts, a_score_comments = averageScore(t_score_posts, t_score_comments, n_posts, n_comments, sub)
# print("Average scores done!")
# #print(a_score)

# print("Controversiality started............")
# # controversiality
# p_con, c_con = controversiality(sub)
# print("Controversiality done!")
# #print(p_con)

#sorted list of subreddits active on

# distribution of subreddits active on

# most used words

# tree depth & width
depths, widths = treeDepthWidth(sub)
#print(depths)
#print(widths)

# print("Post/comment ratio started............")
# # post/comment ratio
# p_c_ratio = ratioPostComment(n_posts, n_comments, sub)
# print("Post/comment ratio done!")
#print(p_c_ratio)

# # number of levels in post trees between users' replies
# nodes = nodesBetweenReplies(sub)
# #print(nodes)


# # average score of posts/comments per subreddit
# averagescore = [(su, score_metrics(posts[su])[0]) for su in sub]
# print('when the average is scored')

# # distribution of posts/comments per subreddit
# # averagedist = [activity_distribution(posts[su]) for su in sub]
# print('distributed the posts/comments')
# # most active users per subreddit
# aclist = active_users(forest)
# print('active listed')

kfDict = {}

kfDict['replies between users'] = replies
kfDict['in-degree'] = in_degree
kfDict['out-degree'] = out_degree
# kfDict['nrPosts, nrComments, totalScorePosts, totalScoreComments'] = n_posts, n_comments, t_score_posts, t_score_comments
# kfDict['avgScorePosts, avgScoreComments'] = a_score_posts, a_score_comments
# kfDict['postControversiality, commentControversiality'] = p_con, c_con
kfDict['tree depth'] = depths
kfDict['tree width'] = widths
# kfDict['postCommentRatio'] = p_c_ratio
# kfDict["nr levels in post trees between users' replies"] = nodes
# kfDict['average post/comment score'] = averagescore
# kfDict['most active users per subreddit'] = aclist


resultsPath = f"Results/{getTime(timeSlice)}/"
createDirectory(resultsPath)

with open(resultsPath + f'key_features_PCN.pickle', 'wb') as f:
    pickle.dump(kfDict, f, protocol=pickle.HIGHEST_PROTOCOL)