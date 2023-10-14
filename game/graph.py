
import networkx as nx
import matplotlib.pyplot as plt

def create_grid_graph(L, W):
    # Create an empty graph
    G = nx.Graph()

    # Add nodes to the graph
    for i in range(L):
        for j in range(W):
            G.add_node((i, j))

    # Add edges to the graph
    for i in range(L):
        for j in range(W):
            # Connect to the node to the right
            if i < L - 1:
                G.add_edge((i, j), (i + 1, j))
            # Connect to the node below
            if j < W - 1:
                G.add_edge((i, j), (i, j + 1))

    return G

# Example usage:
L, W = 5, 5
G = create_grid_graph(L, W)

# one hop from 2,2
print(G[(4,4)])

# Draw the graph
pos = {(x, y): (y, -x) for x, y in G.nodes()}
nx.draw(G, pos=pos, with_labels=True, node_size=100, node_color="blue")
plt.show()
