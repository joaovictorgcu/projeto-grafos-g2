import heapq
from collections import deque
from itertools import count

# — [IA] Claude – Ajuda na implementação do BFS e da reconstrução de caminho.
def bfs(grafo, origem):
    """Retorna (dist, pai). dist[v] = nível de v (passos desde a origem)."""
    dist = {origem: 0}
    pai = {origem: None}
    fila = deque([origem])
    while fila:
        u = fila.popleft()
        for v in grafo.vizinhos(u):
            if v not in dist:
                dist[v] = dist[u] + 1
                pai[v] = u
                fila.append(v)
    return dist, pai


def caminho(pai, destino):
    """Caminho da origem até destino, ou None se inalcançável."""
    if destino not in pai:
        return None
    c = []
    while destino is not None:
        c.append(destino)
        destino = pai[destino]
    return c[::-1]

# — [IA] Claude – Contribuição no DFS iterativo com classificação de arcos gerado pela IA.
def dfs(grafo, origens=None):
    """Retorna (tipo, d, f, tem_ciclo).
    tipo[(u, v)] in {'arvore', 'retorno', 'avanco', 'cruzamento'}.
    d/f = tempos de descoberta e término.
    """
    cor = {}  # ausente = branco, 1 = cinza, 2 = preto
    d, f, tipo = {}, {}, {}
    tempo = 0
    for raiz in (origens if origens is not None else grafo.nos()):
        if raiz in cor:
            continue
        tempo += 1
        d[raiz] = tempo
        cor[raiz] = 1
        pilha = [(raiz, iter(grafo.vizinhos(raiz)))]
        while pilha:
            u, it = pilha[-1]
            for v in it:
                if v not in cor:
                    tipo[(u, v)] = "arvore"
                    tempo += 1
                    d[v] = tempo
                    cor[v] = 1
                    pilha.append((v, iter(grafo.vizinhos(v))))
                    break
                elif cor[v] == 1:
                    tipo[(u, v)] = "retorno"
                elif d[u] < d[v]:
                    tipo[(u, v)] = "avanco"
                else:
                    tipo[(u, v)] = "cruzamento"
            else:
                pilha.pop()
                tempo += 1
                f[u] = tempo
                cor[u] = 2
    return tipo, d, f, "retorno" in tipo.values()

# — [IA] Claude – Dijkstra com recusa de pesos negativos gerado pela IA; testado por mim.
def dijkstra(grafo, origem):
    """Retorna (dist, pai). Lança ValueError se algum arco tiver peso negativo."""
    for u in grafo.nos():
        for v, peso in grafo.arcos(u):
            if peso < 0:
                raise ValueError(
                    f"Dijkstra não aceita pesos negativos: arco {u} -> {v} "
                    f"tem peso {peso}. Use Bellman-Ford."
                )
    dist = {origem: 0}
    pai = {origem: None}
    cont = count()  # desempate no heap, para nunca comparar nós entre si
    heap = [(0, next(cont), origem)]
    feito = set()
    while heap:
        d, _, u = heapq.heappop(heap)
        if u in feito:
            continue
        feito.add(u)
        for v, peso in grafo.arcos(u):
            nd = d + peso
            if v not in dist or nd < dist[v]:
                dist[v] = nd
                pai[v] = u
                heapq.heappush(heap, (nd, next(cont), v))
    return dist, pai