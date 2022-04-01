import pickle
from keyFeatures import Tree, Node
from userNetwork import Comment, User, Network, createDirectory
from networkx.algorithms import community
import matplotlib.pyplot as plt
import seaborn as sns
from time import perf_counter


# Visualise UN
import networkx as nx
from pyvis.network import Network as PyvisNetwork


# Path to store the visualisations
pathNetwork = "Networks/"

subreddit = "news"

plots = False



time1 = perf_counter()

if __name__ == "__main__":

    with open(pathNetwork + f'{subreddit}.pickle', 'rb') as f:
        network = pickle.load(f)
    
    users = network.users

    print(len(users))

    userDict = {user.id : user for user in users}

    # Path to store the visualisations
    path = f"Figures/{subreddit}/"

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

    if plots:
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

    
        # Save figures
        figWeights.savefig(path + f'weightPlots.png', bbox_inches="tight")
        figScores.savefig(path + f'scorePlots.png', bbox_inches="tight")



    ### Visualize the UN

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
    user_network.save_graph(path + f"UN_{subreddit}.html")

    # Additional options for visualisation
    user_network.show_buttons(filter_=['physics'])

    if plots:
        # Extract some key features
        figCent, axs = plt.subplots(ncols=1, nrows=4, figsize=(20,14))
        sns.histplot(data=nx.degree_histogram(user_graph), bins = getBins(nx.degree_histogram(user_graph)), ax = axs[0])
        axs[0].set_title(f"Histogram degree distribution")


        betweennessValues = list(filter(lambda x: x >0.01 , nx.betweenness_centrality(user_graph).values()))
        sns.histplot(data=betweennessValues, bins=20, ax = axs[1])
        axs[1].set_title(f"Histogram betweenness centrality")

        closenessValues = list(filter(lambda x: x >0.01 , nx.closeness_centrality(user_graph).values()))
        sns.histplot(data=closenessValues, bins=100, ax = axs[2])
        axs[2].set_title(f"Histogram closeness centrality")

        sns.histplot(data=list(map(lambda x: 1/x, closenessValues)), bins=100, ax = axs[3])
        axs[3].set_title(f"Histogram reciprocal closeness centrality")


        # Save figure for later use
        figCent.savefig(path + f'centralityMeasures.png', bbox_inches="tight")


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

    resultsPath = "Results/"
    createDirectory(resultsPath)

    # Save the key features
    with open(resultsPath + f'{subreddit}_key_features.pickle', 'wb') as f:
        pickle.dump(centralityDict, f, protocol=pickle.HIGHEST_PROTOCOL)


    time2 = perf_counter()

    print(time2 - time1)

    print("DONE")