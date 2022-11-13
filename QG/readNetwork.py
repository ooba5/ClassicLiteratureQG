import networkx as nx

G = nx.read_gml("test_written_graph.gml")

for n,nd in G.nodes.items():
    print(n, nd)

for e in G.edges.items():
    print(e)