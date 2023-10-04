import networkx as nx
import random
import math
import copy

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
    return colouring, remaining_vertices


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
    """
    for colour in range(len(child)):
        for vertex in graph.nodes:
            if vertex in child[colour] and bad_vertex(child, vertex):
                options = valid_colours(child, vertex)
                if options:
                    child[colour].remove(vertex)
                    child[random.choice(options)].add(vertex)
                else:
                    new_colour = random.randint(0, len(child)-1)
                    for vertex in graph.nodes:
                        if vertex in child[new_colour] and bad_vertex(child, vertex):
                            child[new_colour].remove(vertex)
                            child[colour].add(vertex)
                            break
                    child[new_colour].add(vertex)
    """
    unpicked = False
    vertex = None
    previous_colour = None
    while unpicked == False:
        vertex = random.choice(list(graph.nodes))
        if bad_vertex(child, vertex):
            unpicked = True
    for colour in child:
        if vertex in colour:
            previous_colour = colour
            colour.remove(vertex)
            break

    potential_colours = [colour for colour in range(len(child)) if colour != previous_colour]
    new_colour = random.choice(potential_colours)
    child[new_colour].add(vertex)
    return child

def simulated_annealing(number_of_colours):
    iteration = 1
    step = 0
    initial_temperature = 10 * len(graph.nodes)
    temperature = initial_temperature
    stopping_temperature = len(graph.nodes)

    partial_colouring, remaining_vertices = initial_colouring(number_of_colours)
    current_colouring = allocate_remaining_vertices(number_of_colours, copy.deepcopy(partial_colouring), remaining_vertices)
    while temperature > stopping_temperature:
        adjacent_colouring = mutate(current_colouring)
        current_conflicts = number_of_conflicts(current_colouring)
        adjacent_conflicts = number_of_conflicts(adjacent_colouring)

        if adjacent_conflicts < current_conflicts:
            current_colouring = adjacent_colouring
            current_conflicts = adjacent_colouring
        else:
            swapping_prob = math.exp((adjacent_conflicts - current_conflicts) / max(1, math.log(temperature)))
            prob = random.uniform(0, 1)
            if prob <= swapping_prob:
                current_colouring = adjacent_colouring
                current_conflicts = adjacent_conflicts
                temperature = initial_temperature / (1 + math.log(1 + step))
                step += 1


        if current_conflicts == 0:
            return current_colouring, len(set(current_colouring.values()))
        else:
            print('iteration ' + str(iteration) +': ' + str(int(current_conflicts)))

        iteration += 1

    return None, math.inf

def run_simulated_annealing(initial_upper_bound):
    number_of_colours = initial_upper_bound
    min_upper_bound = math.inf
    min_colouring = None
    terminate = False
    while not terminate:
        print()
        print('attempting to obtain: ' + str(number_of_colours) + '-colouring')
        print()
        colouring, upper_bound = simulated_annealing(number_of_colours)
        if upper_bound <= min_upper_bound and upper_bound != math.inf:
            min_upper_bound = upper_bound
            min_colouring = colouring
            print()
            print( str(min_upper_bound) + '-colouring: ' + str(colouring))
            print()
            number_of_colours -= 1
        elif min_colouring is not None:
            terminate = True
        else:
            number_of_colours += 1
    print()
    print(str(min_upper_bound) + '-colouring: ' + str(min_colouring))
    print()






if __name__ == "__main__":
    graph = represent_graph('graph_instances/' + input('input graph representation file name: ') + '.col.txt')
    initial_upper_bound= max(nx.coloring.greedy_color(graph, strategy='DSATUR').values())
    run_simulated_annealing(initial_upper_bound)