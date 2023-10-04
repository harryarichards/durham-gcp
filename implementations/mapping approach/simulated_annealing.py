import networkx as nx
import random
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


def random_colour(number_of_colours):
    colouring = {}
    for i in range(1, len(graph.nodes())+1):
        colouring[i] = random.randint(1, number_of_colours)
    return colouring


def number_of_conflicts(colouring):
    number_of_conflicts = 0
    for edge in graph.edges:
        if colouring[edge[0]] == colouring[edge[1]]:
            number_of_conflicts += 1
    return number_of_conflicts


def bad_vertex(colouring, vertex):
    for neighbour in list(graph.neighbors(vertex)):
        if colouring[neighbour] == colouring[vertex]:
            return True
    return False


def mutate1(colouring, number_of_colours):
    all_colours = list(range(1, number_of_colours))
    for vertex in colouring:
        if bad_vertex(colouring, vertex):
            valid_colours = all_colours.copy()
            for neighbour in graph.neighbors(vertex):
                if colouring[neighbour] in valid_colours:
                    valid_colours.remove(colouring[neighbour])
            if valid_colours:
                colouring[vertex] = random.choice(valid_colours)
            else:
                colouring[vertex] = random.choice(all_colours)
    return colouring


def simulated_annealing(number_of_colours):
    iteration = 1
    step = 0
    initial_temperature = 10 * len(graph.nodes)
    temperature = initial_temperature
    stopping_temperature = len(graph.nodes)

    current_colouring = random_colour(number_of_colours)
    while temperature > stopping_temperature:
        adjacent_colouring = mutate1(current_colouring, number_of_colours)
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