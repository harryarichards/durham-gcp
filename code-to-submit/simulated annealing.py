import networkx as nx
import random
import matplotlib.pyplot as plt
import copy
import math


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


def initial_colouring(number_of_colours):
    colouring = list()
    for i in range(number_of_colours):
        colouring.append(set())
    remaining_vertices = list(graph.nodes)
    for i in range(len(graph.nodes)):
        remaining_vertices = allowed_colour_classes(remaining_vertices, colouring)
        vertex = remaining_vertices[0]
        neighbours = set(graph.neighbors(vertex))
        for colour in range(number_of_colours):
            if not neighbours.intersection(colouring[colour]):
                colouring[colour].add(vertex)
                remaining_vertices.remove(vertex)
                break
    colouring = allocate_remaining_vertices(number_of_colours, copy.deepcopy(colouring), remaining_vertices)
    return colouring


def allocate_remaining_vertices(number_of_colours, colouring, remaining_vertices):
    random_class = random.randint(0, number_of_colours - 1)
    for vertex in remaining_vertices:
        colouring[random_class].add(vertex)
    colouring = [colour for colour in colouring if colour]
    return colouring


def number_of_conflicts(colouring):
    number_of_conflicts = 0
    for colour in colouring:
        for vertex in colour:
            neighbours = set(graph.neighbors(vertex))
            number_of_conflicts += len(neighbours.intersection(colour))
    return int(number_of_conflicts/2)


def bad_vertex(colouring, vertex):
    for colour in colouring:
        if vertex in colour and colour.intersection(set(graph.neighbors(vertex))):
            return True
    return False


def valid_colours(colouring, vertex):
    valid_colours = list()
    for colour in range(len(colouring)):
        if not colouring[colour].intersection(set(graph.neighbors(vertex))):
            valid_colours.append(colour)
    return valid_colours


def mutate(child):
    for colour in range(len(child)):
        for vertex in graph.nodes:
            if vertex in child[colour] and bad_vertex(child, vertex):
                options = valid_colours(child, vertex)
                if options:
                    child[colour].remove(vertex)
                    child[random.choice(options)].add(vertex)
                else:
                    new_colour = random.randint(0, len(child)-1)
                    child[colour].remove(vertex)
                    child[new_colour].add(vertex)
    return child


def anneal(number_of_colours):
    print()
    print('attempting to obtain: ' + str(number_of_colours) + '-colouring')
    print()
    iteration = 1
    step = 0
    initial_temperature = 200
    temperature = initial_temperature
    stopping_temperature = 20
    current_colouring = initial_colouring(number_of_colours)

    if number_of_conflicts(current_colouring) == 0:
        print(str(len(current_colouring)) + '-colouring: ' + str(current_colouring))
        draw_graph(current_colouring)
        return len(current_colouring), False, current_colouring

    while temperature > stopping_temperature:
        adjacent_colouring = mutate(copy.deepcopy(current_colouring))
        current_conflicts = number_of_conflicts(current_colouring)
        adjacent_conflicts = number_of_conflicts(adjacent_colouring)

        if adjacent_conflicts < current_conflicts:
            current_colouring = copy.deepcopy(adjacent_colouring)
            current_conflicts = copy.copy(adjacent_conflicts)
        else:
            swapping_prob = math.exp((current_conflicts - adjacent_conflicts) / max(1, math.log(temperature)))
            prob = random.uniform(0, 1)
            if prob <= swapping_prob:
                current_colouring = copy.deepcopy(adjacent_colouring)
                current_conflicts = copy.copy(adjacent_conflicts)
        temperature = initial_temperature / (1 + math.log(1 + step))
        step += 1


        if current_conflicts == 0:
            print(str(len(current_colouring)) + '-colouring: ' + str(current_colouring))
            draw_graph(current_colouring)
            return len(current_colouring), False, current_colouring

        print('iteration ' + str(iteration) + ': ' + str(number_of_conflicts(current_colouring)) + ' faults')
        iteration += 1

    return None, True, None


def run_simulated_annealing(initial_upper_bound):
    number_of_colours = initial_upper_bound
    terminate = False
    best_colouring = None
    while terminate == False:
        new_k, terminate, new_colouring = anneal(number_of_colours)

        if new_k and new_colouring:
            best_colouring = new_colouring
            number_of_colours = new_k - 1
    print()
    if best_colouring != None:
        print(str(len(best_colouring)) + '-colouring: ' + str(best_colouring))
    else:
        initial_upper_bound += 1
        run_simulated_annealing(initial_upper_bound)
    return number_of_colours


def draw_graph(colouring):
    positions = nx.spring_layout(graph)
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
    initial_upper_bound = max(nx.coloring.greedy_color(graph, strategy='DSATUR').values()) + 10
    number_of_colours = run_simulated_annealing(initial_upper_bound)