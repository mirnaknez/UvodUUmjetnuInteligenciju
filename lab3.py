import sys
import math

# globalne varijable za ispis informacijske dobiti i grana stabla
ig_print = ""
branches_print = ""

def read_data(filepath):
    with open(filepath, 'r') as file: # učitava podatke iz CSV datoteke
        header = file.readline().strip().split(',') # učitava zaglavlje
        data = [line.strip().split(',') for line in file.readlines()] # učitava sve redke datoteke
    return header, data

def entropy(data, target_index):
    # broji pojavljivanja svake vrijednosti ciljne varijable
    label_count = {}
    for row in data:
        label = row[target_index]
        if label not in label_count:
            label_count[label] = 0
        label_count[label] += 1
    # izračun entropije
    ent = 0.0
    total = len(data)
    for label in label_count:
        probability = label_count[label] / total
        ent -= probability * math.log2(probability)
    return ent

def information_gain(data, split_index, target_index):
    # izračun entropije za cijeli skup podataka
    total_entropy = entropy(data, target_index)
    subset_entropy = 0.0

    # grupacija podataka prema vrijednostima odabrane značajke
    value_counts = {}
    for row in data:
        key = row[split_index]
        if key not in value_counts:
            value_counts[key] = []
        value_counts[key].append(row)

    # izračun uvjetne entropije za podskupove podataka
    for key in value_counts:
        subset_prob = len(value_counts[key]) / float(len(data))
        subset_entropy += subset_prob * entropy(value_counts[key], target_index)

    return total_entropy - subset_entropy

def best_feature_to_split(data, header, target_index):
    global ig_print
    num_features = len(data[0])  # broj značajki
    best_gain = 0  # najbolja informacijska dobit
    best_feature = -1  # indeks najbolje značajke
    gains = []  # lista informacijskih dobiti za sve značajke

    # prolazi kroz sve značajke, računa informacijsku dobit za svaku
    for feature in range(num_features):
        if feature != target_index:  # zanemaruje ciljnu varijablu
            gain = information_gain(data, feature, target_index)
            gains.append((header[feature], gain))  
            if gain > best_gain:  # nova najbolja informacijska dobit i značajka
                best_gain = gain
                best_feature = feature

    gains.sort(key=lambda x: (-x[1], x[0]))  # sortira prema informacijskoj dobiti (silazno), zatim abecedno
    # ispis za informacijsku dobit
    for name, gain in gains:
        ig_print += f"IG({name})={gain:.4f} "
    
    return best_feature  # indeks značajke s najboljom informacijskom dobiti

def build_tree(data, header, target_index, depth=None, level=1, branch=""):
    global branches_print
    # provjera jesu li sve ciljne varijable iste
    if len(set(row[target_index] for row in data)) == 1:
        return data[0][target_index]

    # provjera je li dostignuta maksimalna dubina
    if depth is not None and depth == 0:
        return majority_vote(data, target_index)

    # provjera je li ostala samo jedna značajka
    if len(data[0]) == 1:
        return majority_vote(data, target_index)

    # najbolja značajka za grananje
    best_feature = best_feature_to_split(data, header, target_index)
    if best_feature == -1:
        return majority_vote(data, target_index)

    tree = {}
    feature_values = set(row[best_feature] for row in data)
    tree[header[best_feature]] = {}

    # nova podstabla za svaku vrijednost najbolje značajke
    for value in feature_values:
        subset = [row[:best_feature] + row[best_feature+1:] for row in data if row[best_feature] == value]
        subtree_header = header[:best_feature] + header[best_feature+1:]
        subtree = build_tree(subset, subtree_header, target_index if best_feature > target_index else target_index - 1, depth - 1 if depth is not None else None, level + 1, f"{branch}{level}:{header[best_feature]}={value} ")
        tree[header[best_feature]][value] = subtree
        # grana u ispis ako je podstablo list
        if isinstance(subtree, str):
            branches_print += f"{branch}{level}:{header[best_feature]}={value} {subtree}\n"

    return tree

