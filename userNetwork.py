from keyFeatures import Tree, Node
import keyFeatures as kf
import matplotlib.pyplot as plt
import seaborn as sns

# Visualise UN
import networkx as nx
from pyvis.network import Network as PyvisNetwork

# Create new directories
import os

# Post or comment in tree
class Comment:
    # Class to represent comments. Difference with kf.Node is the parent property
    def __init__(self, data, auth, score, controversial, parent, depth=-1):
        self.id = data
        self.auth = auth
        self.score = score
        self.controversial = controversial
        self.depth = depth
        self.next = []
        self.parent = parent

    def __repr__(self):
        if self.parent == 0:
            return (self.id + " by " + self.auth + " with no parent" + " score: " + str(self.score))
        else:
            return (self.id + " by " + self.auth + " with parent " + self.parent.id + " score: " + str(self.score))

# Data structures for UN that includes directed weighted edges
class User:
    def __init__(self, userID):
        self.id = userID
        self.outArcs = {}
        self.postScore = 0
        self.commentScore = 0

    def __repr__(self):
        return ("User " + self.id + " with a post score of " + str(self.postScore) + " and a comment score of " + str(self.commentScore) )

    def addScores(self, postScore = 0, commentScore = 0):
        """Increases post and comment score"""
        self.postScore += int(postScore)
        self.commentScore += int(commentScore)

    def existsArc(self, userID: str) -> bool:
        """Checks if the arc self.id -> userID already exists"""
        try:
            if self.outArcs[userID]:
                return True
        except:
            return False
        
    def addArcs(self, userID: str, weights: list):
        """Creates a weighted edge from self.user to userID"""
        self.outArcs[userID] = weights
    
    def addArcWeights(self, userID: str, weights: list):
        """Updates the weights of the edge self.user -> userID."""
        if self.existsArc(userID):
            oldWeights = self.outArcs[userID]
            newWeights = [i + j for i,j in zip(oldWeights, weights)]
            self.outArcs[userID] = newWeights
        else:
            self.addArcs(userID, weights)
        
# Currently not used, but can hold all Users in the UN for later export
class Network:
    def __init__(self, users: list):
        self.users = users

def nodeToComment(node: Node, parent):
    """Returns the node in the Comment datastructure"""
    comment = Comment(node.id, node.auth, node.score, node.controversial, parent, node.depth)
    comment.next = node.next
    return comment


def getComments(rootComment: Comment):
    """Returns a list with the Comment structures that originate from the PCN tree, starting from a rootComment."""

    comments = [rootComment]

    children = rootComment.next
        
    for child in children:
        childComment = nodeToComment(child, rootComment)
        comments += getComments(childComment)
                
    return comments

def createDirectory(path: str):
    """Check existence for path and creates it if necessary."""
    existsPath = os.path.exists(path)

    if not existsPath:
        # Create a new directory because it does not exist 
        os.makedirs(path)

# Import the Forest
forest = kf.forestImportTrain()

# Subreddit to compute the statistics for. Could later be turned into a loop over forest.keys()
subreddit = 'liberal'

# Dictionary of posts
postDict = forest[subreddit]

comments = []
users = dict() 

# Update all user properties and create a users dictionary, with userID as key and a User object as value
for postID in postDict.keys():
    rootNode = postDict[postID]
    # Extract Comment datastructures originating from rootNode (such)
    rootComment = nodeToComment(rootNode, 0)
    newComments = getComments(rootComment)
    comments += newComments

    for comment in newComments:
        
        try:
            # Check if it is contained in the dict and create it otherwise
            if users[comment.auth]:
                user = users[comment.auth]
        except Exception as e:
            user = User(comment.auth)
            users[comment.auth] = user


        # Check if comment is a post
        if comment.parent == 0:
            # Update scores and weights for a root node
            user.addScores(postScore = comment.score)
            for child in comment.next:
                addReplies = 0
                addSandwich = 0
                addPost = 1
                user.addArcWeights(child.auth, [addReplies, addSandwich, addPost])

        
        else:
            # Comment is a reply
            user.addScores(commentScore = comment.score)
            addReplies = 1
            # Check for sandwhiches 
            addSandwich = 0
            for child in comment.next:
                
                # Check if the user is sandwiched by another user
                if comment.parent.auth == child.auth:
                    addSandwich += 1    
            addPost = 0
            user.addArcWeights(comment.parent.auth, [addReplies, addSandwich, addPost])

# Extract all user IDs
userID = list(users.keys())

# Store the three weights per arc
weight1List = []
weight2List = []
weight3List = []

# Store the scores per user
postScoreList = []
commentScoreList = []
totalScoreList = []

for user in users.values():
    postScoreList.append(user.postScore)
    commentScoreList.append(user.commentScore)
    totalScoreList.append(user.postScore + user.commentScore)
    for arc in user.outArcs.values():
        weight1, weight2, weight3 =  arc
        weight1List.append(weight1)
        weight2List.append(weight2)
        weight3List.append(weight3)



# Create subplots for visualisations.
figWeights, axsWeights = plt.subplots(ncols=3, nrows=2, figsize=(20,9))
figScores, axsScores = plt.subplots(ncols=3, nrows=2, figsize=(20,9))

# Create (cummulative) histograms for several key values

