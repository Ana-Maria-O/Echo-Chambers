import networkx as nx
import pickle
from keyfeatures_2_riccardo import Tree, Node, getTime
from userNetworkFunction import Comment, User, Network, createDirectory
import matplotlib.pyplot as plt
import seaborn as sns
from pyvis.network import Network as PyvisNetwork
# from pydot import graphiz
# from networkx.drawing.nx_pydot import graphviz_layout

saveFolder = "Forests/PushShift/"

sub = "enoughtrumpspam"
treeFile = saveFolder + "/forest_for_testing_dataset.pickle"

with open(treeFile, 'rb') as f:
    forest = pickle.load(f)


print(list(forest.keys()))


tree = forest[sub]
posts = list(tree.keys())


# treeRoot = tree[posts[0]]

### Visualize the UN

# Create a Graph object
nrOfTrees = 10

def addChildren(T, node, addNode = True):
    if addNode:
        T.add_node(node.auth)

    if len(node.next) == 0:
        return T

    for child in node.next:
        T.add_node(child.auth)
        T.add_edge(node.auth, child.auth)
        addChildren(T, child, False)

    return T

# First nrOfTrees
for treeIndex in range(nrOfTrees):
    
    treeRoot = tree[posts[treeIndex]]

    temp = addChildren(nx.DiGraph(), treeRoot)
    
    # Create PyvisNetwork object
    pyvis_Tree = PyvisNetwork(height="90%", width="100%", bgcolor="white", font_color="black", \
                notebook=False, heading=f"User Network of subreddit {sub}")

    # Import the Graph object into the Network
    pyvis_Tree.from_nx(temp)

    # Show the network
    # user_network.barnes_hut(gravity=-80000, central_gravity=1.5, spring_length=250, spring_strength=0.0001, damping=0.09, overlap=0)

    createDirectory(saveFolder + sub + "/")

    # Save the network
    pyvis_Tree.save_graph(saveFolder + sub + "/" + f"PCN_{treeIndex}.html")

    # Additional options for visualisation
    pyvis_Tree.show_buttons(filter_=['physics'])


# Plot tree with largest first response
maxSize = 0
maxIndex = -1
for i in range(len(posts)):
    post = posts[i]
    root = tree[post]
    if len(root.next) > maxSize:
        maxSize = len(root.next)
        maxIndex = i

print("Found Max")

treeRoot = tree[posts[maxIndex]]

temp = addChildren(nx.DiGraph(), treeRoot)

# Create PyvisNetwork object
pyvis_Tree = PyvisNetwork(height="90%", width="100%", bgcolor="white", font_color="black", \
            notebook=False, heading=f"PCN of subreddit r/{sub}")

# Import the Graph object into the Network
pyvis_Tree.from_nx(temp)

# Show the network
pyvis_Tree.barnes_hut(gravity=-80000, central_gravity=1.5, spring_length=250, spring_strength=0.0001, damping=0.09, overlap=0)

createDirectory(saveFolder + sub + "/")

# Save the network
pyvis_Tree.save_graph(saveFolder + sub + "/Largest_First_Response_" + f"PCN_{treeIndex}.html")

# Additional options for visualisation
# pyvis_Tree.show_buttons(filter_=['physics'])