def majority_vote(data, target_index):
    # broji pojavljivanja svake vrijednosti ciljne varijable
    counts = {}
    for row in data:
        label = row[target_index]
        if label not in counts:
            counts[label] = 0
        counts[label] += 1

    # sortira prema broju pojavljivanja (silazno) i abecedno
    items = list(counts.items())
    items.sort(key=lambda x: x[0])  # sortira abecedno
    items.sort(key=lambda x: x[1], reverse=True)  # sortira prema broju pojavljivanja (silazno)
    
    # vraća vrijednost s najviše pojavljivanja
    return items[0][0]

def predict(tree, sample, header, train_data, target_index):
    # provjerava je li čvor list
    if isinstance(tree, str):
        return tree
    
    # prolaz kroz značajke u stablu
    for feature, branches in tree.items():
        feature_index = header.index(feature)  # indeks značajke
        feature_value = sample[feature_index]  # vrijednost značajke iz uzorka

        # provjera postoji li grana za ovu vrijednost značajke
        if feature_value in branches:
            # rekurzivno predviđanje koristeći podstablo
            return predict(branches[feature_value], sample, header, train_data, target_index)
    
    # ako vrijednost nije pronađena u granama, vraća najčešću vrijednost ciljne varijable
    return majority_vote(train_data, target_index)

def evaluate_accuracy(data, tree, header, train_data, target_index):
    # broji točne predikcije
    correct = 0
    predictions = []
    
    # za svaki uzorak u skupu podataka
    for sample in data:
        # predviđanje vrijednosti ciljne varijable za uzorak
        predicted = predict(tree, sample, header, train_data, target_index)
        # dodaje predikciju u listu predikcija
        predictions.append(predicted)
        # provjerava je li predikcija točna
        if predicted == sample[-1]:
            correct += 1
    
    # izračunava točnost kao omjer točnih predikcija i ukupnog broja uzoraka
    accuracy = correct / len(data)
    return predictions, accuracy

def confusion_matrix(data, predictions, header):
    # stvarne vrijednosti ciljne varijable iz podataka
    actual = [row[-1] for row in data]
    # jedinstvene vrijednosti ciljne varijable, sortirane
    unique_labels = sorted(set(actual))
    # inicijalizira matricu zabune s nulama
    matrix = {label: {l: 0 for l in unique_labels} for label in unique_labels}

    # popunjava matricu zabune na temelju stvarnih i predviđenih vrijednosti
    for true, pred in zip(actual, predictions):
        matrix[true][pred] += 1

    return matrix

def print_confusion_matrix(matrix):
    # jedinstvene i sortirane oznake ciljne varijable
    labels = sorted(matrix.keys())
    # ispisuje zaglavlje za matricu zabune
    print("[CONFUSION_MATRIX]:")
    # ispisuje redove matrice zabune
    for label in labels:
        # ispisuje brojeve iz matrice zabune za određenu oznaku
        print(" ".join(str(matrix[label][l]) for l in labels))

def ID3(file1, file2, depth=None):
    global ig_print, branches_print

    # učitava podatke iz datoteka za treniranje i testiranje
    header1, data1 = read_data(file1)
    header2, data2 = read_data(file2)

    # gradi stablo odluke koristeći skup podataka za treniranje
    tree = build_tree(data1, header1, len(header1) - 1, depth)
    
    # ispisuje informacije o informacijskoj dobiti i granama stabla
    print(ig_print.strip())
    print("[BRANCHES]:")
    print(branches_print.strip())

    # evaluira točnost modela na skupu podataka za testiranje
    predictions, accuracy = evaluate_accuracy(data2, tree, header2, data1, len(header1) - 1)
    print("[PREDICTIONS]:", " ".join(predictions))
    print("[ACCURACY]:", f"{accuracy:.5f}")

    # generira i ispisuje matricu zabune
    matrix = confusion_matrix(data2, predictions, header2)
    print_confusion_matrix(matrix)

try:
    file1 = sys.argv[1]  # putanja do datoteke skupa podataka za treniranje
    file2 = sys.argv[2]  # putanja do datoteke skupa podataka za testiranje
    depth = int(sys.argv[3]) if len(sys.argv) > 3 else None  # dubina stabla (opcionalno)
except IndexError:
    sys.exit(1)  # izlazi ako argumenti nisu ispravno dani

# pokreće ID3 algoritam s danim argumentima
ID3(file1, file2, depth)
