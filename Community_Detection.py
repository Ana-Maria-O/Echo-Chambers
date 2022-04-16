import pickle
import networkx as nx
import matplotlib.pyplot as plt
from community import community_louvain
from userNetworkFunction import Network, User

def PullOutChanges(graph: nx.classes.graph.Graph, graph_new: nx.classes.graph.Graph) -> list:
    changes = []

    # check which edges to change
    for node in graph.nodes:
        if not graph_new.has_node(node):
            changes.append({'type': 'remove node', 'node': node})
        
    for edge in graph.edges:
        if not graph_new.has_edge(edge[0], edge[1]):
            changes.append({'type': 'remove edge', 'node': edge[0], 'node2' : edge[1]})

    for node in graph_new.nodes:
        if not graph.has_node(node):
            changes.append({'type': 'add node', 'node': node})

    for edge in graph_new.edges:
        if not graph.has_edge(edge):
            changes.append({'type': 'add_edge', 'node': edge[0], 'node2': edge[1]})
    
    return changes

def ConstructCompressedGraph(graph, graph_new, communities) -> nx.classes.graph.Graph:
    delta_G = PullOutChanges(graph, graph_new)
    
    for change in delta_G:
        if change['type'] == 'remove node':
            u = change['node']
            #TODO: replace communities[u] with a subset of nodes in u's community
            super_nodes, super_edges = RemoveNode(u, communities[u])
        
        if change['type'] == 'remove edge':
            u = change['node']
            v = change['node2']

            if communities[u] == communities[v]:


def Louvain(graph = nx.classes.graph.Graph) -> dict:
    G = community_louvain.best_partition(graph)
    print(type(G))
    return G

def C_Blondel(graph, graph_new, communities) -> dict:
    compressed = ConstructCompressedGraph(graph, graph_new, communities)
    communities_new = Louvain(compressed)

    return communities_new

# Makes the user network of the indicated subreddit
# Input: string which indicates a subreddit
# Output: an nx unidrected weighted graph
def makeGraph(subreddit = str) -> nx.classes.graph.Graph:
    pfile = open('Networks//' + subreddit + '.pickle', 'rb')
    network = pickle.load(pfile)
    pfile.close()

    G = nx.Graph()
    count = 0

    for user in network.users:
        count += 1
        for user2 in user.outArcs:
            if G.has_edge(user.id, user2):
                G[user.id][user2]["weight"] = G[user.id][user2]["weight"] + user.outArcs[user2][0]
            else:
                G.add_edge(user.id, user2, weight=user.outArcs[user2][0])
    return G

def main():
    subreddit = 'lockdownskepticism'
    G = makeGraph(subreddit)
    # print(G.edges)

    '''test = nx.Graph()
    test.add_edge('a', 'b')
    for edge in test.edges:
        print(test.has_edge(edge[0], edge[1]))
    test.add_edge('a','b', weight=3)
    print(test.edges.data())
    test['b']['a']["weight"] = 4
    print(test.edges.data())'''
'''
    elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 2]
    esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 2]

    pos = nx.spring_layout(G, seed=7)  # positions for all nodes - seed for reproducibility

    # nodes
    nx.draw_networkx_nodes(G, pos, node_size=700)

    # edges
    nx.draw_networkx_edges(G, pos, edgelist=elarge, width=6)
    nx.draw_networkx_edges(
        G, pos, edgelist=esmall, width=6, alpha=0.5, edge_color="b", style="dashed"
    )

    # labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")

    ax = plt.gca()
    ax.margins(0.08)
    plt.axis("off")
    plt.tight_layout()
    plt.show()'''

    
            

if __name__ == "__main__":
    main()