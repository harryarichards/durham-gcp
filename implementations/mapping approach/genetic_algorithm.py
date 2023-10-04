import networkx as nx
import random
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

def random_colour(number_of_colours):
    colouring = {}
    for i in range(1, len(graph.nodes())+1):
        colouring[i] = random.randint(1, number_of_colours)
    return colouring

def initial_population(population_size, number_of_colours):
    population = list()
    for i in range(population_size):
        colouring = random_colour(number_of_colours)
        population.append(colouring)
    return population

def number_of_conflicts(colouring):
    number_of_conflicts = 0
    for edge in graph.edges:
        if colouring[edge[0]] == colouring[edge[1]]:
            number_of_conflicts += 1
    return number_of_conflicts

def population_fitness(population):
    population_fitness = list()
    for i in range(len(population)):
        colouring = population[i]
        population_fitness.append((i, number_of_conflicts(colouring)))
    return population_fitness

def selection1(population_size, population_fitness):
    parents = list()
    while len(parents) < population_size:
        temp_parents1 = [random.choice(population_fitness), random.choice(population_fitness)]
        temp_parents2 = [random.choice(population_fitness), random.choice(population_fitness)]
        parent1 = min(temp_parents1, key=lambda x: x[1])[0]
        parent2 = min(temp_parents2, key=lambda x: x[1])[0]
        parents.append((parent1, parent2))
    return parents

def selection2(population_size, population_fitness):
    population_fitness = sorted(population_fitness, key=lambda x:x[1])
    potential_parents = [colouring for colouring in population_fitness if colouring[1] <= population_fitness[1][1]]
    parents = list()
    while len(parents) < population_size:
        parents.append((random.choice(potential_parents)[0], random.choice(potential_parents)[0]))
    return parents

def crossover(parents, population):
    new_population = list()
    for parents_pair in parents:
        index = random.randint(1, len(graph.nodes()))
        parent1, parent2 = population[parents_pair[0]], population[parents_pair[1]]
        child1, child2 = {}, {}
        for j in range(1, index+1):
            child1[j] = parent1[j]
            child2[j] = parent2[j]
        for j in range(index+1, len(graph.nodes())+1):
            child1[j] = parent2[j]
            child2[j] = parent1[j]

        if number_of_conflicts(child1) < number_of_conflicts(child2):
            chosen_child = child1
        else:
            chosen_child = child2
        new_population.append(chosen_child)
    return new_population

def bad_vertex(colouring, vertex):
    for neighbour in list(graph.neighbors(vertex)):
        if colouring[neighbour] == colouring[vertex]:
            return True
    return False

def mutate1(population, number_of_colours):
    all_colours = list(range(1, number_of_colours))
    for colouring in population:
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
    return population


def mutate2(population, number_of_colours):
    all_colours = list(range(1, number_of_colours))
    for colouring in population:
        for vertex in colouring:
            if bad_vertex(colouring, vertex):
                colouring[vertex] = random.choice(all_colours)
    return population


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
            print(str(len(set(best_colouring.values()))) + '-colouring: ' + str(best_colouring))
            draw_graph(best_colouring)
            return len(set(best_colouring.values())), terminate, best_colouring
        elif iteration > 20000:
            return None, True, None
        else:
            print('iteration ' + str(iteration) + ': ' + str(int(least_faults)) + ' faults')

        if least_faults <= max(int(len(graph.nodes) / 20), 4):
            parents = selection2(population_size, fitness)
            population = crossover(parents, population)
            population = mutate2(population, number_of_colours)
        else:
            parents = selection1(population_size, fitness)
            population = crossover(parents, population)
            population = mutate1(population, number_of_colours)

        iteration += 1


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
        colours = [colouring[vertex] for vertex in graph.nodes()]
        nx.draw_networkx(graph, positions, alpha=1.0, with_labels=False, node_color=colours, cmap = 'gist_ncar')
        plt.axis('off')
        plt.show()


if __name__ == "__main__":
    graph = represent_graph('graph_instances/'+ input('input graph representation file name: ')+ '.col.txt')
    draw_graph(None)
    initial_upper_bound = max(nx.coloring.greedy_color(graph, strategy='DSATUR').values())
    number_of_colours = run_genetic_algorithm(initial_upper_bound)






