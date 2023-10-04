import networkx as nx
import random
import matplotlib.pyplot as plt
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

def population_fitness(population):
    population_fitness = list()
    for i in range(len(population)):
        colouring = population[i]
        population_fitness.append((i, number_of_conflicts(colouring)))
    return population_fitness

def selection(population):
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
                    for vertex in graph.nodes:
                        if vertex in child[new_colour] and bad_vertex(child, vertex):
                            child[new_colour].remove(vertex)
                            child[colour].add(vertex)
                            break
                    child[new_colour].add(vertex)
    return child

"""
def wisdom_of_artificial_crowds(population):
    fitness = population_fitness(population)
    population = [population[x[0]] for x in sorted(fitness, key=lambda x: x[1])]
    best_colouring = population[0]
    most_used_colour = best_colouring.index(max(best_colouring, key=len))
    for colouring in population:
        for colour in colouring:
            for vertex in graph.nodes:
                if vertex in colour and bad_vertex(colouring, vertex):
                    colour.remove(vertex)
                    colouring[most_used_colour].add(vertex)
    return population
"""

def genetic_algorithm(number_of_colours):
    print()
    print('attempting to obtain: ' + str(number_of_colours) + '-colouring')
    print()
    iteration = 1
    population_size = 1000
    population = initial_population(population_size, number_of_colours)
    terminate = False
    while terminate == False:
        fitness = population_fitness(population)
        least_faults = sorted(fitness, key=lambda x: x[1])[0][1]
        best_colouring = population[sorted(fitness, key=lambda x: x[1])[0][0]]
        if least_faults == 0:
            print()
            print(str(len(best_colouring)) + '-colouring: ' + str(best_colouring))
            #draw_graph(best_colouring)
            return len(best_colouring)-1, terminate, best_colouring
        elif iteration > 20000:
            return None, True, None
        else:
            print('iteration ' + str(iteration) + ': ' + str(int(least_faults)) + ' faults')

        parents = selection(population)
        child = crossover(copy.deepcopy(parents), number_of_colours)
        if random.randint(0, 100)/100 <= 0.8:
            child = mutate(child)
        if number_of_conflicts(parents[0]) < number_of_conflicts(parents[1]):
            population.remove(parents[1])
        elif number_of_conflicts(parents[1]) < number_of_conflicts(parents[0]):
            population.remove(parents[0])
        else:
            population.remove(parents[random.randint(0, 1)])

        population.append(child)

        iteration += 1

def run_genetic_algorithm(initial_upper_bound):
    number_of_colours = initial_upper_bound
    terminate = False
    best_colouring = None
    while terminate == False:
        new_k, terminate, new_colouring = genetic_algorithm(number_of_colours)
        if new_k and new_colouring:
            best_colouring = new_colouring
            number_of_colours = new_k
    print()
    if best_colouring != None:
        print(str(len(best_colouring)) + '-colouring: ' + str(best_colouring))
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
    graph = represent_graph('graph_instances/'+ input('input graph representation file name: ')+ '.col.txt')
    #draw_graph(None)
    initial_upper_bound = max(nx.coloring.greedy_color(graph, strategy='DSATUR').values())
    number_of_colours = run_genetic_algorithm(initial_upper_bound)
