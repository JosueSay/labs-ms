import random
from typing import List
from io_tsp import getDistance

def makeRandomTour(n: int) -> List[int]:
    """ Crea permutación aleatoria vaida π∈S_n"""
    tour = list(range(n))
    random.shuffle(tour)
    return tour

def nearestInsertionSeed(n: int, vec: List[int]) -> List[int]:
    """Constr un tur con el aglortimo de incs. + cercano"""
    if n == 0:
        return []
    
    #S0 = Ciudad aleaotira
    start = random.randint(0, n - 1)
    tour = [start]
    unvisited = set(range(n)) - {start}
    
    #Ciudad e inceserion + cerca na al inicio
    if unvisited:
        nearest = min(unvisited, key=lambda city: getDistance(start, city, n, vec))
        tour.append(nearest)
        unvisited.remove(nearest)
    
    while unvisited:
        best_city = None
        best_position = -1
        best_cost_increase = float('inf')
        
        for city in unvisited:
            for pos in range(len(tour)):
                prev_city = tour[pos - 1]
                next_city = tour[pos]
                
                current_cost = getDistance(prev_city, next_city, n, vec)
                new_cost = (getDistance(prev_city, city, n, vec) + 
                           getDistance(city, next_city, n, vec))
                
                cost_increase = new_cost - current_cost
                
                if cost_increase < best_cost_increase:
                    best_cost_increase = cost_increase
                    best_city = city
                    best_position = pos
        
        tour.insert(best_position, best_city)
        unvisited.remove(best_city)
    
    return tour
    
def initPopulation(n: int, vec: List[int], N: int, seedFrac: float=0.25) -> List[List[int]]:
    """iniciar poablacion"""
    population = []
    
    #Tours aleatorios
    num_random = int(N * (1.0 - seedFrac))
    for _ in range(num_random):
        population.append(makeRandomTour(n))
    
    #Tours algorit. constructivos
    num_seeds = N - num_random
    for _ in range(num_seeds):
        #incersion cerca
        tour = nearestInsertionSeed(n, vec)
        population.append(tour)
    
    for i, tour in enumerate(population):
        if not validar_permutacion(tour, n):
            population[i] = makeRandomTour(n)
    
    return population

def validar_permutacion(permutacion: List[int], n: int) -> bool:
    """Permutación válida de n elementos"""
    if len(permutacion) != n:
        return False
    
    seen = set()
    for city in permutacion:
        if city < 0 or city >= n or city in seen:
            return False
        seen.add(city)
    
    return len(seen) == n
