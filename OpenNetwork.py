import pickle
from keyfeatures_2_riccardo import Tree, Node, getTime
from userNetworkFunction import Comment, User, Network, createDirectory
from networkx.algorithms import community
import matplotlib.pyplot as plt
import seaborn as sns

# Visualise UN
import networkx as nx
from pyvis.network import Network as PyvisNetwork

# Filter the users that are displayed in the UN
def filterUsers(user: User) -> bool:
    """Determines whether user will be shown in the network"""
    # postThreshold = 500
    # commentThreshold = 500
    # return user.postScore > postThreshold or user.commentScore > commentThreshold
    totalScore = 0
    return user.postScore + user.commentScore > totalScore

# Filter the edges that are displayed
def filterEdges(user1: User, user2ID: str) -> bool:
    """Determines whether the edge from user1 to user2 will be shown"""
    replyThreshold = 1
    replyWeight = user1.outArcs[user2ID][0]
    return replyWeight >= replyThreshold


def computeKeyFeaturesUN(subreddit, num, plots = False):
    # Path to store the visualisations
    pathNetwork = f"Networks/{getTime(num)}/"

    with open(pathNetwork + f'{subreddit}.pickle', 'rb') as f:
        network = pickle.load(f)
    
    users = network.users

    userDict = {user.id : user for user in users}

    # Path to store the visualisations
    path = f"Figures/{getTime(num)}/{subreddit}/"

    createDirectory(path)

    # Save the centrality measures
    centralityDict = {}

    #### Plot Centrality measures

    # Extract all user IDs
    userID = [user.id for user in users]

    # Store the three weights per arc
    weight1List = []
    weight2List = []
    weight3List = []

    # Store the scores per user
    postScoreList = []
    commentScoreList = []
    totalScoreList = []

    for user in users:
        postScoreList.append(user.postScore)
        commentScoreList.append(user.commentScore)
        totalScoreList.append(user.postScore + user.commentScore)
        for arc in user.outArcs.values():
            weight1, weight2, weight3 =  arc
            weight1List.append(weight1)
            weight2List.append(weight2)
            weight3List.append(weight3)

    # Save the weight lists
    centralityDict["ReplyWeights"] = weight1List
    centralityDict["Sandwiches"] = weight2List
    centralityDict["PostWeights"] = weight3List

    # Create a Graph object
    user_graph = nx.DiGraph()

    # Add all users
    for user in users:
        if filterUsers(user):
            user_graph.add_node(user.id)

    # Add all (unweighted) edges 
    for user in users:
        for userOutID in user.outArcs.keys():
            if filterUsers(user) and filterUsers(userDict[userOutID]) and filterEdges(user, userOutID):
                user_graph.add_edge(user.id, userOutID)

    # Compute remaining centrality measures
    inDegreeCentrality = nx.in_degree_centrality(user_graph)
    centralityDict["InDegree"] = inDegreeCentrality

    outDegreeCentrality = nx.out_degree_centrality(user_graph)
    centralityDict["OutDegree"] = outDegreeCentrality

    eigenVectorCentrality = nx.eigenvector_centrality(user_graph)
    centralityDict["EigenVector"] = eigenVectorCentrality

    # try:
    #     katzCentrality = nx.katz_centrality(user_graph)
    #     centralityDict["Katz"] = katzCentrality
    # except:
    #     pass

    harmonicCentrality = nx.harmonic_centrality(user_graph)
    centralityDict["Harmonic"] = harmonicCentrality

    voteRankCentrality = nx.voterank(user_graph)
    centralityDict["VoteRank"] = voteRankCentrality

    communities = community.greedy_modularity_communities(user_graph)
    centralityDict["Communities"] = communities

    resultsPath = f"Results/{getTime(num)}/"
    createDirectory(resultsPath)

    # Save the key features
    with open(resultsPath + f'{subreddit}_key_features.pickle', 'wb') as f:
        pickle.dump(centralityDict, f, protocol=pickle.HIGHEST_PROTOCOL)


