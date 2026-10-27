"""networkx usado só aqui, como oráculo, para conferir os algoritmos próprios."""
# — [IA] Claude – testes de oráculo com networkx gerados pela IA; executados e integrados por mim
import random

import networkx as nx
import pytest

from src.graphs.algorithms import bellman_ford, bfs, dfs, dijkstra
from src.graphs.graph import Grafo

SEMENTES = range(200)


def gerar(semente, peso_min, peso_max, dag=False):
    """Mesmo grafo aleatório nas duas implementações (sem arcos paralelos)."""
    rnd = random.Random(semente)
    n = rnd.randint(2, 9)
    g, ref = Grafo(), nx.DiGraph()
    for i in range(n):
        g.adicionar_no(i)
        ref.add_node(i)
    for _ in range(rnd.randint(1, 20)):
        u, v = rnd.sample(range(n), 2)
        if dag and u > v:
            u, v = v, u
        if ref.has_edge(u, v):
            continue
        p = rnd.randint(peso_min, peso_max)
        g.adicionar_arco(u, v, p)
        ref.add_edge(u, v, weight=p)
    return g, ref


@pytest.mark.parametrize("semente", SEMENTES)
def test_bfs_niveis_iguais_ao_networkx(semente):
    g, ref = gerar(semente, 1, 1)
    dist, _ = bfs(g, 0)
    assert dist == dict(nx.single_source_shortest_path_length(ref, 0))


@pytest.mark.parametrize("semente", SEMENTES)
def test_dfs_ciclo_igual_ao_networkx(semente):
    g, ref = gerar(semente, 1, 1)
    _, _, _, tem_ciclo = dfs(g)
    assert tem_ciclo == (not nx.is_directed_acyclic_graph(ref))


@pytest.mark.parametrize("semente", SEMENTES)
def test_dijkstra_distancias_iguais_ao_networkx(semente):
    g, ref = gerar(semente, 0, 9)
    dist, _ = dijkstra(g, 0)
    assert dist == dict(nx.single_source_dijkstra_path_length(ref, 0))


@pytest.mark.parametrize("semente", SEMENTES)
def test_bellman_ford_peso_negativo_sem_ciclo(semente):
    g, ref = gerar(semente, -5, 9, dag=True)  # DAG: nunca tem ciclo
    dist, _, ciclo = bellman_ford(g, 0)
    assert ciclo is None
    assert dist == dict(nx.single_source_bellman_ford_path_length(ref, 0))


@pytest.mark.parametrize("semente", SEMENTES)
def test_bellman_ford_flag_de_ciclo_igual_ao_networkx(semente):
    g, ref = gerar(semente, -4, 6)
    dist, _, ciclo = bellman_ford(g, 0)
    try:
        esperado = nx.single_source_bellman_ford_path_length(ref, 0)
    except nx.NetworkXUnbounded:  # ciclo negativo alcançável a partir da origem
        assert ciclo is not None
        nos, custo = ciclo
        assert nos[0] == nos[-1] and custo < 0
        assert custo == sum(ref[a][b]["weight"] for a, b in zip(nos, nos[1:]))
    else:
        assert ciclo is None
        assert dist == dict(esperado)