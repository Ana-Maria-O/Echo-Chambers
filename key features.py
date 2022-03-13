from typing import Counter
import pandas as pd
import numpy as np

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
    def __init__(self, data):
        self.id = data
        self.next = []

    def __repr__(self):
        return self.id

# returns a dataframe with all the posts from the mentioned sub from the selected sections
def allPosts(hot, new, controversial, sub):
    all_posts = pd.DataFrame()

    # choose which subreddit to aggregate posts from
    psts = posts[sub]

    if hot:
        all_posts = pd.concat([all_posts, psts['hot']])

    if new:
        all_posts = pd.concat([all_posts, psts['new']])

    if controversial:
        all_posts = pd.concat([all_posts, psts['controversial']])

    all_posts = all_posts.drop_duplicates(subset='id', keep='last')
    return all_posts

def addCommentsToTree(node, comms, sub, above=0):
    
    replies = []
    #print(node)
    if above == 0:
        replies = comms.loc[comms['reply to comment'].isnull()]
    else:
        replies = comms.loc[comms['reply to comment'] == node.id]

    #print(replies.shape[0])
    if replies.shape[0] > 0:
        replies_id = replies['id'].tolist()

        for reply in replies_id:
            r_node = Node(reply)
            r_node = addCommentsToTree(r_node, comms, sub, 1)
            node.next.append(r_node)

    return node

# uses the posts and comments dictionaries to create a forest containing all post trees
# returns a forestDict dictionary such that forestDict[subreddit][post] is the tree with post as its root, 
# where post was posted on subreddit
def createForest():
    forestDict = dict.fromkeys(posts.keys(), None)
    
    for sub in forestDict.keys():
        print(sub)
        comms = comments[sub].drop_duplicates(subset='id', keep='last')
        psts = allPosts(True, True, True, sub)
        forestDict[sub] = dict.fromkeys(psts['id'], None)

        for post in forestDict[sub].keys():
            forestDict[sub][post] = Tree(Node(post))
            forestDict[sub][post] = addCommentsToTree(forestDict[sub][post].root, comms.loc[comms['post id'] == post], sub)

    return forestDict

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
# takes as input a post dictionary of dataframes and a comment dictionary of dataframes
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

# computes the depth of a post tree and the number of nodes at each depth, where the depth of the root is given
# and the widths of the tree at each level of depth
# takes as input a string id representing the id of the root post, 
# comms the comment dataframe from which to extract the replies to the post,
# depth which is the depth of the root and widths which is a dictionary of all the widths of the tree
# returns the depth of the subtree with id as its root and the dictionary witdths such that such that
# widths[index] is the number of nodes of depth index
def Depth(id, comms, depth, widths):
    # find all direct replies to the root post
    print(id)
    if depth == 0:
        replies = comms.loc[comms['reply to comment'].isnull()]
    else:
        replies = comms.loc[comms['reply to comment'] == id]
    print(replies.shape[0])
    if depth in widths:
        widths[depth] += replies.shape[0]
    else:
        widths[depth] = replies.shape[0]

    if replies.shape[0] > 0:
        # compute depth of the deepest subtree
        depth += 1
        sub_depth = depth
        replies_id = replies['id'].tolist()

        # compute depth of each subtree
        for tree in replies_id:
            tree_depth, widths = Depth(tree, comms, depth, widths)
            if tree_depth > sub_depth:
                sub_depth = tree_depth

        return sub_depth, widths
    else:
        return depth, widths

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

# returns a dictionary of all users in a subreddit and their controversiality
# takes as input a string which is the name of the subreddit
# returns a dictionary con such that con[user] is the controversilaity score of that user
def controversiality(sub):
    # list of all users in the subreddit
    users = allUsers(True, True, True, sub)

    # dictionary of controversiality
    con = dict.fromkeys(users, 0)

    # check controversial comments
    c_comments = comments[sub].loc[comments[sub]['controversial'] == 1] # all controversial comments in subreddit

    # for each controversial comment update the controversial scores in con
    for index, row in c_comments.iterrows():
        auth = row['author']
        con[auth] += 1

    # check controversial posts
    c_posts = allPosts(False, False, True, sub) # all controversial posts in subreddit

    # for each controversial comment update the controversial scores in con
    for index, row in c_posts.iterrows():
        auth = row['author']
        con[auth] += 1

    return con

