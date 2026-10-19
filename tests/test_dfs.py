from src.graphs.algorithms import dfs
from src.graphs.graph import Grafo

# — [IA] Claude – casos de teste do DFS.


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