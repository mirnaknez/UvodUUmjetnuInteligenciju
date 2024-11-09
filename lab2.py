import sys
import re
from collections import deque

def load_resolution(filename): #učitavanje podataka
    with open(filename, 'r') as file:
        lines = [line.strip() for line in file.readlines() if not line.startswith('#') and line.strip()]
    return lines

def negate(literal): #negiranje literala
    literal = literal.strip()
    return literal[1:] if literal.startswith('~') else '~' + literal

def resolve(clause1, clause2, neg):
    #radimo uniju dvije klauzule, te potom mičemo komplementarne literale
    new_clause = set()
    for literal in clause1:
        new_clause.add(literal)
    for literal in clause2:
        new_clause.add(literal)

    for literal in neg:
        new_clause.remove(literal)
        new_clause.remove(negate(literal))

    if not new_clause:
        return "NIL"
    
    return frozenset(new_clause)

def print_traceback(dictall, counter1, camefrom):
    #printanje prvotnog zadanog skupa klauzula
    for i, key in enumerate(dictall.keys(), 1):
        if i < counter1:
            print_key = ' v '.join(key).lower()
            print(f'{dictall[key]}. {print_key}')
        else:
            break
    print("===============")
    
    steps = [] 
    parents = ["NIL"]
    #pronalazak roditelja svake novonastale klauzule dok nismo došli do NIL
    for current in parents:
        if current in camefrom:
            new_parent1, new_parent2 = camefrom[current]
            if new_parent1 not in parents:
                parents.append(new_parent1)
            if new_parent2 not in parents:
                parents.append(new_parent2)
            
            k = dictall.get(current, "Unknown")
            k1 = dictall.get(new_parent1, "Unknown")
            k2 = dictall.get(new_parent2, "Unknown")
            
            step = ' v '.join(current).lower() if isinstance(current, frozenset) else current
            steps.append(f'{k}. {step} ({k1}, {k2})')
    #printanje trace-a do rješenja
    while steps:
        print(steps.pop())
    print("===============")


def resolution(file1):
    lines = load_resolution(file1)
    original_target = lines[-1] #originalna finalna klauzula
    clauses = set()
    dictall = dict()
    camefrom = dict()
    counter = 1
    #dodavanje klauzula u obliku skupa u skup svih klauzula
    for line in lines[:-1]:
        clause = frozenset([literal.strip() for literal in re.split(' V | v ', line)])
        clauses.add(clause)
        dictall[clause] = counter
        counter += 1
    remove = set()
    for clause in clauses:
        for literal in clause:
            if negate(literal) in clause:
                remove.add(clause)
                break
    clauses.difference_update(remove)
    #kreiranje setofsupport iz finalne klauzule koju dokazujemo
    setofsupport = set()
    for lit in re.split(' V | v ', original_target):
        setofsupport.add(frozenset([negate(lit).strip()]))
    for clause in setofsupport:
        dictall[clause] = counter
        counter += 1
    counter1 = counter
    #proces nalaženja komplementarnih literala klauzulama te njihovo rješavanje
    while True:
        for clause in setofsupport:
            for literal in clause:
                if negate(literal) in clause:
                    remove.add(clause)
                    break
        setofsupport.difference_update(remove)
        new_clauses = set()
        for clause1 in setofsupport:
            for clause2 in clauses.union(setofsupport):
                if clause1 != clause2:
                    neg = set()
                    for literal in clause1:
                        if negate(literal) in clause2:
                            neg.add(literal)
                    if neg:
                        new_clause = resolve(clause1, clause2, neg)
                        if new_clause == "NIL":
                            camefrom["NIL"] = (clause1, clause2)
                            dictall["NIL"] = counter
                            counter += 1
                            print_traceback(dictall, counter1, camefrom)
                            print(f"[CONCLUSION]: {original_target} is true") #pronalazak NIL-a i ispis točnosti klauzule
                            return True
                        camefrom[new_clause] = (clause1, clause2)
                        if new_clause not in dictall.keys():
                            dictall[new_clause] = counter
                            counter += 1
                        new_clauses.add(frozenset(new_clause))
        if new_clauses.issubset(clauses.union(setofsupport)):
            print(f"[CONCLUSION]: {original_target} is unknown") #ispis da klauzula nije pronađena
            return False
        else:
            setofsupport.update(new_clauses)
    
def cooking(file1, file2):
    lines1 = load_resolution(file1) #učitavanje podataka
    clauses = set()
    for line in lines1:
        clause = frozenset([literal.strip() for literal in re.split(' V | v ', line)])
        clauses.add(clause)
    remove = set()
    for clause in clauses: #nastanak skupa klauzula
        for literal in clause:
            if negate(literal) in clause:
                remove.add(clause)
                break
    clauses.difference_update(remove)
    with open(file2, 'r') as file:
        lines2 = [line.strip() for line in file.readlines() if not line.startswith('#') and line.strip()] #učitavanje drugog file-a
    for line in lines2:
        line = line.strip()
        if line[-1] == "?": #traženje rezolucije za zadani target
            original_target = line[:-1].strip() 
            target = negate(original_target)  
            clauses.add(frozenset({target})) 
            while True:
                new_clauses = set()
                for clause1 in clauses:
                    for clause2 in clauses:
                        if clause1 != clause2:
                            neg = set()
                            for literal in clause1:
                                if negate(literal) in clause2:
                                    neg.add(literal)
                            if neg:
                                new_clause = resolve(clause1, clause2, neg)
                                if new_clause == "NIL":
                                    print(f"[CONCLUSION]: {original_target} is true")
                                    return True
                                new_clauses.add(frozenset(new_clause))
                if new_clauses.issubset(clauses):
                    print(f"[CONCLUSION]: {original_target} is unknown")
                    return False
                else:
                    clauses.update(new_clauses)
        elif line[-1] == "+": #dodavanje klauzule u skup klauzula
            clauses.add(frozenset([literal.strip() for literal in re.split(' V | v ', line[:-1].strip())]))
        elif line[-1] == "-": #brisanje klauzule iz skupa klauzula
            clauses.difference_update(frozenset([literal.strip() for literal in re.split(' V | v ', line[:-1].strip())]))

if "resolution" in sys.argv:
    ind = sys.argv.index("resolution") + 1
    file1 = sys.argv[ind]
    resolution(file1)
if "cooking" in sys.argv:
    ind = sys.argv.index("cooking") + 1
    file1 = sys.argv[ind]
    file2 = sys.argv[ind + 1]
    cooking(file1, file2)
