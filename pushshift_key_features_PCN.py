import pandas as pd
import pickle
import numpy as np
import os
from keyfeatures_2_riccardo import *
from userNetworkFunction import createDirectory

subs = ['conspiracy', 'enoughtrumpspam']

#The_Donald_comments = pd.read_csv('Pushshift/The_Donald/The_Donald_comments.csv')
#The_Donald_posts = pd.read_csv('Pushshift/The_Donald/The_Donald_posts.csv')

#News_comments = pd.read_csv('Pushshift/News/News_comments.csv')
#News_posts = pd.read_csv('Pushshift/News/News_posts.csv')

#CMV_comments = pd.read_csv('Pushshift/Changemyview/Changemyview_comments.csv')
#CMV_posts = pd.read_csv('Pushshift/Changemyview/Changemyview_posts.csv')

# path = os.path.dirname(__file__) + '/Pickle/'

# existsPath = os.path.exists(path)

# if not existsPath:
#     # Create a new directory because it does not exist 
#     os.makedirs(path)

# with open(path + 'news_comments.pickle', 'wb') as f:
#         pickle.dump(News_comments, f, protocol=pickle.HIGHEST_PROTOCOL)



from collections import defaultdict
import pandas as pd
import pickle
import json

time = ''


posts = {}
comments = {}
for sub in subs:
    filename = 'Pushshift/' + sub + '/' + sub
    if sub == 'Changemyview':
        posts['CMV'] = pd.read_csv(filename + '_posts.csv')
        comments['CMV'] = pd.read_csv(filename + '_comments.csv')
    else:
        posts[sub] = pd.read_csv(filename + '_posts.csv')
        comments[sub] = pd.read_csv(filename + '_comments.csv')
    #posts = {'The_Donald': The_Donald_posts, 'News': News_posts, 'CMV': CMV_posts}
    #comments = {'The_Donald': The_Donald_comments, 'News': News_comments, 'CMV': CMV_comments}

psts = {}


for sub in subs:
    print(f"sub {sub} nr posts: {len(posts[sub])}")
#posts = {'The_Donald': The_Donald_posts, 'News': News_posts, 'CMV': CMV_posts}
#psts = {}
#comments = {'The_Donald': The_Donald_comments, 'News': News_comments, 'CMV': CMV_comments}

users = []
forest = {}

for sub in subs:
    print(len(posts[sub]))

posts = {'explainlikeimfive': ELI5_posts, 'askscience': AskScience_posts}
psts = {}
comments = {'explainlikeimfive': ELI5_comments, 'askscience': AskScience_comments}
users = []
forest = {}
subs = ['askscience', 'explainlikeimfive']
# print(len(posts['News']))
# print(len(posts['CMV']))



# Linked list to represent a tree
# tree.root is the root of a tree
# tree.root.id is the id of the post at the root
# tree.root.next is a list containing the subtrees rooted in the direct responses to the root post
class Tree:
    def __init__(self, post):
        self.root = post

    def __repr__(self) -> str:
        node = self.head
        nodes = []
        while node is not None:
            nodes.append(node.data)
            node = node.next
        nodes.append("None")
        return " -> ".join(nodes)

# Node in tree
class Node:
    def __init__(self, data, auth, score, controversial, depth=-1):
        self.id = data
        self.auth = auth
        self.score = score
        self.controversial = controversial
        self.depth = depth
        self.next = []

    def __repr__(self):
        return (self.id + " by " + self.auth + " score: " + str(self.score))

# returns a dictionary of dataframes with all the posts from the mentioned subreddits
def allPosts(subs):
    all_posts = {}

    for sub in subs:
        # choose which subreddit to aggregate posts from
        psts = posts[sub]
        all_posts[sub] = posts[sub]

        # get rid of duplicate entries
        all_posts[sub] = all_posts[sub].drop_duplicates(subset='id', keep='last')

    return all_posts

# add all comments from a post to its tree
def addCommentsToTree(node, comms, sub, root=True):
    replies = []

    # gather all the replies to the current node
    if root:
        replies = comms.loc[comms['reply to'] == node.id] # CHANGED!!!!!!! for pushshift
    else:
        replies = comms.loc[comms['reply to'] == node.id]

    # if the node has replies
    if replies.shape[0] > 0:
        # get all the ids of the replies
        replies_id = replies['full_id'].tolist()

        # for each reply, add it and the thread it spawns to the tree
        for reply in replies_id:
            # find the row in comms corresponding to the reply
            place = comms.loc[comms['full_id'] == reply]

            # extract the information the node will store
            auth = place.author.item()
            score = place.score.item()
            controversial = place.controversial.item()

            # create a reply node
            r_node = Node(reply, auth, score, controversial)

            # add the rest of the thread the reply spawns to the tree
            r_node = addCommentsToTree(r_node, comms, sub, False)

            # add the reply node to the original node's list of replies
            node.next.append(r_node)

    return node

