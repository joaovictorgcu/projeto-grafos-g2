from collections import defaultdict
from src.graphs.algorithms import bfs, caminho

# — [IA] Claude – casos de teste do BFS conferidos por mim.

class Grafo:  # provisório, trocar pelo graph.py do grupo
    def __init__(self):
        self.adj = defaultdict(list)

    def adicionar_arco(self, u, v, peso=1):
        self.adj[u].append((v, peso))
        self.adj[v]

    def vizinhos(self, u):
        return [v for v, _ in self.adj[u]]


def montar():
    g = Grafo()
    for a, b in [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E"), ("F", "A")]:
        g.adicionar_arco(a, b)
    return g


def test_niveis():
    dist, _ = bfs(montar(), "A")
    assert dist == {"A": 0, "B": 1, "C": 1, "D": 2, "E": 3}


def test_caminho_minimo():
    _, pai = bfs(montar(), "A")
    c = caminho(pai, "E")
    assert len(c) - 1 == 3
    assert c[0] == "A" and c[-1] == "E"


def test_inalcancavel():
    dist, pai = bfs(montar(), "A")
    assert "F" not in dist
    assert caminho(pai, "F") is None