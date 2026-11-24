import csv
import json
from pathlib import Path

import networkx as nx
import pytest

from src.analise import maps

from src.graphs.algorithms import estados_armadilha
from src.graphs.estados import ALVO, construir_estados
from src.graphs.io import ler_mapa

ROOT = Path(__file__).resolve().parents[1]
MAPAS_GRUPO = ROOT / "data" / "mapas_grupo"
OUT = ROOT / "out" / "parte1"


def test_mapa_chaves_tem_tres_chaves_esteiras_e_bonus():
    mapa = ler_mapa(MAPAS_GRUPO / "mapa_chaves.txt")
    assert mapa.nome == "mapa_chaves"
    assert (mapa.altura, mapa.largura) == (12, 17)
    assert len(mapa.tipos_de_chave) >= 3
    assert mapa.esteiras
    assert mapa.bonus


def test_mapa_armadilhas_tem_pelo_menos_vinte_porcento_de_armadilhas():
    mapa = ler_mapa(MAPAS_GRUPO / "mapa_armadilhas.txt")
    assert mapa.nome == "mapa_armadilhas"
    assert (mapa.altura, mapa.largura) == (5, 13)
    grafo = construir_estados(mapa).grafo
    estados = [no for no in grafo.nos() if no != ALVO]
    armadilhas = estados_armadilha(grafo, ALVO)
    assert len(armadilhas) / len(estados) >= 0.20


def test_artefatos_obrigatorios_do_p3_existem():
    obrigatorios = [
        "metricas_global.json",
        "camadas.json",
        "comparacao_modelagem.csv",
        "solucoes.csv",
        "dfs_classificacao.csv",
        "percurso_m03.json",
        "ciclo_negativo_m06.json",
        "armadilhas_m04.csv",
        "armadilhas_m07.csv",
    ]
    assert all((OUT / nome).exists() for nome in obrigatorios)
    metricas = json.loads((OUT / "metricas_global.json").read_text(encoding="utf-8"))
    assert {"mapa_chaves", "mapa_armadilhas"} <= metricas.keys()
    assert (OUT / "graus_mapa_chaves.csv").exists()
    assert (OUT / "graus_mapa_armadilhas.csv").exists()


# ---- Conferência (revisão do P3): recalcula os artefatos de out/parte1 com networkx ----
# — [IA] Claude – testes de conferência dos artefatos do P3 gerados pela IA; executados e integrados por mim

MAPAS_POR_NOME = dict(maps())


def referencia(nome):
    """Grafo de estados do mapa em um DiGraph do networkx (menor peso entre arcos paralelos)."""
    construido = construir_estados(ler_mapa(MAPAS_POR_NOME[nome]))
    ref = nx.DiGraph()
    ref.add_nodes_from(construido.grafo.nos())
    for u in construido.grafo.nos():
        for v, p in construido.grafo.arcos(u):
            if not ref.has_edge(u, v) or p < ref[u][v]["weight"]:
                ref.add_edge(u, v, weight=p)
    return construido.inicial, ref


def ler_csv(nome):
    with (OUT / nome).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.mark.parametrize("linha", ler_csv("solucoes.csv"), ids=lambda l: f"{l['mapa']}-{l['algoritmo']}")
def test_solucoes_batem_com_o_networkx(linha):
    inicio, ref = referencia(linha["mapa"])
    status, alg = linha["status"], linha["algoritmo"]
    tem_negativo = any(d["weight"] < 0 for _, _, d in ref.edges(data=True))

    if status == "RECUSA":  # só o Dijkstra pode recusar, e só se houver peso negativo
        assert alg == "DIJKSTRA" and tem_negativo
    elif status == "CICLO_NEGATIVO":
        assert alg == "BELLMAN_FORD"
        assert nx.negative_edge_cycle(ref, weight="weight")
        assert float(linha["custo"]) < 0
    elif status == "SEM_SOLUCAO":
        assert not nx.has_path(ref, inicio, ALVO)
    else:
        assert status == "OK"
        if alg == "BFS":
            esperado = nx.shortest_path_length(ref, inicio, ALVO) - 1  # sem o arco final até o ALVO
            assert int(linha["passos"]) == esperado
        else:
            esperado = nx.bellman_ford_path_length(ref, inicio, ALVO, weight="weight")
            assert float(linha["custo"]) == esperado


def test_percurso_m03_e_um_caminho_valido():
    dados = json.loads((OUT / "percurso_m03.json").read_text(encoding="utf-8"))
    inicio, ref = referencia("m03")
    caminho = dados["caminho"]
    assert caminho[0] == inicio and dados["passos"] == len(caminho) - 1
    assert all(ref.has_edge(a, b) for a, b in zip(caminho, caminho[1:]))
    assert ref.has_edge(caminho[-1], ALVO)
    assert sum(ref[a][b]["weight"] for a, b in zip(caminho, caminho[1:])) == dados["custo"]
    assert dados["custo"] == nx.bellman_ford_path_length(ref, inicio, ALVO, weight="weight")


def test_ciclo_negativo_m06_e_um_ciclo_negativo_de_verdade():
    dados = json.loads((OUT / "ciclo_negativo_m06.json").read_text(encoding="utf-8"))
    _, ref = referencia("m06")
    ciclo = dados["caminho_do_ciclo"]
    assert dados["status"] == "CICLO_NEGATIVO" and ciclo[0] == ciclo[-1]
    assert all(ref.has_edge(a, b) for a, b in zip(ciclo, ciclo[1:]))
    custo = sum(ref[a][b]["weight"] for a, b in zip(ciclo, ciclo[1:]))
    assert custo == dados["custo_do_ciclo"] < 0


@pytest.mark.parametrize("nome", ["m04", "m07"])
def test_armadilhas_sao_os_estados_que_nao_chegam_ao_alvo(nome):
    inicio, ref = referencia(nome)
    sem_saida = {n for n in ref.nodes if n != ALVO and not nx.has_path(ref, n, ALVO)}
    assert {l["estado"] for l in ler_csv(f"armadilhas_{nome}.csv")} == sem_saida


def test_dfs_classificacao_forma_uma_arvore_geradora():
    """Em cada mapa, os arcos de árvore ligam exatamente os estados alcançáveis do início."""
    for linha in ler_csv("dfs_classificacao.csv"):
        nome = linha["mapa"]
        inicio, ref = referencia(nome)
        alcancaveis = nx.descendants(ref, inicio) | {inicio}
        tipos = {tipo: int(linha[tipo]) for tipo in ("arvore", "retorno", "avanco", "cruzamento")}
        assert tipos["arvore"] == len(alcancaveis) - 1, nome
        assert sum(tipos.values()) == sum(ref.out_degree(n) for n in alcancaveis), nome
