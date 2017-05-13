import networkx as nx
import networkx.algorithms.isomorphism as iso
import subprocess


G = nx.DiGraph()

edge_list = [('node1', 'node2'), ('node2', 'node3'), ('node3', 'node4')]

edge_list.append(('node4', 'node5'))

print edge_list


#edge_list = edge_list+('node4', 'node5')

#print edge_list


G.add_edges_from(edge_list, weight=1)

print G.edges()

H = nx.DiGraph()
H.add_edges_from([('node1', 'node3'), ('node3', 'node4')], weight=1)
result = iso.is_isomorphic(G, H)

print result

output = subprocess.check_output(['grep', 'Test'])

print output

# check if the graphs are isomorphic
    # if isomorphic means same graph structure  new node names, check the list for the node names
    # if not isomorphic meaning changes in flow, create new calvin file