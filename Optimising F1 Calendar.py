import random
import pandas as pd
from math import acos, sin, cos

# Read Excel file with all info of each race
racesFile = pd.read_excel('Races.xlsx')
racesInfo = racesFile.values.tolist()

# [Race Number, Country, City, Latitude, Longitude]
races = [[sublist[0], sublist[1], sublist[2], sublist[10], sublist[11]] for sublist in racesInfo]

# Parameter settings which can be changed to affect code
size = 1000
num_of_gens = 150
mutation_rate = 0.05


# Create random solutions
def create_order():
    digits = list(range(0, 24))
    return random.sample(digits, len(digits))


# Calculate the total distance for a solution
def cal_distance(order):
    distance = 0
    for i in range(len(races) - 1):
        # Distance in km between two places on Earth given latitude and longitude in radians
        distance += acos((sin(races[order[i]][3]) * sin(races[order[i + 1]][3])) + (
                cos(races[order[i]][3]) * cos(races[order[i + 1]][3])) * (
                             cos(races[order[i + 1]][4] - races[order[i]][4]))) * 6371
    return distance


# Perform order crossover on parents to create child
def crossover(parent1, parent2):
    # Cut 1 is smaller than cut 2
    cut1 = cut2 = random.randint(0, len(races))
    while cut1 == cut2:
        cut2 = random.randint(0, len(races))
    if cut1 > cut2:
        cut1, cut2 = cut2, cut1

    # Child has cut segment from parent 1 and filled with 'None' everywhere else
    child = [None] * len(races)
    child[cut1:cut2] = parent1[cut1:cut2]

    # Start filling from after segment
    index = cut2

    # For each value after cut 2 in parent 2 and then from start of parent 2
    for value in parent2[cut2:] + parent2[:cut2]:
        if value not in child:
            while None in child:
                # Ensures that the index wraps around if it exceeds the length of child
                if child[index % len(child)] is None:
                    # Assigns value to empty spot
                    child[index % len(child)] = value
                    index += 1
                    break

    return child


# Perform inverse mutation to create diversity and stop early convergence
def mutation(order):
    # Choose two random positions in the order
    pos1 = random.randint(0, len(order) - 1)
    pos2 = random.randint(0, len(order) - 1)

    # Ensure pos2 is greater than pos1
    if pos1 > pos2:
        pos1, pos2 = pos2, pos1

    # Reverse the segment between pos1 and pos2
    order[pos1:pos2 + 1] = reversed(order[pos1:pos2 + 1])

    return order


# Perform roulette wheel selection to get parents for crossover
def get_parents(population):
    # Linear weighting to get bias for selection based on index in list
    weights = [1 / (i + 3) for i in range(len(population))]
    while True:
        # Gets two values based on weighting
        parents = random.choices(population, weights=weights, k=2)
        if parents[0] != parents[1]:
            return parents


def main(mutation_rate):
    generation = 1
    population = []

    # Create first random population
    for _ in range(size):
        x = create_order()
        population.append(x)

    # Repeat for specified number of generations
    for _ in range(num_of_gens):
        # Sort population using their total distances in increasing order
        population = sorted(population, key=cal_distance)

        # Elitism
        # Take best 10% straight through to new gen
        elites = int(size / 10)
        new_generation = population[:elites]

        # Crossover
        # Fill in remaining 90%
        for i in range(size - elites):
            # Get two parents from roulette wheel selection
            parents_for_crossover = get_parents(population)
            # Perform crossover on parents to get child
            child = crossover(parents_for_crossover[0], parents_for_crossover[1])
            # Add to new gen
            new_generation.append(child)

        # Sort new population
        new_generation = sorted(new_generation, key=cal_distance)

        # Mutation
        # Mutate worst 95%
        for i in range(len(new_generation) // 20, len(new_generation)):
            # mutation_rate% chance of performing a mutation
            if random.random() < mutation_rate:
                # Mutate individual
                new_generation[i] = mutation(new_generation[i])

        # Sort new population again
        population = sorted(new_generation, key=cal_distance)
        # Print result for each generation
        print(f"Generation =  {generation} and best distance is {cal_distance(population[0])}km")
        # Increase generation number
        generation += 1
        # Increase mutation rate, so more mutations happen as the algorithm converges more
        mutation_rate += 0.002

    # Print order of races for final solution
    print("Solution is:")
    for i in population[0]:
        print(races[i][2] + ", " + races[i][1])
    print(f"With a total distance of {cal_distance(population[0])} km")
    # Distance travelled in current F1 season
    print(f"Original order of races has distance of {cal_distance(list(range(0, 24)))}km")


main(mutation_rate)
