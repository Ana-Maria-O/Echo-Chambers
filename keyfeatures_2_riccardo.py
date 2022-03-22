#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from collections import defaultdict
import pandas as pd
import pickle

time = ''
posts = {}
psts = {}
comments = {}
users = []
forest = {}

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

# returns a dictionary of dataframes with all the posts from the mentioned subreddits
def allPosts(subs):
    all_posts = {}

    for sub in subs:
        # choose which subreddit to aggregate posts from
        psts = posts[sub]
        all_posts[sub] = pd.DataFrame()

        # gather all posts from sub
        all_posts[sub] = pd.concat([all_posts[sub], psts['hot']])

        all_posts[sub] = pd.concat([all_posts[sub], psts['new']])

        all_posts[sub] = pd.concat([all_posts[sub], psts['controversial']])

        # get rid of duplicate entries
        all_posts[sub] = all_posts[sub].drop_duplicates(subset='id', keep='last')

    return all_posts

# add all comments from a post to its tree
def addCommentsToTree(node, comms, sub, root=True):
    replies = []

    # gather all the replies to the current node
    if root:
        replies = comms.loc[comms['reply to comment'].isnull()]
    else:
        replies = comms.loc[comms['reply to comment'] == node.id]

    # if the node has replies
    if replies.shape[0] > 0:
        # get all the ids of the replies
        replies_id = replies['id'].tolist()

        # for each reply, add it and the thread it spawns to the tree
        for reply in replies_id:
            # find the row in comms corresponding to the reply
            place = comms.loc[comms['id'] == reply]

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

        forestDict[sub] = dict.fromkeys(psts[sub]['id'].tolist(), None)

        # make a tree for each post in the subreddit
        for post in forestDict[sub].keys():
            # get the row from psts corresponding to the post
            place = psts[sub].loc[psts[sub]['id'] == post]

            # extract the controversial score of the post
            if post in posts[sub]['controversial']['id'].tolist():
                controversial = 1
            else:
                controversial = 0

            # create the tree corresponding to the post and its comments
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
def importPosts(kind):
    # replace this with the path for your own files
    path = 'C://Users//20190819//Reddit Data//Posts//'

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

    # for each subreddit, add all of its posts' dataframes to the dictionary
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
    # replace this with the path for your own files
    path = 'C://Users//20190819//Reddit Data//Comments//'

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

    # for each subreddit, add its comments dataframe to the dictionary
    for sub in commentDF.keys():
            path2 = path + sub + '.csv'
            commentDF[sub] = pd.read_csv(path2)
            commentDF[sub] = commentDF[sub].drop_duplicates(subset='id', keep='last')

    return commentDF

# returns a list of all users in a comment and a post dictionaries
# takes as input a post dictionary of dataframes and a comment dictionary of dataframes
# returns a list of all users in those dictionaries
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
        users[sub].extend(cmments['reply to user'].unique().tolist())

        # for each section of posts: hot, new, controversial get all authors of posts in this section
        users[sub].extend(psts[sub]['author'].unique().tolist())

        # remove duplicate entries 
        uset = set(users[sub])
        users[sub] = list(uset)


    return users

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

# returns a dictionary with the number of replies from each user to every other user on each subreddit at a certain timeslice
# takes as input a string which is the name of the subreddit
# returns a dictionary replies which has usernames as keys. Each key is associated with a different dictionary which also has usernames as keys
# replies[sub][user1][user2] represents the number of replies by user1 to user2 on posts from subreddit sub
def repliesBetweenUsers(subs):
    replies = {}

    # for each subreddit
    for sub in subs:
        # get the trees corresponding to every post in the current subreddit
        subF = forest[sub]
        replies[sub] = defaultdict(dict) 

        # for each post in the subreddit add its replies to the dictionary
        for post in subF.keys():
            replies[sub] = addReplies(replies[sub], subF[post])

    return replies
                
