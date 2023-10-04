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


def initial_colouring(number_of_colours, vertices):
    colouring = list()
    for i in range(number_of_colours):
        colouring.append(set())
    unassigned = set(vertices)
    for vertex in vertices:
        neighbours = set(graph.neighbors(vertex))
        for colour in range(number_of_colours):
            if not neighbours.intersection(colouring[colour]):
                colouring[colour].add(vertex)
                unassigned.remove(vertex)
                break
    if unassigned:
        for vertex in unassigned:
            colouring[random.randint(0, number_of_colours-1)].add(vertex)
        return colouring
    else:
        print(str(number_of_colours) + '-colouring: ' + str(colouring))
        run_genetic_algorithm(number_of_colours-1)


def initial_population(population_size, number_of_colours):
    population = list()
    for i in range(population_size):
        vertices = sorted(graph.nodes, key=lambda x: random.random())
        colouring = initial_colouring(number_of_colours, vertices)
        population.append(colouring)
    for i in range(len(population)):
        population[i] = anneal(population[i])
    return population


def number_of_conflicts(colouring):
    number_of_conflicts = 0
    for colour in colouring:
        for vertex in colour:
            neighbours = set(graph.neighbors(vertex))
            number_of_conflicts += len(neighbours.intersection(colour))
    return int(number_of_conflicts/2)


def neighbouring_colouring(colouring):
    for colour in range(len(colouring)):
        for vertex in colouring[colour]:
            neighbours = set(graph.neighbors(vertex))
            if neighbours.intersection(colouring[colour]):
                colouring[colour].remove(vertex)
                others = [x for x in colouring if x != colouring[colour]]
                if others:
                    new_colour = random.choice(others)
                else:
                    new_colour = random.choice(colouring)
                new_colour.add(vertex)
                return colouring
    return colouring


def anneal(current_colouring):
    iteration = 1
    step = 0
    initial_temperature = 3*len(graph.nodes)
    temperature = initial_temperature
    stopping_temperature = 50

    while temperature > stopping_temperature and iteration < 10000:

        adjacent_colouring = neighbouring_colouring(copy.deepcopy(current_colouring))
        current_conflicts = number_of_conflicts(current_colouring)
        adjacent_conflicts = number_of_conflicts(adjacent_colouring)
        if adjacent_conflicts < current_conflicts:
            current_colouring = adjacent_colouring
            current_conflicts = adjacent_colouring
        else:
            swapping_prob = math.exp((adjacent_conflicts - current_conflicts) / initial_temperature)
            prob = random.uniform(0, 1)
            if prob <= swapping_prob:
                current_colouring = adjacent_colouring
                current_conflicts = adjacent_conflicts
                temperature = initial_temperature / (1 + math.log(1 + step))
                step += 1

        if current_conflicts == 0:
            print('found colouring...')
            return current_colouring

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

    while terminate == False:
        colouring, min_conflicts = check_population(population)
        if min_conflicts == 0:
            print()
            print(str(len(colouring)) + '-colouring: ' + str(colouring))
            draw_graph(colouring)
            return len(colouring), False, colouring
        elif iteration > 1000:
            return None, True, None
        else:
            print('iteration ' + str(iteration) + ': ' + str(min_conflicts) + ' faults')
        parents = choose_parents(population)
        child = crossover(copy.deepcopy(parents), number_of_colours)
        child = anneal(child)
        population = update_population(population, parents, child)
        print('iteration ' + str(iteration) + ': ' + str(min_conflicts) + ' faults')
        iteration += 1
    return number_of_colours-1, False, colouring


def run_genetic_algorithm(initial_upper_bound):
    number_of_colours = initial_upper_bound
    terminate = False
    best_colouring = None
    while terminate == False:
        new_k, terminate, new_colouring = genetic_algorithm(number_of_colours)
        if new_k and new_colouring:
            best_colouring = new_colouring
            number_of_colours -= 1
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
        colours = [colouring[vertex] for vertex in graph.nodes()]
        nx.draw_networkx(graph, positions, alpha=1.0, with_labels=False, node_color=colours, cmap = 'gist_ncar')
        plt.axis('off')
        plt.show()


if __name__ == "__main__":
    graph = represent_graph('graph_instances/'+ input('input graph representation file name: ')+ '.col.txt')
    #draw_graph(None)
    initial_upper_bound = max(nx.coloring.greedy_color(graph, strategy='DSATUR').values())
    initial_upper_bound = 9
    number_of_colours = run_genetic_algorithm(initial_upper_bound)