# uses the posts and comments dictionaries to create a forest containing all post trees
# returns a forestDict dictionary such that forestDict[subreddit][post] is the tree with post as its root, 
# where post was posted on subreddit sub
def createForest():
    forestDict = dict.fromkeys(posts.keys(), None)

    # for each subreddit
    for sub in forestDict.keys():
        print(sub)

        # get all the comments from sub
        comms = comments[sub]

        forestDict[sub] = dict.fromkeys(psts[sub]['full_id'].tolist(), None)

        # make a tree for each post in the subreddit
        for post in forestDict[sub].keys():
            # get the row from psts corresponding to the post
            place = psts[sub].loc[psts[sub]['full_id'] == post]

            controversial = None

            # create the tree corresponding to the post and its comments
            forestDict[sub][post] = Tree(Node(post, place.author.item(), place.score.item(), controversial))
            forestDict[sub][post] = addCommentsToTree(forestDict[sub][post].root, comms.loc[comms['post id'] == post], sub)

    return forestDict

# returns the modified input dictionary replies of number of replies such that 
# the replies given in the tree rooted at current are taken into account
def addReplies(replies, current):
    # if there are any replies to current
    if len(current.next) > 0:
            for reply in current.next:
                # update/instantiate the number of replies by the author of the reply to the author of current
                if reply.auth in replies and current.auth in replies[reply.auth]:
                    replies[reply.auth][current.auth] += 1
                else:
                    replies[reply.auth][current.auth] = 1
                
                # add the replies from further down in the comment thread that continues from reply
                replies = addReplies(replies, reply)
    
    return replies

def allUsers(subs):
    users = {}
    
    # for each subreddit, add all its active users to the list
    for sub in subs:
        # choose which subreddit to pick the comments from
        cmments = comments[sub]

        users[sub] = []

        # get all authors of comments
        users[sub].extend(cmments['author'].unique().tolist())

        # get all people who were replied to
        # users[sub].extend(cmments['reply to'].unique().tolist())

        # for each section of posts: hot, new, controversial get all authors of posts in this section
        users[sub].extend(psts[sub]['author'].unique().tolist())

        # remove duplicate entries 
        uset = set(users[sub])
        users[sub] = list(uset)


    return users

def countSandwiches(node):

    sandwhichCounter = 0
    possibleSandwiches = 0

    if len(node.next) != 0:
        for child in node.next:
            for grandChild in child.next:

                possibleSandwiches += 1

                # Check if sandwich occurs
                if grandChild.auth == node.auth:
                    sandwhichCounter += 1

    return sandwhichCounter, possibleSandwiches

def countTotalSandwiches(root):
    totalSandwhichCounter, totalPossibleSandwiches = countSandwiches(root)

    for child in root.next:
        temp = countTotalSandwiches(child)
        totalSandwhichCounter += temp[0]
        totalPossibleSandwiches += temp[1]


    return totalSandwhichCounter, totalPossibleSandwiches


def sandwiches(forest):
    # forestDict[subreddit][post]
    sandwichDictionary = {sub: dict() for sub in subs}

    for sub in subs:
        for post in forest[sub].keys():
            root = forest[sub][post]
            temp = countTotalSandwiches(root)

            sandwichDictionary[sub][post] = dict()
            sandwichDictionary[sub][post]["counted"] = temp[0]
            sandwichDictionary[sub][post]["possible"] = temp[1]



    return sandwichDictionary

print("Start setup ........")
print("Start importing posts ........")

posts = posts
psts = allPosts(posts.keys())

print("Posts imported!")
print("Start importing comments ........")

comments = comments

postcommentidToAuthor = {}
for sub in subs:
    comments[sub] = comments[sub].drop(comments[sub][comments[sub].author == '[deleted]'].index)
    comments[sub] = comments[sub].drop(comments[sub][comments[sub].author == 'AutoModerator'].index)
    
    # for postid in psts[sub]['full_id']:
    #     postcommentidToAuthor[postid] = psts[sub][psts[sub]['full_id'] == postid]['author']
    # for commentid in comments[sub]['full_id']:
    #     postcommentidToAuthor[commentid] = comments[sub][comments[sub]['full_id'] == commentid]['author'][0]


users = allUsers(posts.keys())


# print("Comments imported!")
print("Start creating forest ........")