# returns a dictionary of all users and their in-degree or their out-degree
# takes as input a string which is the name of the subreddit, the dictionary replies of number of replies and a boolean ind such that
# ind == true => returns in-degree dictionary, else returns out-degree dictionary
# returns a dictionary deg such that deg[sub][user] is the value of user's in-degree/out-degree in subreddit sub
def in_out_Degree(subs, replies, ind):
    # dictionary holding the indegrees/outdegrees of users
    deg = {}

    for sub in subs:
        deg[sub] = dict.fromkeys(users[sub], 0)

        for user1 in replies[sub].keys():
            for user2 in replies[sub][user1]:
                if ind:
                 deg[sub][user2] += replies[sub][user1][user2]
                else:
                    deg[sub][user1] += replies[sub][user1][user2]

    return deg

# returns the modified ct_scores and cn_posts dictionaries as specified in the 
# description for totalScore()
def addCommentScores(ct_scores, cn_posts, node):
    # if the current node has replies
    if len(node.next) > 0:

        # for each reply to the current node, update the comment score and comment count of the reply's author
        for comment in node.next:
            ct_scores[comment.auth] += comment.score
            cn_posts[comment.auth] += 1

            # update the comment scores and the comment counts of the authors who wrote the comments in the rest of the current comment thread
            ct_scores, cn_posts = addCommentScores(ct_scores, cn_posts, comment)
    
    return ct_scores, cn_posts

# returns a dictionary of all users in a subreddit, their total post and comment score in that subreddit and a dictionary
# which keeps track of how many posts and comments each user has made
# takes as input a string which is the name of the subreddit
# returns dictionaries pt_scores, ct_scores, pn_posts and cn_posts such that 
# pt_scores[sub][user] is the total score of user's posts in the subreddit sub,
# ct_scores[sub][user] is the total score of user's comments in the subreddit sub,
# pn_posts[sub][user] is the total number of posts that user has made in subreddit sub and
# cn_posts[sub][user] is the total number of comments that user has made in subreddit sub
def totalScore(subs):
    pt_scores = {}
    ct_scores = {}
    pn_posts = {}
    cn_posts = {}

    for sub in subs:
        # dictionary with all users' post scores
        pt_scores[sub] = dict.fromkeys(users[sub], 0)

        # dictionary with all users' comment scores
        ct_scores[sub] = dict.fromkeys(users[sub], 0)

        # dictionary with number of all users' posts
        pn_posts[sub] = dict.fromkeys(users[sub], 0)

        # dictionary with number of all users' comments
        cn_posts[sub] = dict.fromkeys(users[sub], 0)

        # get the ids of all the posts in the subreddit
        post_ids = psts[sub]['id']

        # gather all post scores and update all post counts
        for post in post_ids:
            node = forest[sub][post]
            pt_scores[sub][node.auth] += node.score
            pn_posts[sub][node.auth] += 1

            ct_scores[sub], cn_posts[sub] = addCommentScores(ct_scores[sub], cn_posts[sub], node)

    return pn_posts, cn_posts, pt_scores, ct_scores

# returns a dictionary of all users in a subset of users and their average score for the subreddits taken into account
# takes as input a dictionary of all users and their scores and a dictionary of all users and the number of comments and posts they made
# returns dicitonary avg such that avg[sub][user] is the average score of that user
def averageScore(p_scores, c_scores, p_number, c_number, subs):
    p_avg = defaultdict(dict)
    c_avg = defaultdict(dict)

    for sub in subs:
        for user in users[sub]:
            if p_number[sub][user] == 0:
                p_avg[sub][user] = None
            else:
                p_avg[sub][user] = p_scores[sub][user] / p_number[sub][user]

            if c_number[sub][user] == 0:
                c_avg[sub][user] = None
            else:
                c_avg[sub][user] = c_scores[sub][user] / c_number[sub][user]
        
    return p_avg, c_avg

# return the modified dictionary c_con such that the controversial scores of the comments in the thread starting 
# with node are taken into account
def addControversial(c_con, node):
    # if the current node has any replies
    if len(node.next) > 0:
        for reply in node.next:
            # update the controversial score of the reply's author
            c_con[node.auth] += node.controversial

            # update the controversial scores of the authors of all comments following node in the comment thread
            c_con = addControversial(c_con, reply)
    
    return c_con

