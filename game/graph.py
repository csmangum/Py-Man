import networkx as nx
import matplotlib.pyplot as plt

# The given string representation
maze_string = """
X X X X X X X X X X ...
... (rest of your string here)
X X X X X X X X X X X X X X X X X X X X X X X X X X X X
"""

# Convert the string representation to a 2D list
maze_2d = [list(row.split()) for row in maze_string.strip().split("\n")]

# Create a grid graph
G = nx.grid_2d_graph(len(maze_2d), len(maze_2d[0]))

for i in range(len(maze_2d)):
    for j in range(len(maze_2d[0])):
        G.nodes[(i, j)]["label"] = maze_2d[i][j]

# Draw the graph
pos = dict((n, n) for n in G.nodes())
labels = nx.get_node_attributes(G, "label")
nx.draw(G, pos, with_labels=True, labels=labels)
plt.show()


import networkx as nx
import matplotlib.pyplot as plt


def create_grid_graph(dim):
    G = nx.grid_2d_graph(dim, dim)

    # Wrap around the edges
    for x in range(dim):
        G.add_edge((x, 0), (x, dim - 1))
        G.add_edge((0, x), (dim - 1, x))

    # Label nodes with integers instead of (x, y) coordinates
    relabel_dict = {(x, y): y * dim + x for x, y in G.nodes()}
    G = nx.relabel_nodes(G, relabel_dict)

    return G


def coordinate_to_node_label(x, y, dim):
    return y * dim + x


# Create a 10x10 grid graph
G = create_grid_graph(10)

# Draw the graph with updated position mapping
dim = 10
pos = {(x + y * 10): (x, dim - 1 - y) for x in range(dim) for y in range(dim)}
nx.draw(G, pos, with_labels=True, node_size=400, node_color="lightblue")
plt.show()