path = "Forests//PushShift//forest_for_testing_dataset" + ".pickle"

#path = "Forests//PushShift//forest_askscience_explainlikeimfive" + ".pickle"

# read the file

pfile = open(path, 'rb')

# unpickle the file
forest = pickle.load(pfile)
forest1 = {}
for sub in subs:
    forest1[sub] = forest[sub]
forest = forest1

# close the file
pfile.close()

sub = posts.keys()

setup(time, posts, psts, comments, users, forest)


print("Replies between users started............")
# number of replies from one user to another
# replies = repliesBetweenUsers(sub)
print("Replies between users done!")
#print(replies)

print("In degree started............")
# in degree
# in_degree = in_out_Degree(sub, replies, True)
print("In degree done!")
#print(in_degree)

print("Out degree started............")
# out degree
# out_degree = in_out_Degree(sub, replies, False)
print("Out degree done!")
#print(out_degree)

print("Total scores started............")
# total scores
# n_posts, n_comments, t_score_posts, t_score_comments = totalScore(sub)
print("Total scores done!")
#print(t_score)
#print(n_comments)

print("Average scores started............")
# average score
# a_score_posts, a_score_comments = averageScore(t_score_posts, t_score_comments, n_posts, n_comments, sub)
print("Average scores done!")
#print(a_score)

print("Controversiality started............")
# controversiality
# p_con, c_con = controversiality(sub)
print("Controversiality done!")

# print("Replies between users started............")
# # number of replies from one user to another
# replies = repliesBetweenUsers(sub)
# print("Replies between users done!")
#print(replies)

print("Sandwiches between users started............")
sandwichesDict = sandwiches(forest)

# Convert to decimal values for plotting
sandwichesDictValues = {s: dict() for s in subs}
for s in subs:
    for post in sandwichesDict[s].keys():
        if sandwichesDict[s][post]["possible"] == 0:
            sandwichesDictValues[s][post] = None
        else:
            sandwichesDictValues[s][post] = sandwichesDict[s][post]["counted"]/sandwichesDict[s][post]["possible"]

print("Sandwiches between users done!")

# print("In degree started............")
# # in degree
# in_degree = in_out_Degree(sub, replies, True)
# print("In degree done!")
# #print(in_degree)

# print("Out degree started............")
# # out degree
# out_degree = in_out_Degree(sub, replies, False)
# print("Out degree done!")
# #print(out_degree)

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

#print(p_con)

#sorted list of subreddits active on

# distribution of subreddits active on

# most used words

# tree depth & width
depth, width, width_dist, depth_dist = treeDepthWidth(sub)
#print(depths)
#print(widths)

print("Post/comment ratio started............")
# post/comment ratio
# p_c_ratio = ratioPostComment(n_posts, n_comments, sub)
print("Post/comment ratio done!")
#print(p_c_ratio)

# number of levels in post trees between users' replies
# nodes = nodesBetweenReplies(sub)
#print(nodes)

# print("Post/comment ratio started............")
# # post/comment ratio
# p_c_ratio = ratioPostComment(n_posts, n_comments, sub)
# print("Post/comment ratio done!")
# #print(p_c_ratio)

# # number of levels in post trees between users' replies
# nodes = nodesBetweenReplies(sub)
# #print(nodes)


# print(posts, type(posts))
# print()
# print(sub, type(sub))

# average score of posts/comments per subreddit
# averagescore = [(su, score_metrics(posts[su])[0]) for su in sub]
print('when the average is scored')

# distribution of posts/comments per subreddit
# averagedist = [activity_distribution(posts[su]) for su in sub]
print('distributed the posts/comments')
# most active users per subreddit
# aclist = active_users(forest)
print('active listed')

# # average score of posts/comments per subreddit
# averagescore = [(su, score_metrics(posts[su])[0]) for su in sub]
# print('when the average is scored')

# # distribution of posts/comments per subreddit
# # averagedist = [activity_distribution(posts[su]) for su in sub]
# print('distributed the posts/comments')
# # most active users per subreddit
# aclist = active_users(forest)
# print('active listed')


