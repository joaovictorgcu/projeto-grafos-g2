from collections import defaultdict
from src.graphs.algorithms import bellman_ford, caminho

# — [IA] Claude – casos de teste do Bellman-Ford.

class Grafo:  # provisório, trocar pelo graph.py do grupo
    def __init__(self):
        self.adj = defaultdict(list)

    def adicionar_arco(self, u, v, peso=1):
        self.adj[u].append((v, peso))
        self.adj[v]

    def arcos(self, u):
        return self.adj[u]

    def nos(self):
        return list(self.adj)


def montar(arcos):
    g = Grafo()
    for a, b, p in arcos:
        g.adicionar_arco(a, b, p)
    return g


def test_peso_negativo_sem_ciclo():
    g = montar([("A", "B", 4), ("A", "C", 5), ("C", "B", -3), ("B", "D", 2)])
    dist, pai, ciclo = bellman_ford(g, "A")
    assert dist == {"A": 0, "B": 2, "C": 5, "D": 4}
    assert caminho(pai, "D") == ["A", "C", "B", "D"]
    assert ciclo is None


def test_inalcancavel_fora_do_dist():
    g = montar([("A", "B", 1), ("C", "D", -1)])
    dist, _, ciclo = bellman_ford(g, "A")
    assert "C" not in dist
    assert ciclo is None


def test_ciclo_negativo_detectado_e_exibido():
    g = montar([("A", "B", 1), ("B", "C", -3), ("C", "B", 1), ("C", "D", 1)])
    _, _, ciclo = bellman_ford(g, "A")
    assert ciclo is not None
    nos, custo = ciclo
    assert nos[0] == nos[-1]
    assert set(nos) == {"B", "C"}
    assert custo == -2


def test_ciclo_negativo_inalcancavel_e_ignorado():
    g = montar([("A", "B", 1), ("X", "Y", -3), ("Y", "X", 1)])
    _, _, ciclo = bellman_ford(g, "A")
    assert ciclo is None