def getBins(list: list, minVal: int=1, isInteger = False):
    """Returns the bins for sns plots"""
    nbins = 75
    if max(list) - minVal < nbins and isInteger:
        return [0.5 + i for i in range(minVal-1,int(max(list))+1)]
    else:
        delta = (max(list) - min(list))/nbins
        return [min(list) + i*delta for i in range(nbins)]

def createPlots(subreddit, num, UN = False):

    saveFolder = f"Figures/{getTime(num)}/{subreddit}/"

    createDirectory(saveFolder)

    with open(f'Results/{getTime(num)}/{subreddit}_key_features.pickle', 'rb') as f:
        centralityDict = pickle.load(f)

    weight1List = centralityDict["ReplyWeights"]
    weight2List = centralityDict["Sandwiches"]
    weight3List = centralityDict["PostWeights"] 

    # Create subplots for visualisations of weights and scores
    figWeights, axsWeights = plt.subplots(ncols=3, nrows=2, figsize=(20,9))
    figScores, axsScores = plt.subplots(ncols=3, nrows=2, figsize=(20,9))

    # Create (cummulative) histograms for several key values

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

    # Open network file
    pathNetwork = f"Networks/{getTime(num)}/"

    with open(pathNetwork + f'{subreddit}.pickle', 'rb') as f:
        network = pickle.load(f)
    
    users = network.users

    userDict = {user.id : user for user in users}

    postScoreList = [user.postScore for user in users]
    commentScoreList = [user.commentScore for user in users]
    totalScoreList = [user.postScore + user.commentScore for user in users]

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


    # Save figures
    figWeights.savefig(saveFolder + 'weightPlots.png', bbox_inches="tight")
    figScores.savefig(saveFolder + 'scorePlots.png', bbox_inches="tight")


    if UN:
        ### Visualize the UN

        # Create a Graph object
        user_graph = nx.DiGraph()

        # Add all users
        for user in users:
            if filterUsers(user):
                user_graph.add_node(user.id)

        # Add all (unweighted) edges 
        for user in users:
            for userOutID in user.outArcs.keys():
                if filterUsers(user) and filterUsers(userDict[userOutID]) and filterEdges(user, userOutID):
                    user_graph.add_edge(user.id, userOutID)

        # Create PyvisNetwork object
        user_network = PyvisNetwork(height="90%", width="100%", bgcolor="white", font_color="black", \
                    notebook=False, heading=f"User Network of subreddit {subreddit}")

        # Import the Graph object into the Network
        user_network.from_nx(user_graph)

        # Show the network
        user_network.barnes_hut(gravity=-80000, central_gravity=1.5, spring_length=250, spring_strength=0.0001, damping=0.09, overlap=0)

        # Save the network
        user_network.save_graph(saveFolder + f"UN_{subreddit}.html")

        # Additional options for visualisation
        user_network.show_buttons(filter_=['physics'])


    # Save remaining centrality measures
    # measures = ["VoteRank", "Harmonic", "EigenVector", "InDegree", "OutDegree"]
    measures = ["Harmonic", "EigenVector", "InDegree", "OutDegree"]
    for measure in measures:
        values = list(centralityDict[measure].values())
        # Exclude first lower 90%
        filteredValues = sorted(values)[len(values)//100*90:]
        bins = getBins(values)
        filteredBins = getBins(filteredValues)

        
        figCent, (ax, axFilter) = plt.subplots(ncols=1, nrows=2, figsize=(20,14))
        sns.histplot(data = values, bins = bins, ax = ax)
        ax.set_title(f"Centrality score of {measure}")
        sns.histplot(data = filteredValues, bins = filteredBins, ax = axFilter)
        axFilter.set_title(f"Centrality score of {measure} excluding lower 90%")
        # Save figure for later use
        figCent.savefig(saveFolder + f'{measure}.png', bbox_inches="tight")