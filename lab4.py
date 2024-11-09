import numpy as np 
import random  
import sys 

class Population:
    def __init__(self, input_len, nn):
        self.layers = [input_len] + nn + [1]  # slojevi neuronske mreže
        # težine - normalna distribucija
        self.weights = []
        for i in range(len(self.layers) - 1):
            self.weights.append(np.random.normal(0, 0.01, size=(self.layers[i+1], self.layers[i])))
        # pristranosti - normalna distribucija
        self.biases = []
        for i in range(len(self.layers) - 1):
            self.biases.append(np.random.normal(0, 0.01, size=(self.layers[i+1])))
        self.diff_squared = float('inf')  # početna kvadratna razlika - beskonačnost

def read_from_file(path):
    with open(path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    data = []
    for line in lines:
        if line.strip():
            data.append(line.strip().split(','))
    return data

def sigmoid(x):
    return 1 / (1 + np.exp(-x))  # sigmoidna funkcija

def forward(x, weights, biases):
    for w, b in zip(weights[:-1], biases[:-1]):  # kroz sve slojeve osim izlaznog
        x = sigmoid(np.dot(w, x) + b)  # izlaz trenutnog sloja
    return np.dot(weights[-1], x) + biases[-1]  # izlaz mreže

def propagate(data, populations):
    for pop in populations:  # kroz svaku populaciju
        dif_squared = 0  # kvadratna razlika na nulu
        for row in data:  # kroz svaki red u podacima
            x = np.array(row[:-1], dtype=np.float64)  # ulazni podatci
            y = float(row[-1])  # ciljna vrijednost
            prediction = forward(x, pop.weights, pop.biases)  # predikcija mreže
            dif_squared += (y - prediction) ** 2  # kvadratna razlika
        pop.diff_squared = dif_squared / len(data)  # srednja kvadratna razlika


def create_matrix(file_name):
    lines = read_from_file(file_name)[1:]  # bez zaglavlja
    matrix = []
    for line in lines:
        matrix.append(list(map(float, line)))
    return matrix  

def train(train_data, test_data, nn, popsize, elitism, p, k, iterations):
    input_len = len(train_data[0]) - 1  
    populations = []  # inicijalizacija populacije
    for _ in range(popsize):
        populations.append(Population(input_len, nn))

    for iteration in range(iterations):  # kroz broj iteracija
        propagate(train_data, populations)  # Propagacija - trening podatci
        sorted_population = sorted(populations, key=lambda x: x.diff_squared)  # sortiranje populacije po kvadratnoj razlici
        next_generation = sorted_population[:elitism]  # najbolji

        if iteration % 2000 == 1999:  # greška svakih 2000 iteracija
            print(f"[Train error @{iteration+1}]: {float(next_generation[0].diff_squared)}")

        while len(next_generation) < popsize:  # nova populacija
            parent1 = random.sample(sorted_population, 1)[0]
            parent2 = random.sample(sorted_population + next_generation, 1)[0]
            child_weights = []
            for w1, w2 in zip(parent1.weights, parent2.weights):
                child_weights.append((w1 + w2) / 2)
            child_biases = []
            for b1, b2 in zip(parent1.biases, parent2.biases):
                child_biases.append((b1 + b2) / 2)
            child = Population(input_len, nn)
            child.weights= child_weights
            child.biases = child_biases
            next_generation.append(child)

        for individual in next_generation:  # mutacija jedinki
            for i in range(len(individual.weights)):
                if random.random() < p:
                    individual.weights[i] += np.random.normal(0, k, size=individual.weights[i].shape)
                    individual.biases[i] += np.random.normal(0, k, size=individual.biases[i].shape)

        populations = next_generation  # nova generacija kao trenutna

    best_individual = min(populations, key=lambda x: x.diff_squared)  # najbolja jedinka
    propagate(test_data, [best_individual])  # propagacija - testni podatci
    print(f"[Test error]: {float(best_individual.diff_squared)}")  # greška

args = sys.argv

train_file = args[args.index("--train") + 1]
test_file = args[args.index("--test") + 1]
nn_layers = args[args.index("--nn") + 1]
popsize = int(args[args.index("--popsize") + 1])
elitism = int(args[args.index("--elitism") + 1])
p = float(args[args.index("--p") + 1])
k = float(args[args.index("--K") + 1])
iterations = int(args[args.index("--iter") + 1])

if nn_layers == "5s":
    nn = [5]
elif nn_layers == "20s":
    nn = [20]
elif nn_layers == "5s5s":
    nn = [5, 5]

train_data = create_matrix(train_file)
test_data = create_matrix(test_file)

train(train_data, test_data, nn, popsize, elitism, p, k, iterations)
