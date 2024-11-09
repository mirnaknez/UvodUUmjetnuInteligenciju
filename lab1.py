import sys
from collections import deque
from queue import PriorityQueue

def load_transitions(filename): #ucitavanje prijelaza izmedu stanja iz datoteke
    with open(filename, 'r') as file:
        lines = [line.strip() for line in file.readlines() if not line.startswith('#') and line.strip()]
    start = lines[0] #pocetno stanje
    goal = lines[1].split(" ") #lista ciljnih stanja
    transitions = {}
    for line in lines[2:]:
        state, lista = line.split(":")[0], line.split(":")[1].strip()
        transitions[state] = [(part.split(',')[0], int(part.split(',')[1])) for part in lista.split()] #prijelazi kao tuple (sljedece_stanje, trosak)
    return start, goal, transitions

def load_heuristics(filename): #ucitavanje heuristickih vrijednosti iz datoteke
    heuristics = {}
    with open(filename, 'r') as file:
        for line in file:
            parts = line.split(":")
            heuristics[parts[0].strip()] = int(parts[1].strip())
    return heuristics

def short_path(came_from, start, goal): #konstrukcija putanje od pocetnog do ciljnog stanja
    current, path = goal, []
    while current != start: #od cilja prema startu
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse() #obrnuti redoslijed
    return path

def print_output(alg, path, visited, filename, total_cost=None): #ispis rezultata algoritama
    if alg == "A*":
        print(f"# A-STAR {filename}")
    else:
        print(f"# {alg}")
    print("[FOUND_SOLUTION]: yes")
    print("[STATES_VISITED]:", len(visited))
    print("[PATH_LENGTH]:", len(path))
    if total_cost is not None:
        print("[TOTAL_COST]:", total_cost)
    print("[PATH]:", " => ".join(path))

def bfs(filename): #algoritam pretrage u sirinu
    start, goal, transitions = load_transitions(filename) #pocetno stanje, ciljevi i prijelazi iz datoteke
    deq = deque([(start, 0)]) #stog s pocetnim stanjem i pocetnim troskom 0
    came_from = {start: None} #putanje do stanja
    cost = {start: 0} #trosak do stanja
    visited = set([start]) #skup posjecenih stanja

    while deq:
        current, current_cost = deq.popleft() #prvi element sa stoga

        if current in goal: #trenutno stanje je ciljno stanja
            path = short_path(came_from, start, current) #putanja
            print_output("BFS", path, visited, filename, current_cost) #ispis rezultata
            return #gotova funkcija

        for next, next_cost in transitions[current]: #svi moguci prijelazi iz stanja
            new_cost = current_cost + next_cost #novi trosak
            if next not in visited or new_cost < cost.get(next, float('inf')): #sljedece stanje nije posjeceno ili pronaden jeftiniji put
                deq.append((next, new_cost)) #dodajemo stanje na stog
                came_from[next] = current #pamtimo prethodno stanje
                cost[next] = new_cost #azuriranje troska
                visited.add(next)  #sljedece stanje dodajemo u posjeceno

    print("# BFS\n[FOUND_SOLUTION]: no") #ako algoritam nije pronasao putanju

def ucs(filename): #algoritam uniformne troskovne pretrage
    start, goal, transitions = load_transitions(filename) #pocetno stanje, ciljevi i prijelazi iz datoteke
    pq, came_from, cost, visited = PriorityQueue(), {start: None}, {start: 0.0}, set()  #prioritetni red, putanje do stanja, trosak, posjecena stanja
    pq.put((0.0, start))  #pocetno stanje s troskom 0
    while not pq.empty(): #dok prioritetni red nije prazan
        current_cost, current = pq.get() 
        if current in goal: #ako je trenutno stanje ciljno
            print_output("UCS", short_path(came_from, start, current), visited, filename, f"{cost[current]:.1f}") #ispis rezultata algoritma
            return #kraj funkcije
        visited.add(current) #trenutno stanje kao posjeceno
        for next, next_cost in transitions[current]: #za svaki prijelaz iz stanja
            new_cost = current_cost + float(next_cost)  #novi trosak
            if next not in cost or new_cost < cost[next]: #ako nije odabrano sljedece stanje ili postoji jeftiniji put
                pq.put((new_cost, next)) #novo stanje u prioritetni red
                came_from[next] = current #pamti prethodno stanje
                cost[next] = new_cost #azurira trosak
    print("# UCS\n[FOUND_SOLUTION]: no") #ako putanja nije pronadena