# returns a dictionary of all users in a subreddit and their controversiality
# takes as input a string which is the name of the subreddit
# returns a dictionary con such that con[sub][user] is the controversilaity score of that user in subreddit sub
def controversiality(subs):
    p_con = {}
    c_con = {}

    for sub in subs:
        # dictionaries of controversiality
        p_con[sub] = dict.fromkeys(users[sub], 0)
        c_con[sub] = dict.fromkeys(users[sub], 0)

        for post in forest[sub]:
            p_con[sub][forest[sub][post].auth] += forest[sub][post].controversial

            c_con[sub] = addControversial(c_con[sub], forest[sub][post])

    return p_con, c_con

# computes the depth of a post tree and the number of nodes at each depth, where the depth of the root is given
# and the widths of the tree at each level of depth
# takes as input a string id representing the id of the root post, 
# comms the comment dataframe from which to extract the replies to the post,
# depth which is the depth of the root and widths which is a dictionary of all the widths of the tree
# returns the depth of the subtree with id as its root and the dictionary witdths such that such that
# widths[index] is the number of nodes of depth index
def Depth(node, depth, widths):
    # extract all direct replies to the current node
    replies = node.next

    # update the node's depth
    node.depth = depth

    # update the witdh of the current depth level
    if depth in widths:
        widths[depth] += len(replies)
    else:
        widths[depth] = len(replies)

    # if the current node has replies compute depth of its deepest subtree
    if len(replies) > 0:
        sub_depth = depth

        # compute depth of each subtree
        for nextNode in replies:
            tree_depth, widths = Depth(nextNode, depth + 1, widths)

            # update the largest depth
            if tree_depth > sub_depth:
                sub_depth = tree_depth

        return sub_depth, widths
    else:
        return depth, widths

# returns a dictionary with the depths and a dictionary with the heights of all trees corresponding to posts on a subreddit
# takes as input a string which is the name of the subreddit
# returns dictionaries depth and width such that depth[sub][post] is the depth of the tree rooted at post in subreddit sub
#  and width[sub][post] is the width of the tree rooted at post in subreddit sub
def treeDepthWidth(subs):
    # initiate the depth and width dictionaries
    depth = {}
    width = {}

    for sub in subs:
        # all ids of all posts in subreddit
        post_ids = forest[sub].keys()

        depth[sub] = dict.fromkeys(post_ids, 0)
        width[sub] = dict.fromkeys(post_ids, 1)

        # for each post, compute the depth and widtyh of its tree
        for post in post_ids:
            widths = defaultdict(dict)

            # compute the depth of the post tree and all its different widths
            depth[sub][post], widths = Depth(forest[sub][post], 0, widths)

            # find the maximum width of the post tree
            width[sub][post] = max(widths.values())

    return depth, width

# returns a dictionary with every active user on a subreddit and their post/comment ratio
# takes as input a string sub which is the name of the subreddit
# returns a dictionary pcRatio such that pcRatio[sub][user] is the post/comment ratio of user on the subreddit sub
def ratioPostComment(n_posts, n_comments, subs):
    #initialize pcRatio
    pcRatio = defaultdict(dict)

    for sub in subs:
        for user in users[sub]:
            if n_comments[sub][user] == 0:
                pcRatio[sub][user] = 1
            else:
                pcRatio[sub][user] = n_posts[sub][user] / n_comments[sub][user]

    return pcRatio

# returns the modified dictionary nodes_between such that the numbers of nodes between each user's replies in the thread starting at node
# are talen into account
def addNodes(nodes_between, last_nodes, node, post):
    # if the author of the current node has written another comment earlier in the thread
    if node.auth in last_nodes:
        prev = last_nodes[node.auth]

        # update the number of nodes between the author's comments in this thread
        if post not in nodes_between[node.auth]:
            nodes_between[node.auth][post] = []

        nodes_between[node.auth][post].append(node.depth - last_nodes[node.auth] - 1)
    else:
        prev = -1
    
    # update the depth of the latest occurence of this author commenting in this thread
    last_nodes[node.auth] = node.depth

    # check the rest of the thread and update the dictionary
    for reply in node.next:
        nodes_between = addNodes(nodes_between, last_nodes, reply, post)

    # once this function is exited we're switching to a different thread, so undo the latest occurence of the author
    if prev == -1:
        last_nodes.pop(node.auth)
    else:
        last_nodes[node.auth] = prev

    return nodes_between

