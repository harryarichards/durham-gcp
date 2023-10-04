import networkx as nx
import matplotlib.pyplot as plt


def represent_graph(file_name):
    number_of_vertices = 0
    edges = list()
    with open(file_name) as file:
        for line in file:
            if line[0] == 'e':
                edge = (int(line.split()[1]), int(line.split()[2]))
                edges.append(edge)
            elif line[0] == 'p':
                number_of_vertices = int(line.split()[2])
    graph = nx.Graph(edges)
    graph.add_nodes_from(range(1, number_of_vertices))
    return graph


def allowed_colour_classes(remaining_vertices, colouring):
    ordered_vertices = list()
    for vertex in remaining_vertices:
        neighbours = set(graph.neighbors(vertex))
        allowed_classes = 0
        for colour in colouring:
            if not neighbours.intersection(colour):
                allowed_classes += 1
        ordered_vertices.append((vertex, allowed_classes))
    ordered_vertices = sorted(ordered_vertices, key=lambda x : x[1])
    ordered_vertices = list(x[0] for x in ordered_vertices)
    return ordered_vertices


def colour(number_of_colours):
    colouring = list()
    for i in range(number_of_colours):
        colouring.append(set())
    remaining_vertices = list(graph.nodes)
    for i in range(len(graph.nodes)):
        remaining_vertices = allowed_colour_classes(remaining_vertices, colouring)
        vertex = remaining_vertices[0]
        neighbours = set(graph.neighbors(vertex))
        for colour in range(len(colouring)):
            if not neighbours.intersection(colouring[colour]):
                colouring[colour].add(vertex)
                remaining_vertices.remove(vertex)
                break
            elif colour == len(colouring)-1:
                colouring.append(set(vertex))
                remaining_vertices.remove(vertex)
    return colouring

def draw_graph(colouring):
    positions = nx.nx_agraph.graphviz_layout(graph)
    if colouring == None:
        plt.title('Graph structure', fontsize=16)
        nx.draw_networkx(graph, positions, alpha=1.0, with_labels=False)
        plt.axis('off')
        plt.show()
    else:
        plt.title(str(len(colouring))+'-colouring',fontsize=16)
        colours = list()
        for vertex in graph.nodes:
            for colour in range(len(colouring)):
                if vertex in colouring[colour]:
                    colours.append(colour)
        nx.draw_networkx(graph, positions, alpha=1.0, with_labels=False, node_color=colours, cmap = plt.cm.hsv)
        plt.axis('off')
        plt.show()


if __name__ == "__main__":
    graph = represent_graph('graph_instances/'+ input('input graph representation file name: ')+ '.col.txt')
    draw_graph(None)
    k = max(nx.coloring.greedy_color(graph, strategy='DSATUR').values()) + 1
    colouring = colour(k)
    print(str(len(colouring)) + '-colouring: ' + str(colouring))
    draw_graph(colouring)