# returns a dictionary with the depths and a dictionary with the heights of all trees corresponding to posts on a subreddit
# takes as input a string which is the name of the subreddit
# returns dictionaries depth and width such that depth[post] is the depth of the tree rooted at post and width[post] is the
# width of the tree rooted at post
def treeDepthWidth(sub):
    # all posts in subreddit
    all_posts = allPosts(True, True, True, sub)

    # all comments from subreddit
    all_comments = comments[sub]

    # all ids of all posts in subreddit
    post_ids = all_posts['id'].tolist()

    # initiate the depth and width dictionaries
    depth = dict.fromkeys(post_ids, 0)
    width = dict.fromkeys(post_ids, 0)

    # for each post, compute the depth and widtyh of its tree
    for post in post_ids:
        widths = {}
        # compute the depth of the post tree and all its different widths
        depth[post], widths = Depth(post, all_comments.loc[all_comments['post id'] == post], 0, widths)

        # find the maximum width of the post tree
        width[post] = max(widths.values())

    return depth, width

# returns a dictionary with every active user on a subreddit and their post/comment ratio
# takes as input a string sub which is the name of the subreddit
# returns a dictionary pcRatio such that pcRatio[user] is the post/comment ratio of user on the subreddit sub
def ratioPostComment(sub):
    # get a list of all users in the subreddit
    users = allUsers(True, True, True, sub)

    #initialize pcRatio
    pcRatio = dict.fromkeys(users, 1)

    # get a list of all posts in the subeddit
    psts = allPosts(True, True, True, sub)
    psts = psts.drop_duplicates(subset='id', keep='last')

    # get all comments in the sub
    cmmts = comments[sub]

    for user in users:
        # all posts made by user
        uPosts = psts.loc[psts['author'] == user]

        # number of posts made by user
        uPosts_num = uPosts.shape[0]

        # all comments made by user
        uComments = cmmts.loc[cmmts['author'] == user]

        # number of comments made by user
        uComments_num = uComments.shape[0]

        # compute post/comment ratio

        if uComments_num == 0:
            pcRatio[user] = 1
        else:
            pcRatio[user] = uPosts_num / uComments_num
    
    return pcRatio

# returns a dictionary with every active user on a subreddit, the posts they made/commented on and a list of
# how many nodes there are on a thread between their replies
# takes as input a string which is the name of the subreddit
# returns a dictionary nodes such that nodes[user][post] is a list of the different amount of nodes
# in a thread between user's replies on post
def nodesBetweenReplies(sub):
    # list of all posts on the subreddit
    psts = allPosts(True, True, True, sub)
    psts = psts.drop_duplicates(subset='id', keep='last')

    # list of all comments on the subreddit
    cmmts = comments[sub]

    # initialize nodes
    nodes = {}

    #for post in posts:
        #nodes = computeNodes(nodes, sub, post, 0, cmmts)

# time slice that the program processes
time = getTime(0)

if time == 'Invalid':
    raise KeyError('The requested timeslice file does not exist.')

# import post and comment dataframes
print("Start setup ........")
print("Start importing posts ........")
posts = importPosts(time)
print("Posts imported!")
print("Start importing comments ........")
comments = importComments(time)
print("Comments imported!")
print("Start creating forest ........")

# forest dictionary
forest = createForest()
print("Forest created!")
print("Setup done!")


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
    #n_posts_comments, t_score = totalScore(sub)
    #print(t_score)
    #print(n_posts_comments)

    # average score
    #a_score = averageScore(t_score, n_posts_comments)
    #print(a_score)

    # controversiality
    #con = controversiality(sub)
    #print(con)

    #sorted list of subreddits active on

    # distribution of subreddits active on

    # most used words

    # tree depth & width
    #depths, widths = treeDepthWidth(sub)
    #print(depths)
    #print(widths)

    # post/comment ratio
    #p_c_ratio = ratioPostComment(sub)
    #print(p_c_ratio)

    # number of levels in post trees between users' replies
    #nodes = nodesBetweenReplies(sub)
    #print(nodes)

# average score of posts/comments per subreddit

# distribution of posts/comments per subreddit

# most active users per subreddi

if __name__ == "__main__":
    main()