# [IA] Claude Code (Claude Opus 5.5) – testes do grafo interativo da Visão geral da Parte 2 (precisam do snapshot em data/dataset_parte2)
import pytest

from src.rotas_parte2 import PASTA, GrafoDaParte2, PedidoInvalido

pytestmark = pytest.mark.skipif(not (PASTA / "transfers.csv.gz").exists() and not (PASTA / "transfers.csv").exists(),
                                reason="snapshot do Transfermarkt não baixado (python scripts/ficha_transfermarkt.py --baixar)")

SANTOS, PSG, BENFICA, BOURNEMOUTH = 221, 583, 294, 989


@pytest.fixture(scope="module")
def grafo():
    return GrafoDaParte2()


def test_bfs_acha_o_caminho_com_menos_arcos(grafo):
    r = grafo.rota("clubes", "BFS", SANTOS, PSG)
    assert r["status"] == "OK" and r["arcos"] == 2
    assert [c["id"] for c in r["caminho"]][0::2] == [SANTOS, PSG]
    assert r["custo"] == sum(t["peso"] for t in r["trechos"])


def test_dijkstra_bate_com_o_relatorio(grafo):
    r = grafo.rota("clubes", "DIJKSTRA", SANTOS, PSG)
    assert r["status"] == "OK" and r["custo"] == -42_500_000
    assert r["custo_deslocado"] == r["custo"] + r["arcos"] * grafo.desl


def test_dfs_segue_os_arcos_de_arvore(grafo):
    r = grafo.rota("clubes", "DFS", SANTOS, PSG)
    assert r["status"] == "OK" and r["caminho"][0]["id"] == SANTOS and r["caminho"][-1]["id"] == PSG
    assert r["arcos"] >= 2


def test_temporal_dijkstra_johnson_e_bellman_ford_dao_o_mesmo_custo(grafo):
    bf = grafo.rota("temporal", "BELLMAN_FORD", BENFICA, BOURNEMOUTH, 2015)
    dj = grafo.rota("temporal", "DIJKSTRA", BENFICA, BOURNEMOUTH, 2015)
    assert bf["status"] == dj["status"] == "OK"
    assert bf["custo"] == dj["custo"] == -335_460_000
    assert bf["caminho"][0] == {"id": BENFICA, "nome": "Benfica", "temporada": "15/16"}
    assert bf["caminho"][-1]["id"] == BOURNEMOUTH


def test_pedidos_invalidos(grafo):
    with pytest.raises(PedidoInvalido):
        grafo.rota("clubes", "A*", SANTOS, PSG)
    with pytest.raises(PedidoInvalido):
        grafo.rota("clubes", "BFS", SANTOS, SANTOS)
    with pytest.raises(PedidoInvalido):
        grafo.rota("temporal", "BFS", SANTOS, PSG, 1990)


def test_resumo_tem_os_clubes_e_o_contexto(grafo):
    r = grafo.resumo()
    assert len(r["clubes"]) == 4739
    assert len(r["contexto"]["nos"]) == 20
    ids = {c["id"] for c in r["contexto"]["nos"]}
    assert all(u in ids and v in ids for u, v, _ in r["contexto"]["arcos"])
