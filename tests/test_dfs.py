from collections import defaultdict
from src.graphs.algorithms import dfs


class Grafo:  # provisório, trocar pelo graph.py do grupo
    def __init__(self):
        self.adj = defaultdict(list)

    def adicionar_arco(self, u, v, peso=1):
        self.adj[u].append((v, peso))
        self.adj[v]

    def vizinhos(self, u):
        return [v for v, _ in self.adj[u]]

    def nos(self):
        return list(self.adj)


def montar(arcos):
    g = Grafo()
    for a, b in arcos:
        g.adicionar_arco(a, b)
    return g


def test_quatro_classificacoes():
    g = montar([("A", "B"), ("B", "C"), ("C", "A"), ("A", "C"), ("A", "D"), ("D", "C")])
    tipo, _, _, ciclo = dfs(g)
    assert tipo[("A", "B")] == "arvore"
    assert tipo[("B", "C")] == "arvore"
    assert tipo[("A", "D")] == "arvore"
    assert tipo[("C", "A")] == "retorno"
    assert tipo[("A", "C")] == "avanco"
    assert tipo[("D", "C")] == "cruzamento"
    assert ciclo is True


def test_sem_ciclo():
    g = montar([("A", "B"), ("B", "C"), ("A", "C")])
    _, _, _, ciclo = dfs(g)
    assert ciclo is False