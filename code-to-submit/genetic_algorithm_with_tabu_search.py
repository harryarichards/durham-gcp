import networkx as nx
import random
import matplotlib.pyplot as plt
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
    random.shuffle(bad_vertices)
    return bad_vertices


def neighbouring_colour(colouring, tabu):
    neighbour = copy.deepcopy(colouring)
    conflicting_vertices = bad_vertices(neighbour)
    if conflicting_vertices:
        vertex_tuple = random.choice(conflicting_vertices)
    else:
        return neighbour, tabu
    vertex = vertex_tuple[0]
    old_colour = vertex_tuple[1]
    neighbour[old_colour].remove(vertex)
    potential_colours = [colour for colour in range(len(tabu[vertex - 1])) if colour != old_colour]
    potential_colour = random.choice(potential_colours)
    neighbour[potential_colour].add(vertex)


    current_conflicts = number_of_conflicts(colouring)
    neighbouring_conflicts = number_of_conflicts(neighbour)

    if neighbouring_conflicts < current_conflicts:
        tabu_tenure = random.randint(0, 9) + int(0.6 * neighbouring_conflicts)
        tabu[vertex - 1][potential_colour] = tabu_tenure
        return neighbour, tabu
    elif tabu[vertex - 1][potential_colour] == 0 and neighbouring_conflicts <= current_conflicts:
        tabu_tenure = random.randint(0, 9) + int(0.6 * neighbouring_conflicts)
        tabu[vertex - 1][potential_colour] = tabu_tenure
        return neighbour, tabu
    else:
        tabu_tenure = random.randint(0, 9) + int(0.6 * neighbouring_conflicts)
        tabu[vertex - 1][potential_colour] = tabu_tenure
        return None, tabu


def get_best_neighbour(number_of_iterations, colouring, tabu):
    i = 0
    current_colouring = copy.deepcopy(colouring)
    while i < number_of_iterations:
        neighbour, tabu = neighbouring_colour(copy.deepcopy(current_colouring), tabu)
        if neighbour and number_of_conflicts(neighbour) <= number_of_conflicts(current_colouring):
            current_colouring = copy.deepcopy(neighbour)
        for vertex in range(len(graph.nodes)):
            for colour in range(len(colouring)):
                if tabu[vertex][colour]:
                    tabu[vertex][colour] -= 1
        i += 1
    return current_colouring


def tabu_search(colouring):
    number_of_iterations = 1000
    tabu = list()
    for i in range(len(graph.nodes)):
        tabu.append([])
        for j in range(len(colouring)):
            tabu[i].append(0)

    best_neighbour = get_best_neighbour(number_of_iterations, copy.deepcopy(colouring), tabu)

    return best_neighbour


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
    graph = represent_graph('graph_instances/'+ input('input graph representation file name: ') + '.col.txt')
    draw_graph(None)
    initial_upper_bound = max(nx.coloring.greedy_color(graph, strategy='DSATUR').values()) + 10
    number_of_colours = run_genetic_algorithm(initial_upper_bound)