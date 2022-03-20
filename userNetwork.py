from keyFeatures import Tree, Node
import keyFeatures as kf
import matplotlib.pyplot as plt
import seaborn as sns

# Visualise UN
import networkx as nx
from pyvis.network import Network as PyvisNetwork

# Post or comment in tree
class Comment:
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

# Data structures for UN
class User:
    def __init__(self, userID):
        self.id = userID
        self.outArcs = {}
        self.postScore = 0
        self.commentScore = 0

    def __repr__(self):
        return ("User " + self.id + " with a post score of " + str(self.postScore) + " and a comment score of " + str(self.commentScore) )

    def addScores(self, postScore = 0, commentScore = 0):
        self.postScore += int(postScore)
        self.commentScore += int(commentScore)

    def existsArc(self, userID: str) -> bool:
        try:
            if self.outArcs[userID]:
                return True
        except:
            return False
        
    def addArcs(self, userID: str, weights: list):
        self.outArcs[userID] = weights
    
    def addArcWeights(self, userID: str, weights: list):
        if self.existsArc(userID):
            oldWeights = self.outArcs[userID]
            newWeights = [i + j for i,j in zip(oldWeights, weights)]
            self.outArcs[userID] = newWeights
        else:
            self.addArcs(userID, weights)
        

class Network:
    def __init__(self, users: list):
        self.users = users

def getComments(node: Node):
    rootComment = Comment(node.id, node.auth, node.score, node.controversial, 0, node.depth)
    rootComment.next = node.next
    comments = [rootComment]
    children = node.next

    childComments = []
    
        
    for child in children:
        childComment = Comment(child.id, child.auth, child.score, child.controversial, rootComment, child.depth)
        childComment.next = child.next
        comments.append(childComment)
        for comment in getComments(child)[1]:
            childComments.append(comment)
                
    return (comments + childComments, childComments)

forest = kf.forestImportTrain()

subreddit = 'lockdownskepticism'

postDict = forest[subreddit]

comments = []
users = dict() 

for postID in postDict.keys():
    rootNode = postDict[postID]
    newComments = getComments(rootNode)[0]
    comments += newComments

    for comment in newComments:
        
        try:
            # Check if it is contained in the dict
            if users[comment.auth]:
                user = users[comment.auth]
        except Exception as e:
            user = User(comment.auth)
            users[comment.auth] = user


        # Check if comment is a post
        if comment.parent == 0:
            # print(comment.next)
            user.addScores(postScore = comment.score)
            for child in comment.next:
                addReplies = 0
                addSandwich = 0
                addPost = 1
                user.addArcWeights(child.auth, [addReplies, addSandwich, addPost])

        # Comment is a reply
        else:
            user.addScores(commentScore = comment.score)
            addReplies = 1
            # Check for sandwhich 
            addSandwich = 0
            for child in comment.next:
                
                # Check if the user is sandwiched by another user
                if comment.parent.auth == child.auth:
                    addSandwich += 1    
            addPost = 0
            user.addArcWeights(comment.parent.auth, [addReplies, addSandwich, addPost])

        # Check if comment is post
        if comment.parent == 0:
            user.addScores(postScore = comment.score, commentScore = 0)
        else:
            user.addScores(postScore = 0, commentScore = comment.score)

# print(users.values())

userID = list(users.keys())

weight1List = []
weight2List = []
weight3List = []

postScoreList = []
commentScoreList = []

for user in users.values():
    postScoreList.append(user.postScore)
    commentScoreList.append(user.commentScore)
    # print(user.outArcs.values())
    for arc in user.outArcs.values():
        # print(arc[1])
        weight1, weight2, weight3 =  arc
        weight1List.append(weight1)
        weight2List.append(weight2)
        weight3List.append(weight3)

print(max(weight1List))
fig, axs = plt.subplots(ncols=3, nrows=2, figsize=(16,9))


sns.histplot(data=list(filter(lambda x: x >0, weight1List)),  bins = [0.5 + i for i in range(max(weight1List)+1)], ax=axs[0][0])
axs[0][0].set_title("Number of replies")

sns.histplot(data=list(filter(lambda x: x >0, weight2List)), bins = [0.5 + i for i in range(max(weight2List)+1)],ax=axs[0][1])
axs[0][1].set_title("Number of sandwiches")

sns.histplot(data=list(filter(lambda x: x >0, weight3List)), bins = [0.5 + i for i in range(max(weight3List)+1)],ax=axs[0][2])
axs[0][2].set_title("Number of post influences")

sns.histplot(data=list(filter(lambda x: x >0, postScoreList)), cumulative=True,ax=axs[1][0])
axs[1][0].set_title("Post scores")

sns.histplot(data=list(filter(lambda x: x >0, commentScoreList)), cumulative=True,ax=axs[1][1])
axs[1][1].set_title("Comment scores")
# plt.show()

# Visualize UN

def filterUsers(user: User) -> bool:
    """Determines whether user will be shown in the network"""
    postThreshold = 750
    commentThreshold = 750
    return user.postScore > postThreshold or user.commentScore > commentThreshold

def filterEdges(user1: User, user2ID: str) -> bool:
    """Determines whether the edge from user1 to user2 will be shown"""
    replyThreshold = 3
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
             notebook=False, heading="User Network")

# Import the Graph object into the Network
user_network.from_nx(user_graph)

# Show the network
user_network.barnes_hut(gravity=-80000, central_gravity=1.5, spring_length=250, spring_strength=0.0001, damping=0.09, overlap=0)
# user_network.show_buttons(filter_=['physics'])
user_network.show("UN.html")

