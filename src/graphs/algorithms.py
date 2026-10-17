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