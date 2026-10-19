import pytest
from src.graphs.algorithms import dijkstra, caminho
from src.graphs.graph import Grafo

# — [IA] Claude – casos de teste do Dijkstra.


def montar(arcos):
    g = Grafo()
    for a, b, p in arcos:
        g.adicionar_arco(a, b, p)
    return g


def test_caminhos_corretos():
    g = montar([("A", "B", 1), ("A", "C", 4), ("B", "C", 2), ("C", "D", 1), ("B", "D", 5)])
    dist, pai = dijkstra(g, "A")
    assert dist == {"A": 0, "B": 1, "C": 3, "D": 4}
    assert caminho(pai, "D") == ["A", "B", "C", "D"]


def test_inalcancavel():
    g = montar([("A", "B", 1), ("C", "D", 1)])
    dist, _ = dijkstra(g, "A")
    assert "C" not in dist


def test_recusa_peso_negativo():
    g = montar([("A", "B", 1), ("B", "C", -3)])
    with pytest.raises(ValueError, match="negativos"):
        dijkstra(g, "A")