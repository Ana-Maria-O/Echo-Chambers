from keyFeatures import Tree, Node
import keyFeatures as kf
forest = kf.forestImportTrain()

lds = forest['lockdownskepticism']
tree = lds['rto3gr']
print(tree.next)
#users = kf.allUsers(['lockdownskepticism'])

def getComments(node: Node):

    comments = [node]
    children = node.next
        
    for child in children:
        for comment in getComments(child):
            comments.append(comment)
                
    return comments
            

comments=[]
for postID in lds.keys():
    comments += getComments(lds[postID])
    
users = set(comment.auth for comment in comments)

class User:
    def __init__(self, userID):
        self.id = userID
        self.outArcs = {}
        self.postScore = 0
        self.commentScore = 0
        
    def addArcs(self, user, weights: list):
        self.outArcs[user.id] = weights

class Network:
    def __init__(self, users)




