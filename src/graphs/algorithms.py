from collections import deque

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