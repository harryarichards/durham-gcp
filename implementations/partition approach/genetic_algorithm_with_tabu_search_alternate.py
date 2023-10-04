import networkx as nx
import random
import matplotlib.pyplot as plt
import math
import copy
import time


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

    return ordered_vertices


def initial_colouring(number_of_colours):
    colouring = list()
    for i in range(number_of_colours):
        colouring.append(set())
    remaining_vertices = list(graph.nodes)
    for i in range(len(graph.nodes)):
        remaining_vertices = allowed_colour_classes(remaining_vertices, colouring)
        remaining_vertices = list(x[0] for x in remaining_vertices)
        vertex = remaining_vertices[0]
        neighbours = set(graph.neighbors(vertex))
        for colour in range(number_of_colours):
            if not neighbours.intersection(colouring[colour]):
                colouring[colour].add(vertex)
                remaining_vertices.remove(vertex)
                break

    return colouring, remaining_vertices


def allocate_remaining_vertices(number_of_colours, colouring, remaining_vertices):
    terminate = False
    while terminate == False:
        remaining_vertices = allowed_colour_classes(remaining_vertices, colouring)
        available_vertices = [vertex for vertex in remaining_vertices if vertex[1] != 0]
        available_vertices = sorted(available_vertices, key= lambda x: x[1])
        if not available_vertices:
            terminate = True
        else:
            vertex_tuple = available_vertices[0]
            neighbours = set(graph.neighbors(vertex_tuple[0]))
            for colour in range(number_of_colours):
                if not neighbours.intersection(colouring[colour]):
                    colouring[colour].add(vertex_tuple[0])
                    remaining_vertices.remove(vertex_tuple)
                    break
            remaining_vertices = [x[0] for x in remaining_vertices]
    for vertex in remaining_vertices:
        random_class = random.randint(0, number_of_colours - 1)
        colouring[random_class].add(vertex[0])
    colouring = [colour for colour in colouring if colour]
    return colouring


def initial_population(population_size, number_of_colours):
    population = list()
    partial_colouring, remaining_vertices = initial_colouring(number_of_colours)
    for i in range(population_size):
        colouring = allocate_remaining_vertices(number_of_colours, copy.deepcopy(partial_colouring), remaining_vertices)
        population.append(colouring)
    return population


def number_of_conflicts(colouring):
    number_of_conflicts = 0
    for colour in colouring:
        for vertex in colour:
            neighbours = set(graph.neighbors(vertex))
            number_of_conflicts += len(neighbours.intersection(colour))
    return int(number_of_conflicts/2)

def bad_vertices(colouring):
    bad_vertices = list()
    for colour in range(len(colouring)):
        for vertex in colouring[colour]:
            if set(graph.neighbors(vertex)).intersection(colouring[colour]):
                bad_vertices.append((vertex, colour))
    return bad_vertices


def neighbouring_colouring(current_colouring, colour_class_conflicts, tabu):
    original_colour = None
    chosen_colour = None
    chosen_vertex = None
    current_conflicts = number_of_conflicts(current_colouring)
    least_conflicts = copy.copy(current_conflicts)
    conflicting_vertices = bad_vertices(current_colouring)
    if not conflicting_vertices:
        return current_colouring, tabu

    for bad_vertex in conflicting_vertices:
        vertex_index = bad_vertex[0] - 1
        old_colour = bad_vertex[1]
        potential_colours = [colour for colour in range(len(current_colouring)) if colour != old_colour]
        for potential_colour in potential_colours:
            neighbouring_conflicts = current_conflicts - colour_class_conflicts[vertex_index][old_colour] + colour_class_conflicts[vertex_index][potential_colour]
            if neighbouring_conflicts < least_conflicts:
                original_colour = old_colour
                chosen_colour = potential_colour
                chosen_vertex = bad_vertex[0]
            elif tabu[vertex_index][old_colour] == 0 and chosen_vertex == None:
                original_colour = old_colour
                chosen_colour = potential_colour
                chosen_vertex = bad_vertex[0]

    if chosen_colour == None:
        bad_vertex = random.choice(conflicting_vertices)
        potential_colours = [colour for colour in range(len(current_colouring)) if colour != old_colour]
        original_colour = bad_vertex[1]
        chosen_vertex = bad_vertex[0]
        chosen_colour = random.choice(potential_colours)


    current_colouring[original_colour].remove(chosen_vertex)
    current_colouring[chosen_colour].add(chosen_vertex)
    tabu_tenure = random.randint(0, len(current_colouring)) + int(0.6 * number_of_conflicts(current_colouring))
    tabu[chosen_vertex-1][chosen_colour] += tabu_tenure
    for i in range(len(graph.nodes)):
        neighbours = set(graph.neighbors(i + 1))
        for j in range(len(current_colouring)):
            colour_class_conflicts[i][j] = len(neighbours.intersection(current_colouring[j]))
    return current_colouring, colour_class_conflicts, tabu


