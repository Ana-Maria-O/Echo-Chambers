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
    def __init__(self, data, auth, score, controversial, depth=-1):
        self.id = data
        self.auth = auth
        self.score = score
        self.controversial = controversial
        self.depth = depth
        self.next = []

    def __repr__(self):
        return (self.id + " by " + self.user + " score: " + self.score)

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
            controversial = place.controversial.item()
            r_node = Node(reply, auth, score, controversial)
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
        forestDict[sub] = dict.fromkeys(psts['id'].tolist(), None)

        for post in forestDict[sub].keys():
            place = psts.loc[psts['id'] == post]

            if post in posts[sub]['controversial']['id'].tolist():
                controversial = 1
            else:
                controversial = 0

            forestDict[sub][post] = Tree(Node(post, place.author.item(), place.score.item(), controversial))
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
    node.depth = depth

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
    # dictionary holding the indegrees/outdegrees of users
    deg = dict.fromkeys(users, 0)

    for user1 in replies.keys():
        for user2 in replies[user1]:
            if ind:
                deg[user2] += replies[user1][user2]
            else:
                deg[user1] += replies[user1][user2]

    return deg

# returns the modified ct_scores and cn_posts dictionaries as specified in the 
# description for totalScore()
def addCommentScores(ct_scores, cn_posts, node):
    if len(node.next) > 0:
        for comment in node.next:
            ct_scores[comment.auth] += comment.score
            cn_posts[comment.auth] += 1

            ct_scores, cn_posts = addCommentScores(ct_scores, cn_posts, comment)
    
    return ct_scores, cn_posts

# returns a dictionary of all users in a subreddit and their total score in that subreddit and a dictionary
# which keeps track of how many posts and comments each user has made
# takes as input a string which is the name of the subreddit
# returns a dictionary t_scores such that t_scores[user] is the total score of user in the subreddit and a dictionary
# n_posts where n_posts[user] is the total number of posts and comments that user has made
def totalScore(sub):
    # dictionary with all users' post scores
    pt_scores = dict.fromkeys(users, 0)

    # dictionary with all users' comment scores
    ct_scores = dict.fromkeys(users, 0)

    # dictionary with number of all users' posts
    pn_posts = dict.fromkeys(users, 0)

    # dictionary with number of all users' comments
    cn_posts = dict.fromkeys(users, 0)

    post_ids = psts['id']
    # gather all posts scores
    for post in post_ids:
        node = forest[sub][post]
        pt_scores[node.auth] += node.score
        pn_posts[node.auth] += 1

        ct_scores, cn_posts = addCommentScores(ct_scores, cn_posts, node)

    return pn_posts, cn_posts, pt_scores, ct_scores

# returns a dictionary of all users in a subset of users and their average score for the subreddits taken into account
# takes as input a dictionary of all users and their scores and a dictionary of all users and the number of comments and posts they made
# returns dicitonary avg such that avg[user] is the average score of that user
def averageScore(p_scores, c_scores, p_number, c_number):
    p_avg = defaultdict(dict)
    c_avg = defaultdict(dict)

    for user in users:
        if p_number[user] == 0:
            p_avg[user] = None
        else:
            p_avg[user] = p_scores[user] / p_number[user]

        if c_number[user] == 0:
            c_avg[user] = None
        else:
            c_avg[user] = c_scores[user] / c_number[user]
        
    return p_avg, c_avg

def addControversial(c_con, node):
    if len(node.next) > 0:
        for reply in node.next:
            c_con[node.auth] += node.controversial

            c_con = addControversial(c_con, reply)
    
    return c_con

# returns a dictionary of all users in a subreddit and their controversiality
# takes as input a string which is the name of the subreddit
# returns a dictionary con such that con[user] is the controversilaity score of that user
def controversiality(sub):
    # dictionaries of controversiality
    p_con = dict.fromkeys(users, 0)
    c_con = dict.fromkeys(users, 0)

    for post in forest[sub]:
        p_con[forest[sub][post].auth] += forest[sub][post].controversial

        c_con = addControversial(c_con, forest[sub][post])

    return p_con, c_con

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
def ratioPostComment(n_posts, n_comments, sub):
    #initialize pcRatio
    pcRatio = defaultdict(dict)

    for user in users:
        if n_comments[user] == 0:
            pcRatio[user] = 1
        else:
            pcRatio[user] = n_posts[user] / n_comments[user]

    return pcRatio

def addNodes(nodes_between, last_nodes, node, post):
    if node.auth in last_nodes:
        prev = last_nodes[node.auth]
        if post not in nodes_between[node.auth]:
            nodes_between[node.auth][post] = []

        nodes_between[node.auth][post].append(node.depth - last_nodes[node.auth] - 1)
    else:
        prev = -1
    
    last_nodes[node.auth] = node.depth

    for reply in node.next:
        nodes_between = addNodes(nodes_between, last_nodes, reply, post)

    if prev == -1:
        last_nodes.pop(node.auth)
    else:
        last_nodes[node.auth] = prev

    return nodes_between

# returns a dictionary with every active user on a subreddit, the posts they made/commented on and a list of
# how many nodes there are on a thread between their replies
# takes as input a string which is the name of the subreddit
# returns a dictionary nodes such that nodes[user][post] is a list of the different amount of nodes
# in a thread between user's replies on post
def nodesBetweenReplies(sub):
    nodes_between = defaultdict(dict)

    for post in psts['id']:
        last_nodes = {}
        nodes_between[forest[sub][post].auth][post] = []
        nodes_between = addNodes(nodes_between, last_nodes, forest[sub][post], post)

    return nodes_between

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
users = allUsers(True, True, True, 'atheism')  # modify this later

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

    print("Total scores started............")
    # total scores
    n_posts, n_comments, t_score_posts, t_score_comments = totalScore(sub)
    print("Total scores done!")
    #print(t_score)
    #print(n_comments)

    print("Average scores started............")
    # average score
    a_score_posts, a_score_comments = averageScore(t_score_posts, t_score_comments, n_posts, n_comments)
    print("Average scores done!")
    #print(a_score)

    print("Controversiality started............")
    # controversiality
    p_con, c_con = controversiality(sub)
    print("Controversiality done!")
    #print(p_con)

    #sorted list of subreddits active on

    # distribution of subreddits active on

    # most used words

    # tree depth & width
    depths, widths = treeDepthWidth(sub)
    #print(depths)
    #print(widths)

    print("Post/comment ratio started............")
    # post/comment ratio
    p_c_ratio = ratioPostComment(n_posts, n_comments, sub)
    print("Post/comment ratio done!")
    #print(p_c_ratio)

    # number of levels in post trees between users' replies
    nodes = nodesBetweenReplies(sub)
    #print(nodes)

# average score of posts/comments per subreddit

# distribution of posts/comments per subreddit

# most active users per subreddi

if __name__ == "__main__":
    main()