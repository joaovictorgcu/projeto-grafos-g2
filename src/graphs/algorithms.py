import heapq
from collections import deque
from itertools import count

INFINITO = float("inf")
BRANCO, CINZA, PRETO = 0, 1, 2 

def bfs(grafo, origem):
    """Busca em largura. Retorna (dist, pai).

    dist[v] = número de passos (nível) da origem até v.
    pai[v]  = nó de onde v foi descoberto (serve para reconstruir o caminho).
    Nós que não aparecem em dist não são alcançáveis a partir da origem.
    """
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
    """Reconstrói o caminho da origem até o destino, ou None se não for alcançável."""
    if destino not in pai:
        return None

    resultado = []
    atual = destino
    while atual is not None:
        resultado.append(atual)
        atual = pai[atual]

    resultado.reverse()  
    return resultado


def dfs(grafo, origens=None):
    """Busca em profundidade (iterativa). Retorna (tipo, d, f, tem_ciclo).

    tipo[(u, v)] é 'arvore', 'retorno', 'avanco' ou 'cruzamento'.
    d[u] e f[u] são os tempos de descoberta e de término de u.
    tem_ciclo é True se existe algum arco de retorno.

    É iterativa (pilha explícita) porque o grafo de estados pode ser grande
    e a recursão do Python tem limite.
    """
    cor = {}
    d = {}
    f = {}
    tipo = {}
    tempo = 0

    if origens is None:
        origens = grafo.nos()

    for raiz in origens:
        if cor.get(raiz, BRANCO) != BRANCO:
            continue

        tempo += 1
        d[raiz] = tempo
        cor[raiz] = CINZA
        pilha = [[raiz, grafo.vizinhos(raiz), 0]]

        while pilha:
            item = pilha[-1]
            u, vizinhos, i = item

            if i < len(vizinhos):
                item[2] += 1  
                v = vizinhos[i]
                cor_v = cor.get(v, BRANCO)

                if cor_v == BRANCO:  
                    tipo[(u, v)] = "arvore"
                    tempo += 1
                    d[v] = tempo
                    cor[v] = CINZA
                    pilha.append([v, grafo.vizinhos(v), 0])
                elif cor_v == CINZA:  
                    tipo[(u, v)] = "retorno"
                elif d[u] < d[v]: 
                    tipo[(u, v)] = "avanco"
                else: 
                    tipo[(u, v)] = "cruzamento"
            else:  
                pilha.pop()
                tempo += 1
                f[u] = tempo
                cor[u] = PRETO

    tem_ciclo = "retorno" in tipo.values()
    return tipo, d, f, tem_ciclo


def dijkstra(grafo, origem):
    """Menor custo da origem até cada nó. Retorna (dist, pai).

    Lança ValueError se existir algum arco com peso negativo: depois que um nó
    sai do heap, sua distância é considerada definitiva, e isso só vale sem pesos negativos.
    """
    for u in grafo.nos():
        for v, peso in grafo.arcos(u):
            if peso < 0:
                raise ValueError(
                    f"Dijkstra não aceita pesos negativos: arco {u} -> {v} "
                    f"tem peso {peso}. Use Bellman-Ford."
                )

    dist = {origem: 0}
    pai = {origem: None}
    fechados = set()
    desempate = count() 
    heap = [(0, next(desempate), origem)]

    while heap:
        d, _, u = heapq.heappop(heap)
        if u in fechados:  
            continue
        fechados.add(u)

        for v, peso in grafo.arcos(u):
            nova = d + peso
            if v not in dist or nova < dist[v]:
                dist[v] = nova
                pai[v] = u
                heapq.heappush(heap, (nova, next(desempate), v))

    return dist, pai


def peso_do_arco(grafo, a, b):
    """Peso do arco a -> b."""
    for v, peso in grafo.arcos(a):
        if v == b:
            return peso


def bellman_ford(grafo, origem):
    """Menor custo com pesos negativos permitidos. Retorna (dist, pai, ciclo).

    ciclo é None se não há ciclo negativo alcançável a partir da origem.
    Se há, ciclo = (lista_de_nos, custo), com o primeiro nó repetido no fim.
    """
    nos = grafo.nos()
    n = len(nos)
    dist = {origem: 0}
    pai = {origem: None}

    arcos = []
    for u in nos:
        for v, peso in grafo.arcos(u):
            arcos.append((u, v, peso))


    for _ in range(n - 1):
        mudou = False
        for u, v, peso in arcos:
            if u not in dist:  
                continue
            if dist[u] + peso < dist.get(v, INFINITO):
                dist[v] = dist[u] + peso
                pai[v] = u
                mudou = True
        if not mudou:  
            break

    for u, v, peso in arcos:
        if u in dist and dist[u] + peso < dist.get(v, INFINITO):
            pai[v] = u
            return dist, pai, extrair_ciclo(grafo, pai, v, n)

    return dist, pai, None


def extrair_ciclo(grafo, pai, v, n):
    """Acha o ciclo negativo seguindo os pais a partir de v."""
    x = v
    for _ in range(n):
        x = pai[x]

    ciclo = [x]
    atual = pai[x]
    while atual != x:
        ciclo.append(atual)
        atual = pai[atual]
    ciclo.append(x)
    ciclo.reverse()  

    custo = 0
    for a, b in zip(ciclo, ciclo[1:]):
        custo += peso_do_arco(grafo, a, b)
    return ciclo, custo


def estados_armadilha(grafo, alvo="ALVO"):
    """Estados que nunca chegam ao alvo.

    Faz uma BFS a partir do alvo no grafo transposto (arcos invertidos): o que ela
    alcança são os estados que conseguem chegar ao alvo. O resto são armadilhas.
    """
    chegam_ao_alvo, _ = bfs(grafo.transposto(), alvo)
    return [no for no in grafo.nos() if no != alvo and no not in chegam_ao_alvo]