def getBins(list: list, minVal: int=1):
    """Returns the bins for sns plots"""
    nbins = 75
    if max(list) - minVal < nbins:
        return [0.5 + i for i in range(minVal-1,max(list)+1)]
    else:
        delta = (max(list) - minVal)//nbins
        return [minVal + i*delta for i in range(nbins)]

# Weight plots
sns.histplot(data=list(filter(lambda x: x >=1, weight1List)),  bins = getBins(weight1List), ax=axsWeights[0][0])
axsWeights[0][0].set_title("Number of replies")

sns.histplot(data=list(filter(lambda x: x >=1, weight2List)), bins = getBins(weight2List),ax=axsWeights[0][1])
axsWeights[0][1].set_title("Number of sandwiches")

sns.histplot(data=list(filter(lambda x: x >=1, weight3List)), bins = getBins(weight3List),ax=axsWeights[0][2])
axsWeights[0][2].set_title("Number of post influences")

# Tail distribution
filterWeight1 = 5
sns.histplot(data=list(filter(lambda x: x >=filterWeight1, weight1List)),  bins = getBins(weight1List, filterWeight1), ax=axsWeights[1][0])
axsWeights[1][0].set_title(f"Number of replies >= {filterWeight1}")

filterWeight2 = 5
sns.histplot(data=list(filter(lambda x: x >=filterWeight2, weight2List)), bins = getBins(weight2List, filterWeight2),ax=axsWeights[1][1])
axsWeights[1][1].set_title(f"Number of sandwiches >= {filterWeight2}")

filterWeight3 = 5
sns.histplot(data=list(filter(lambda x: x >=filterWeight3, weight3List)), bins = getBins(weight3List, filterWeight3),ax=axsWeights[1][2])
axsWeights[1][2].set_title(f"Number of post influences >= {filterWeight3}")

# Score plots
sns.histplot(data=list(filter(lambda x: x >=1, postScoreList)), bins = getBins(postScoreList),ax=axsScores[0][0])
axsScores[0][0].set_title("Post scores")

sns.histplot(data=list(filter(lambda x: x >=1, commentScoreList)), bins = getBins(commentScoreList),ax=axsScores[0][1])
axsScores[0][1].set_title("Comment scores")

sns.histplot(data=list(filter(lambda x: x >=1, totalScoreList)), bins = getBins(totalScoreList),ax=axsScores[0][2])
axsScores[0][2].set_title("Total scores")

# Tail distribution
filterPostScore = 500
sns.histplot(data=list(filter(lambda x: x >=filterPostScore, postScoreList)), bins = getBins(postScoreList, filterPostScore),ax=axsScores[1][0])
axsScores[1][0].set_title(f"Post scores >= {filterPostScore}")

filterCommentScore = 500
sns.histplot(data=list(filter(lambda x: x >=filterCommentScore, commentScoreList)), bins = getBins(commentScoreList, filterCommentScore),ax=axsScores[1][1])
axsScores[1][1].set_title(f"Comment scores >= {filterCommentScore}")

filterTotalScore = 500
sns.histplot(data=list(filter(lambda x: x >=filterTotalScore, totalScoreList)), bins = getBins(totalScoreList, filterTotalScore),ax=axsScores[1][2])
axsScores[1][2].set_title(f"Total scores >= {filterTotalScore}")

# Path to store the visualisations
path = f"Figures/{subreddit}/"

# Create directories if necessary
createDirectory(path)

# Save figures
figWeights.savefig(path + f'weightPlots.png', bbox_inches="tight")
figScores.savefig(path + f'scorePlots.png', bbox_inches="tight")

# Visualize the UN

# Filter the users that are displayed in the UN
def filterUsers(user: User) -> bool:
    """Determines whether user will be shown in the network"""
    # postThreshold = 500
    # commentThreshold = 500
    # return user.postScore > postThreshold or user.commentScore > commentThreshold
    totalScore = 250
    return user.postScore + user.commentScore > totalScore

# Filter the edges that are displayed
def filterEdges(user1: User, user2ID: str) -> bool:
    """Determines whether the edge from user1 to user2 will be shown"""
    replyThreshold = 2
    replyWeight = user1.outArcs[user2ID][0]
    return replyWeight >= replyThreshold

# Create a Graph object
user_graph = nx.Graph()

# Add all users
for userID in users.keys():
    if filterUsers(users[userID]):
        user_graph.add_node(userID)

# Add all (unweighted) edges 
for user in users.values():
    for userOutID in user.outArcs.keys():
        if filterUsers(user) and filterUsers(users[userOutID]) and filterEdges(user, userOutID):
            user_graph.add_edge(user.id, userOutID)

# Create PyvisNetwork object
user_network = PyvisNetwork(height="90%", width="100%", bgcolor="white", font_color="black", \
             notebook=False, heading=f"User Network of subreddit {subreddit}")

# Import the Graph object into the Network
user_network.from_nx(user_graph)

# Show the network
user_network.barnes_hut(gravity=-80000, central_gravity=1.5, spring_length=250, spring_strength=0.0001, damping=0.09, overlap=0)

# Save the network
user_network.save_graph(path + f"UN_{subreddit}.html")

# user_network.show_buttons(filter_=['physics'])
# user_network.show(path + f"UN_{subreddit}.html")

