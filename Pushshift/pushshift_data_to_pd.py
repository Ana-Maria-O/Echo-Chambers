# -*- coding: utf-8 -*-
"""
Created on Sun May  1 15:23:58 2022

@author: 20192373
"""
import pandas as pd
import pickle
import os

The_Donald_comments = pd.read_csv('The_Donald/The_Donald_comments.csv')
The_Donald_posts = pd.read_csv('The_Donald/The_Donald_posts.csv')

News_comments = pd.read_csv('News/News_comments.csv')
News_posts = pd.read_csv('News/News_posts.csv')

CMV_comments = pd.read_csv('Changemyview/Changemyview_comments.csv')
CMV_posts = pd.read_csv('Changemyview/Changemyview_posts.csv')

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
posts = {'The_Donald': The_Donald_posts, 'News': News_posts, 'CMV': CMV_posts}
psts = {}
comments = {'The_Donald': The_Donald_comments, 'News': News_comments, 'CMV': CMV_comments}
users = []
forest = {}
subs = ['The_Donald', 'News', 'CMV']


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
        users[sub].extend(cmments['reply to'].unique().tolist())

        # for each section of posts: hot, new, controversial get all authors of posts in this section
        users[sub].extend(psts[sub]['author'].unique().tolist())

        # remove duplicate entries 
        uset = set(users[sub])
        users[sub] = list(uset)


    return users

print("Start setup ........")
print("Start importing posts ........")

posts = posts
psts = allPosts(posts.keys())

print("Posts imported!")
print("Start importing comments ........")

comments = comments
for sub in subs:
    comments[sub] = comments[sub].drop(comments[sub][comments[sub].author == '[deleted]'].index)
    comments[sub] = comments[sub].drop(comments[sub][comments[sub].author == 'AutoModerator'].index)
users = allUsers(posts.keys())

print("Comments imported!")
print("Start creating forest ........")

# forest dictionary
forest = createForest()

path= f"Forests/PushShift/"

# Create directories if necessary
existsPath = os.path.exists(path)

if not existsPath:
    # Create a new directory because it does not exist 
    os.makedirs(path)

# Save the network
with open(path + f'forest_new.pickle', 'wb') as f:
    pickle.dump(forest, f, protocol=pickle.HIGHEST_PROTOCOL)