def astar(filename, heuristic_file): #A* algoritam pretrage
    start, goal, transitions = load_transitions(filename) #pocetno stanje, ciljevi i prijelazi iz datoteke
    heuristics = load_heuristics(heuristic_file) #heuristicke vrijednosti za svako stanje iz datoteke
    pq, came_from, cost, visited = PriorityQueue(), {start: None}, {start: 0.0}, set()  #prioritetni red, putanje do stanja, trosak, posjecena stanja
    pq.put((heuristics[start], start, 0.0)) #pocetno stanje u prioritetni red 

    while not pq.empty(): #prioritetni red nije prazan
        _, current, current_cost = pq.get() #stanje iz prioritetnog reda

        if current in goal: #trenutno je ciljno stanje
            print_output("A*", short_path(came_from, start, current), visited, heuristic_file, f"{cost[current]:.1f}") #ispis rezultata algoritma
            return #povratak iz funkcije

        visited.add(current) #trenutno stanje posjeceno
        for next, next_cost in transitions[current]: #za svaki prijelaz iz trenutnog stanja
            new_cost = current_cost + float(next_cost)  #novi trosak
            if next not in cost or new_cost < cost[next]: #sljedece stanje nije obradeno ili pronaden jeftiniji put
                total_cost = new_cost + heuristics[next] #ukupni trosak
                pq.put((total_cost, next, new_cost))  #dodavanje novog stanja u prioritetni red
                came_from[next] = current #pamti prethodno stanje
                cost[next] = new_cost #azurira trosak

    print("# A-STAR\n[FOUND_SOLUTION]: no") #ako putanja nije pronadena

def calculate_cost(state, goal,transitions): #trosak stanja do cilja koristeci UCS algoritam
    pq, came_from, cost, visited = PriorityQueue(), {state: None}, {state: 0.0}, set()   #prioritetni red, putanje do stanja, trosak, posjecena stanja
    pq.put((0.0, state))  #pocetno stanje u prioritetni red
    while not pq.empty(): #dok prioritetni red nije prazan
        current_cost, current = pq.get() #stanje s najmanjim troskom
        if current in goal: #trenutno stanje je ciljno
            return current_cost #vraca trosak
        visited.add(current) #trenutno stanje kao posjeceno
        for next, next_cost in transitions[current]: #prijelazi iz trenutnog stanja
            new_cost = current_cost + float(next_cost)  #novi trosak do sljedeceg stanja
            if next not in cost or new_cost < cost[next]: #sljedece stanje nije posjeceno ili ima jeftiniji put
                pq.put((new_cost, next)) #sljedece stanje u prioritetni red
                came_from[next] = current #dodavanje prethodnog stanja
                cost[next] = new_cost #azurira trosak do stanja


def check_optimistic(filename, heuristic_file): #provjera optimisticnosti za sva stanja
    heuristics = load_heuristics(heuristic_file) #heuristicke vrijednosti iz datoteke
    start, goal, transitions = load_transitions(filename) #pocetno stanje, ciljevi i prijelazi
    opt = True #optimisticna je
    print(f"# HEURISTIC-OPTIMISTIC {heuristic_file}")
    for state, heuristic_value in heuristics.items(): #za svako stanje i heuristicku vrijednost
        cost = calculate_cost(state, goal,transitions) #izracunava trosak
        if heuristic_value <= cost: #heuristicka vrijednost manja ili jednaka stvarnom trosku
            print(f"[CONDITION]: [OK] h({state}) <= h*: {heuristic_value:.1f} <= {cost:.1f}")
        else:
            print(f"[CONDITION]: [ERR] h({state}) <= h*: {heuristic_value:.1f} <= {cost:.1f}")
            opt = False #nije optimisticna
    if opt: #je li optimisticna
        print("[CONCLUSION]: Heuristic is optimistic.")
    else:
        print("[CONCLUSION]: Heuristic is not optimistic.")


def check_consistent(filename, heuristic_file): #provjera konzistentnosti za sva stanja
    start, goal, transitions = load_transitions(filename) #pocetno stanje, ciljevi i prijelazi
    heuristics = load_heuristics(heuristic_file) #heuristicke vrijednosti iz datoteke
    print("# HEURISTIC-CONSISTENT {heuristic_file}")
    cons = True #je konzistentna
    for state, edges in transitions.items(): #sva stanja i prijelazi
        for next_state, cost in edges:
            if heuristics[state] > heuristics[next_state] + cost: #provjera konzistentnosti
                print(f"[CONDITION]: [ERR] h({state}) <= h({next_state}) + c: {heuristics[state]:.1f} <= {heuristics[next_state]:.1f} + {cost:.1f}")
                cons = False #nije konzistentna
            else:
                print(f"[CONDITION]: [OK] h({state}) <= h({next_state}) + c: {heuristics[state]:.1f} <= {heuristics[next_state]:.1f} + {cost:.1f}")

    if cons: # je li konzistentna
        print("[CONCLUSION]: Heuristic is consistent.")
    else:
        print("[CONCLUSION]: Heuristic is not consistent.")

filename = ""
heuristic_file = ""

if "--ss" in sys.argv:
    ss_index = sys.argv.index("--ss") + 1
    filename = sys.argv[ss_index]

if "--h" in sys.argv:
    h_index = sys.argv.index("--h") + 1
    heuristic_file = sys.argv[h_index]

if "--alg" in sys.argv:
    alg_index = sys.argv.index("--alg") + 1
    alg = sys.argv[alg_index]
    if alg == "bfs":
        bfs(filename)
    elif alg == "ucs":
        ucs(filename)
    elif alg == "astar":
        astar(filename, heuristic_file)
    
if "--check-optimistic" in sys.argv:
    check_optimistic(filename, heuristic_file)

if "--check-consistent" in sys.argv:
    check_consistent(filename, heuristic_file)