def final_KFs(sub):
    sub_comments = comments[sub]
    sub_posts = posts[sub]
    comment_controversiality = {}
    comment_score = {}
    post_nr_comments = {}
    post_scores = {}
    for postID in list(sub_posts['full_id'].unique()):
        post_score = sub_posts[sub_posts['full_id']==postID]['score'] 
        post_comments = sub_comments[sub_comments['post id']==postID]
        nr_comments = len(post_comments)
        if nr_comments > 0:
            controversiality = post_comments[post_comments.controversial.isin([0,1])]['controversial']  #[post_comments['controversial'] ]['controversial']  # not always defined
            avg_comment_controversiality = np.mean(controversiality)
            median_comment_controversiality = np.median(controversiality)
            score = post_comments['score']
            avg_comment_score = np.mean(score)
            median_comment_score = np.median(score)

            comment_controversiality[postID] = (avg_comment_controversiality, median_comment_controversiality)
            comment_score[postID] = (avg_comment_score, median_comment_score)
            post_nr_comments[postID] = nr_comments
            post_scores[postID] = post_score
        else:
            pass
    return nr_comments, comment_score, comment_controversiality, post_scores

def countSandwiches(node):

    sandwhichCounter = 0
    possibleSandwiches = 0

    if len(node.next) != 0:
        for child in node.next:
            for grandChild in child.next:

                possibleSandwiches += 1

                # Check if sandwich occurs
                if grandChild.auth == node.auth:
                    sandwhichCounter += 1

    return sandwhichCounter, possibleSandwiches

def countTotalSandwiches(root):
    totalSandwhichCounter, totalPossibleSandwiches = countSandwiches(root)

    for child in root.next:
        temp = countTotalSandwiches(child)
        totalSandwhichCounter += temp[0]
        totalPossibleSandwiches += temp[1]


    return totalSandwhichCounter, totalPossibleSandwiches


def sandwiches(forest):
    # forestDict[subreddit][post]
    sandwichDictionary = {sub: dict() for sub in subs}

    for sub in subs:
        for post in forest[sub].keys():
            root = forest[sub][post]
            temp = countTotalSandwiches(root)

            sandwichDictionary[sub][post] = dict()
            sandwichDictionary[sub][post]["counted"] = temp[0]
            sandwichDictionary[sub][post]["possible"] = temp[1]



    return sandwichDictionary

print("Sandwiches between users started............")
sandwichesDict = sandwiches(forest)

# Convert to decimal values for plotting
sandwichesDictValues = {s: dict() for s in subs}
for s in subs:
    for post in sandwichesDict[s].keys():
        if sandwichesDict[s][post]["possible"] == 0:
            sandwichesDictValues[s][post] = None
        else:
            sandwichesDictValues[s][post] = sandwichesDict[s][post]["counted"]/sandwichesDict[s][post]["possible"]

print("Sandwiches between users done!")

# finalNrComments, finalCommentScore, finalCommentControversiality, finalPostScores = {}, {}, {}, {}
# for sub in subs:
#     subNrComments, subFinalCommentScore, subFinalCommentControversiality, subFinalPostScores = final_KFs(sub)
#     finalNrComments[sub] = subNrComments
#     finalCommentScore[sub] = subFinalCommentScore
#     finalCommentControversiality[sub] = subFinalCommentControversiality
#     finalPostScores[sub] = subFinalPostScores

kfDict = {}

kfDict['sandwiches'] = sandwichesDict
kfDict['sandwichesValues'] = sandwichesDictValues
# kfDict['replies between users'] = replies
# kfDict['in-degree'] = in_degree
# kfDict['out-degree'] = out_degree
# kfDict['nrPosts, nrComments, totalScorePosts, totalScoreComments'] = n_posts, n_comments, t_score_posts, t_score_comments
# kfDict['avgScorePosts, avgScoreComments'] = a_score_posts, a_score_comments
# kfDict['postControversiality, commentControversiality'] = p_con, c_con
kfDict['tree depth'] = depth
kfDict['tree width'] = width
kfDict['tree depth dist'] = depth_dist
kfDict['tree width dist'] = width_dist
# kfDict['postCommentRatio'] = p_c_ratio
# kfDict["nr levels in post trees between users' replies"] = nodes
# kfDict['average post/comment score'] = averagescore
# kfDict['most active users per subreddit'] = aclist

# kfDict['final avg comment controversiality'] = finalCommentControversiality # dict with as keys first sub, then post id and with values the avg comment controversiality
# kfDict['final avg comment score'] = finalCommentScore # dict with as keys first sub, then the post id and with values (avg comments score, post score)
# kfDict['final nr comments'] = finalNrComments # dict with as keys first sub, then post id and with values the nr of comments
# kfDict['final post score'] = finalPostScores


resultsPath = f"Results/Pushshift/"
createDirectory(resultsPath)

print(list(kfDict.keys()))

# print(kfDict['average post/comment score'])


with open(resultsPath + f'KFs_PCN_askscience_explainlikeimfive.pickle', 'wb') as f:

    pickle.dump(kfDict, f, protocol=pickle.HIGHEST_PROTOCOL)