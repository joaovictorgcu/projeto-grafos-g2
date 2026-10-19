from src.graphs.algorithms import bfs, caminho
from src.graphs.graph import Grafo

# — [IA] Claude – casos de teste do BFS conferidos por mim.


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