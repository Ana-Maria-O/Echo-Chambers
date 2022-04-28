from keyFeatures import Tree, Node
from keyFeatures import getTime
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
# Create new directories
import os

# Visualise UN
import networkx as nx
#from pyvis.network import Network as PyvisNetwork

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

def forestImportTrain(num):

    path = "Forests/forest_train_" + getTime(num) + ".p"
    # read the file
    pfile = open(path, 'rb')

    # unpickle the file
    f = pickle.load(pfile)

    # close the file
    pfile.close()

    return f



def createUN(subreddit, num):

    forest = forestImportTrain(num)
    
    # Subreddit to compute the statistics for. Could later be turned into a loop over forest.keys()

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

    

    # Path to store the visualisations
    pathNetwork = f"Networks/{getTime(num)}/"

    # Create directories if necessary
    createDirectory(pathNetwork)

    # Create Network object
    network = Network(list(users.values()))

    # Save the network
    with open(pathNetwork + f'{subreddit}.pickle', 'wb') as f:
        pickle.dump(network, f, protocol=pickle.HIGHEST_PROTOCOL)

    return None
    