# returns a dictionary with every active user on a subreddit, the posts they made/commented on and a list of
# how many nodes there are on a thread between their replies
# takes as input a string which is the name of the subreddit
# returns a dictionary nodes such that nodes[sub][user][post] is a list of the different amount of nodes
# in a thread between user's replies on post in the subreddit sub
def nodesBetweenReplies(subs):
    nodes_between = defaultdict(dict)

    # for each subreddit
    for sub in subs:
        # for each post in the sub, check every thread under the post and update nodes_between
        for post in psts[sub]['id']:
            last_nodes = {}
            nodes_between[sub] = defaultdict(dict)

            nodes_between[sub][forest[sub][post].auth][post] = []
            nodes_between[sub] = addNodes(nodes_between[sub], last_nodes, forest[sub][post], post)

    return nodes_between

def forestExportTrain():
    # create file
    pfile = open('forest_train.p', 'wb')

    # dump forest to file
    pickle.dump(forest, pfile)

    # close file
    pfile.close()

def forestImportTrain():
    # read the file
    pfile = open('forest_train.p', 'rb')

    # unpickle the file
    f = pickle.load(pfile)

    # close the file
    pfile.close()

    return f

#----
def dicttest(df):
        #this is really just the most barebones test
        #i could think of to differentiate between 
        #the posts and comments. 
        #just so I don't write everything twice
        if 'hot' in df.keys():
            return True
        else:
            return False

def active_list(df):
    #returns a list of users in a comment thread
    if not dicttest(df):
        pass
    else:
        df = pd.concat([df[i] for i in df.keys()]).drop_duplicates().reset_index(drop=True)
    auth_unique = list(df.author.unique())
    if '[deleted]' in auth_unique:
        auth_unique.remove('[deleted]')
    active = []
    for i in auth_unique:
        active.append((i, len(df[df['author'] == i])))
    return sorted(active, key = lambda x: x[1], reverse = True)

def score_metrics(df):
    if not dicttest(df):
        pass
    else:
        df = pd.concat([df[i] for i in df.keys()]).drop_duplicates().reset_index(drop=True)
    avg = sum(df['score'])/len(df)
    maxs = sorted(df.score, reverse = True)[0]
    mins = sorted(df.score)[0]
    #print('Average score of subreddit: {}\nMaximum Score: {}\nMinimum Score: {}'.format(avg, maxs, mins))
    return avg, maxs, mins

def activity_distribution(data):
    user_dist = {}
    for reddit in data:
        user_dist[reddit] = {}
        reddict = user_dist[reddit]

        sub = data[reddit]
        if dicttest(sub):
            df = pd.concat(sub[i] for i in sub).drop_duplicates().reset_index(drop=True)
        else:
            df = sub

        for i in df.author.unique():
            if i in reddict.keys():
                pass
            else:
                reddict[i] = 0
        for auth in df.author:
            reddict[auth] += 1

    return user_dist

def setup():
    global time
    global posts
    global psts
    global comments
    global users
    global forest
    # time slice that the program processes
    time = getTime(0)

    if time == 'Invalid':
       raise KeyError('The requested timeslice file does not exist.')

    # import post and comment dataframes
    print("Start setup ........")
    print("Start importing posts ........")

    posts = importPosts(time)
    psts = allPosts(posts.keys())

    print("Posts imported!")
    print("Start importing comments ........")

    comments = importComments(time)
    users = allUsers(posts.keys())

    print("Comments imported!")
    print("Start creating forest ........")

    # forest dictionary
    forest = createForest()

    print("Forest created!")
    print("Setup done!")

def main():

    # setup for the rest of these fucntions to work
    setup()
    forestExportTrain()
    # subreddit
    sub = posts.keys()

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
    a_score_posts, a_score_comments = averageScore(t_score_posts, t_score_comments, n_posts, n_comments, sub)
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
    
    print(posts, type(posts))
    print()
    print(sub, type(sub))
    
# average score of posts/comments per subreddit
    averagescore = [(su, score_metrics(posts[su])[0]) for su in sub]
    print('when the average is scored')

# distribution of posts/comments per subreddit
    averagedist = [activity_distribution(posts[su]) for su in sub]
    print('distributed the posts/comments')
# most active users per subreddit
    aclist = [active_list(posts[df]) for df in posts]
    print('active listed')
    
if __name__ == "__main__":
    main()

