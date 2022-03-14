from collections import defaultdict
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
    def __init__(self, data, auth, score):
        self.id = data
        self.auth = auth
        self.score = score
        self.next = []

    def __repr__(self):
        return (self.id + " by " + self.user)

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

    if above == 0:
        replies = comms.loc[comms['reply to comment'].isnull()]
    else:
        replies = comms.loc[comms['reply to comment'] == node.id]

    if replies.shape[0] > 0:
        replies_id = replies['id'].tolist()

        for reply in replies_id:
            place = comms.loc[comms['id'] == reply]

            auth = place.author.item()
            score = place.score.item()
            r_node = Node(reply, auth, score)
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
        comms = comments[sub]
        forestDict[sub] = dict.fromkeys(psts['id'], None)

        for post in forestDict[sub].keys():
            place = psts.loc[psts['id'] == post]
            forestDict[sub][post] = Tree(Node(post, place.author.item(), place.score.item()))
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
        5: '07.02.2022',
        6: '14.02.2022',
        7: '20.02.2022',
        8: '28.02.2022',
        9: '06.03.2022',
        10: '13.03.2022'
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
            commentDF[sub] = commentDF[sub].drop_duplicates(subset='id', keep='last')
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
        # for each section of posts: hot, new, controversial get all authors of posts in this section
        users.extend(psts['author'].unique().tolist())

    # make sure the entries in the list of users are unique
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
def Depth(node, depth, widths):
    # find all direct replies to the root post
    replies = node.next

    # update the witdh at current depth
    if depth in widths:
        widths[depth] += len(replies)
    else:
        widths[depth] = len(replies)

    if len(replies) > 0:
        # compute depth of the deepest subtree
        sub_depth = depth

        # compute depth of each subtree
        for nextNode in replies:
            tree_depth, widths = Depth(nextNode, depth + 1, widths)
            if tree_depth > sub_depth:
                sub_depth = tree_depth

        return sub_depth, widths
    else:
        return depth, widths

# returns the modified input dictionary of number of replies such that 
# the replies given in the tree rooted at root are taken into account
def addReplies(replies, current):
    if len(current.next) > 0:
            for reply in current.next:

                if reply.auth in replies and current.auth in replies[reply.auth]:
                    replies[reply.auth][current.auth] += 1
                else:
                    replies[reply.auth][current.auth] = 1
                
                replies = addReplies(replies, reply)
    
    return replies

# returns a dictionary with the number of replies from each user to every other user on a certain subreddit at a certain timeslice
# takes as input a string which is the name of the subreddit
# returns a dictionary replies which has usernames as keys. Each key is associated with a different dictionary which also has usernames as keys
# replies[user1][user2] represents the number of replies by user1 to user2
def repliesBetweenUsers(sub):
    subF = forest[sub]
    replies = defaultdict(dict) 

    for post in subF.keys():
        # root of the subtree
        replies = addReplies(replies, subF[post])

    return replies
                
# returns a dictionary of all users and their in-degree or their out-degree
# takes as input a string which is the name of the subreddit, the dictionary replies of number of replies and a boolean ind such that
# ind == true => returns in-degree dictionary, else returns out-degree dictionary
# returns a dictionary deg such that deg[user] is the value of user's in-degree/out-degree
def in_out_Degree(sub, replies, ind):
    # the list of all active users in the subreddit
    users = allUsers(True, True, True, sub)

    # dictionary holding the indegrees/outdegrees of users
    deg = dict.fromkeys(users, 0)

    for user1 in replies.keys():
        for user2 in replies[user1]:
            if ind:
                deg[user2] += replies[user1][user2]
            else:
                deg[user1] += replies[user1][user2]

    return deg

# returns a dictionary of all users in a subreddit and their total score in that subreddit and a dictionary
# which keeps track of how many posts and comments each user has made
# takes as input a string which is the name of the subreddit
# returns a dictionary t_scores such that t_scores[user] is the total score of user in the subreddit and a dictionary
# n_posts where n_posts[user] is the total number of posts and comments that user has made
def totalScore(sub):
    # list of all users who made at least one post
    p_users = allUsers(True, False, False, sub)

    # list of all users who made at least one comment
    c_users = allUsers(False, True, False, sub)

    # dictionary with all users' post scores
    pt_scores = dict.fromkeys(p_users, 0)

    # dictionary with all users' comment scores
    ct_scores = dict.fromkeys(c_users, 0)

    # dictionary with number of all users' posts
    pn_posts = dict.fromkeys(p_users, 0)

    # dictionary with number of all users' comments
    cn_posts = dict.fromkeys(c_users, 0)

    # gather all posts scores and all number of posts
    for sect in posts[sub].keys():
        for _, row in posts[sub][sect].iterrows():
            auth = row['author']
            pt_scores[auth] += row['score']
            pn_posts[auth] += 1

    # gather all comment scores
    for index, row in comments[sub].iterrows():
        auth = row['author']
        ct_scores[auth] += row['score']
        cn_posts[auth] += 1

    return pn_posts, cn_posts, pt_scores, ct_scores

# returns a dictionary of all users in a subset of users and their average score for the subreddits taken into account
# takes as input a dictionary of all users and their scores and a dictionary of all users and the number of comments and posts they made
# returns dicitonary avg such that avg[user] is the average score of that user
def averageScore(scores, numbers):
    avg = defaultdict(dict)
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
    # all ids of all posts in subreddit
    post_ids = forest[sub].keys()

    # initiate the depth and width dictionaries
    depth = dict.fromkeys(post_ids, 0)
    width = dict.fromkeys(post_ids, 1)

    # for each post, compute the depth and widtyh of its tree
    for post in post_ids:
        widths = defaultdict(dict)
        # compute the depth of the post tree and all its different widths
        depth[post], widths = Depth(forest[sub][post], 0, widths)

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
    nodes = defaultdict(dict)

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
psts = allPosts(True, True, True, 'atheism')  # modify this later
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
    replies = repliesBetweenUsers(sub)
    #print(replies)

    # in degree
    in_degree = in_out_Degree(sub, replies, True)
    #print(in_degree)

    # out degree
    out_degree = in_out_Degree(sub, replies, False)
    #print(out_degree)

    # total scores
    n_posts, n_comments, t_score_posts, t_score_comments = totalScore(sub)
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
    depths, widths = treeDepthWidth(sub)
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