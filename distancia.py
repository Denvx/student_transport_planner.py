import math

def distancia(p1, p2):
    # Calcula a distância euclidiana entre dois pontos (p1 e p2)
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)