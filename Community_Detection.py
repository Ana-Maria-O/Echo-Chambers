import pickle
import networkx as nx
import matplotlib.pyplot as plt
from community import community_louvain
from userNetworkFunction import Network, User

alpha = 1
sgraph_nodes = {}

# returns a list of all changes that were made to graph in order to become graph_new
# if changes['type'] == 'remove node' or 'add node' then changes['node'] is the 
# name of the node that was removed/added
# if changes['type'] == 'remove edge' or 'add edge' then changes['node'] and
# changes['node2'] are the names of the nodes that the edge connects
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
        if not graph.has_edge(edge[0], edge[1]):
            changes.append({'type': 'add edge', 'node': edge[0], 'node2': edge[1]})
    
    return changes

def AddSuperEdges(graph: nx.classes.graph.Graph, supergraph: nx.classes.graph.Graph) -> nx.classes.graph.Graph:
    comms = {}
    for comm1 in supergraph.nodes:
        comms[comm1] = 1
        for comm2 in supergraph.nodes:
            if comm2 not in comms:
                for node1 in supergraph.nodes[comm1]['nodes']:
                    for node2 in supergraph.nodes[comm2]['nodes']:
                        if graph.has_edge(node1, node2):
                            # print(graph[node1][node2]['weight'])
                            if supergraph.has_edge(comm1, comm2):
                                supergraph.add_edge(comm1, comm2, weight=supergraph[comm1][comm2]['weight'] + graph[node1][node2]['weight'])
                            else:
                                supergraph.add_edge(comm1, comm2, weight = graph[node1][node2]['weight'])

    return supergraph

def removeFromSupergraph(supergraph, node):
    found = False
    # print(node)
    for nodes in list(supergraph.nodes(data="nodes")):
        # print(set(nodes[1])
        # print(set(node))
        if not found:
                if len(list(set(node) & set(nodes[1]))) > 0:
                    # print("before remove: " + str(supergraph.nodes(data=True)))
                    supergraph.remove_node(nodes[0])
                    # print("after remove: " + str(supergraph.nodes(data=True)))
                    found = True
        else:
            nx.relabel_nodes(supergraph, {nodes[0]: nodes[0] - 1})

    return supergraph

def RemoveNode(node: str, communities: dict, graph: nx.classes.graph.Graph, supergraph: nx.classes.graph.Graph):
    global sgraph_nodes

    # list of nodes in the community of node
    community = [key for key in communities if communities[key] == communities[node] and key != node]
    
    # if this node was already accounted for in the supergraph or its community 
    # was already broken, don't do this function again
    if node in sgraph_nodes or (communities[node], True) in sgraph_nodes.values():
        return supergraph
    else:
        if not((communities[node], False) in sgraph_nodes.values()):
            key = supergraph.number_of_nodes()
            supergraph.add_node(key, nodes=community)
            sgraph_nodes[node] = (communities[node], False)

    # get degree of the node
    deg = graph.degree(node)

    # sum of degrees in the community
    comm_deg_sum = deg
    for item in community:
        comm_deg_sum += graph.degree(item)
    
    # average degree in community
    deg_c = comm_deg_sum / (len(community) + 1)

    if deg >= alpha * deg_c:
        # update sgraph_nodes that this community was broken
        og_node = list(sgraph_nodes.keys())[list(sgraph_nodes.values()).index((communities[node], False))]
        sgraph_nodes[og_node] = (communities[node], True)
        
        # if the whole community was already in the supergraph, remove it and re-update the label for every following node
        supergraph = removeFromSupergraph(supergraph, community)

        # get the subcommunities in community
        subcom = Louvain(graph.subgraph(community))
        # print(subcom)
        subcom_values = set(subcom.values())

        # add each subcommunity(supernode) to an integer
        for item in subcom_values:
            # get all nodes from this subcommunity
            c_list = [key for key in subcom if subcom[key] == item]

            # link the nodes from the subcommunity to an integer
            key = supergraph.number_of_nodes()
            supergraph.add_node(key, nodes=c_list)

    return supergraph

# DONE: add superedges function -> joi
# TODO: test everything -> vineri + sambata
# TODO: write code in main -> duminica
def ConstructCompressedGraph(graph: nx.classes.graph.Graph, graph_new: nx.classes.graph.Graph, communities: dict) -> nx.classes.graph.Graph:
    delta_G = PullOutChanges(graph, graph_new)
    supergraph = nx.Graph()
    
    for change in delta_G:
        if change['type'] == 'remove node':
            u = change['node']
            supergraph = RemoveNode(u, communities, graph, supergraph)
        
        if change['type'] == 'remove edge':
            u = change['node']
            v = change['node2']

            if communities[u] == communities[v]:
                supergraph = RemoveNode(u, communities, graph, supergraph)
                supergraph = RemoveNode(v, communities, graph, supergraph)
        
        if change['type'] == 'add node':
            u = change['node']
            supergraph.add_node(supergraph.number_of_nodes(), [u])

            for neighbor in graph_new.neighbors(u):
                if neighbor in communities:
                    supergraph = RemoveNode(neighbor, communities, graph, supergraph)

        if change['type'] == 'add edge':
            u = change['node']
            v = change['node2']

            n = supergraph.number_of_nodes()
            in_sg = False

            for node in supergraph.nodes(data="nodes"):
                if u in node[1] or v in node[1]:
                    in_sg = True
                    break

            if not in_sg:
                supergraph.add_edge((n, [u]), (n + 1, [v]), graph_new[u][v]["weight"])

            if u in communities and v in communities and communities[u] != communities[v]:
                supergraph = RemoveNode(u, communities[u], graph, supergraph)
                supergraph = RemoveNode(v, communities[v], graph, supergraph)

    
    supergraph = AddSuperEdges(graph_new, supergraph)

    return supergraph
            

def Louvain(graph = nx.classes.graph.Graph) -> dict:
    G = community_louvain.best_partition(graph)
    # print(type(G))
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
    # subreddit = 'lockdownskepticism'
    # G = makeGraph(subreddit)
    # print(G.nodes(data="weight"))
    G = nx.Graph()
    G.add_edge(1, 2)
    # l = list(G.nodes(data="dt"))
    # print(l[0][0])
    # G.remove_node(l[0][0])
    # print(G.nodes)
    # communities = Louvain(G)
    #print(Louvain(G))
    # print(G.edges)
    print(G[1])

    # print(G.degree)
    # community = [key for key in communities if communities[key] == 2]
    # sub = Louvain(G.subgraph(community))
    # print(sub)

    # a = {5: "a"}
    # b = {5: "b"}
    # a.update(b)
    # print(a)
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