def tabu_search(colouring):
    number_of_iterations = 2000
    tabu = list()
    for i in range(len(graph.nodes)):
        tabu.append([])
        for j in range(len(colouring)):
            tabu[i].append(0)
    colour_class_conflicts = list()
    for i in range(len(graph.nodes)):
        neighbours = set(graph.neighbors(i+1))
        colour_class_conflicts.append([])
        for j in range(len(colouring)):
            colour_class_conflicts[i].append(len(neighbours.intersection(colouring[j])))

    current_colouring = copy.deepcopy(colouring)
    iteration = 0
    while iteration < number_of_iterations:
        current_colouring, colour_class_conflicts, tabu = neighbouring_colouring(copy.deepcopy(current_colouring), colour_class_conflicts, tabu)
        for vertex in range(len(graph.nodes)):
            for colour in range(len(current_colouring)):
                if tabu[vertex][colour]:
                    tabu[vertex][colour] -= 1
        iteration += 1

    return current_colouring


def choose_parents(population):
    return [random.choice(population), random.choice(population)]


def crossover(parents, number_of_colours):
    child = list()
    for i in range(number_of_colours):
        if not i%2:
            most_used_colour = max(parents[0], key=len)
            child.append(most_used_colour)
            parents[0].remove(most_used_colour)
            for colour in parents[1]:
                colour -= colour.intersection(most_used_colour)
        else:
            most_used_colour = max(parents[1], key=len)
            child.append(most_used_colour)
            parents[1].remove(most_used_colour)
            for colour in parents[0]:
                colour -= colour.intersection(most_used_colour)
    unassigned = set().union(*parents[0])
    for vertex in unassigned:
        child[random.randint(0, number_of_colours-1)].add(vertex)
    return child


def update_population(population, parents, child):
    population.append(child)
    if number_of_conflicts(parents[0]) > number_of_conflicts(parents[1]):
        population.remove(parents[0])
    elif number_of_conflicts(parents[1]) > number_of_conflicts(parents[0]):
        population.remove(parents[1])
    else:
        population.remove(parents[random.randint(0, 1)])
    return population


def check_population(population):
    min_conflicts = math.inf
    for colouring in population:
        if number_of_conflicts(colouring) == 0:
            return colouring, 0
        min_conflicts = min(min_conflicts, number_of_conflicts(colouring))
    return None, min_conflicts


def genetic_algorithm(number_of_colours):
    print()
    print('attempting to obtain: ' + str(number_of_colours) + '-colouring')
    print()
    iteration = 1
    population_size = 10
    population = initial_population(population_size, number_of_colours)
    terminate = False
    colouring = None
    while not terminate:
        colouring, min_conflicts = check_population(population)
        if min_conflicts == 0:
            print()
            print(str(len(colouring)) + '-colouring: ' + str(colouring))
            draw_graph(colouring)
            return len(colouring), False, colouring
        elif iteration > 500000:
            return None, True, None
        else:
            print('iteration ' + str(iteration) + ': ' + str(min_conflicts) + ' faults')
        parents = choose_parents(population)
        child = crossover(copy.deepcopy(parents), number_of_colours)
        if number_of_conflicts(child):
            new_child = tabu_search(copy.deepcopy(child))
            if number_of_conflicts(new_child) <= number_of_conflicts(child):
                child = copy.deepcopy(new_child)
        population = update_population(population, parents, child)
        iteration += 1
    return len(colouring)-1, False, colouring


def run_genetic_algorithm(initial_upper_bound):
    number_of_colours = initial_upper_bound
    terminate = False
    best_colouring = None
    while terminate == False:
        new_k, terminate, new_colouring = genetic_algorithm(number_of_colours)
        if new_k and new_colouring:
            best_colouring = new_colouring
            number_of_colours = new_k - 1
    print()
    if best_colouring != None:
        print(str(len(set(best_colouring.values()))) + '-colouring: ' + str(best_colouring))
    else:
        initial_upper_bound += 1
        run_genetic_algorithm(initial_upper_bound)
    return number_of_colours


def draw_graph(colouring):
    positions = nx.spring_layout(graph)
    if colouring == None:
        nx.draw_networkx(graph, positions, alpha=1.0, with_labels=False)
        plt.axis('off')
        plt.show()
    else:
        colours = list()
        for vertex in graph.nodes:
            for colour in range(len(colouring)):
                if vertex in colouring[colour]:
                    colours.append(colour)
        nx.draw_networkx(graph, positions, alpha=1.0, with_labels=False, node_color=colours, cmap = 'gist_ncar')
        plt.axis('off')
        plt.show()


if __name__ == "__main__":
    time0 = time.time()
    graph = represent_graph('graph_instances/'+ input('input graph representation file name: ') + '.col.txt')
    #draw_graph(None)
    initial_upper_bound = max(nx.coloring.greedy_color(graph, strategy='DSATUR').values())

    initial_upper_bound = 10
    number_of_colours = run_genetic_algorithm(initial_upper_bound)
    print(time.time() - time0)
