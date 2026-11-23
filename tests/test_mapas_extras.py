# [IA] Claude Code (Claude Opus 5.5) – mapas de teste com o que m01–m08 não exercitam, preparação para o mapa surpresa
import pytest

from src.graphs.algorithms import bellman_ford, bfs, caminho, dijkstra
from src.graphs.estados import ALVO, construir_estados
from src.graphs.io import interpretar_mapa

COM_COMENTARIOS = (
    "; mapa de teste: comentários antes, no meio e depois da grade\n"
    "######\n"
    "; entre duas linhas\n"
    "#S..G#\n"
    "######\n"
    "; fim\n"
)
SEM_COMENTARIOS = "######\n#S..G#\n######\n"

DUAS_SAIDAS = (
    "########\n"
    "#G..S.G#\n"
    "########\n"
)

ESTEIRAS_ESQUERDA_E_BAIXO = (
    "#######\n"
    "#S..v.#\n"
    "#.#.#.#\n"
    "#.<.G.#\n"
    "#######\n"
)

BONUS_E_FONTE = (
    "#######\n"
    "#S+.*G#\n"
    "#######\n"
)

CHAVE_E_BONUS = (
    "#######\n"
    "#S+aAG#\n"
    "#######\n"
)

TODOS = {
    "comentarios": COM_COMENTARIOS,
    "duas_saidas": DUAS_SAIDAS,
    "esteiras": ESTEIRAS_ESQUERDA_E_BAIXO,
    "bonus_e_fonte": BONUS_E_FONTE,
    "chave_e_bonus": CHAVE_E_BONUS,
}


def construir(texto, **opcoes):
    return construir_estados(interpretar_mapa(texto, "teste"), **opcoes)


def test_comentarios_nao_mudam_o_grafo():
    assert construir(COM_COMENTARIOS).arcos == construir(SEM_COMENTARIOS).arcos


def test_duas_saidas_ligam_as_duas_ao_alvo():
    g = construir(DUAS_SAIDAS)
    assert sorted(a.origem for a in g.arcos if a.destino == ALVO) == ["(1,1)|-|{}", "(1,6)|-|{}"]


def test_duas_saidas_o_bfs_vai_pela_mais_proxima():
    g = construir(DUAS_SAIDAS)
    _, pai = bfs(g.grafo, g.inicial)
    assert caminho(pai, ALVO) == ["(1,4)|-|{}", "(1,5)|-|{}", "(1,6)|-|{}", ALVO]


def test_saida_nao_tem_movimento_so_o_arco_ate_o_alvo():
    g = construir(DUAS_SAIDAS)
    assert g.grafo.arcos("(1,1)|-|{}") == [(ALVO, 0)]
    assert g.grafo.arcos("(1,6)|-|{}") == [(ALVO, 0)]


def test_esteira_para_esquerda_so_anda_para_oeste():
    g = construir(ESTEIRAS_ESQUERDA_E_BAIXO)
    assert [a.movimento for a in g.arcos if a.origem == "(3,2)|-|{}"] == ["O"]


def test_esteira_para_baixo_contra_a_parede_vira_beco():
    g = construir(ESTEIRAS_ESQUERDA_E_BAIXO)
    assert "(1,4)|-|{}" in g.grafo.nos()
    assert g.grafo.arcos("(1,4)|-|{}") == []


def test_bonus_e_numerado_e_a_fonte_nao_entra_no_conjunto():
    g = construir(BONUS_E_FONTE)
    assert {n.split("|")[2] for n in g.grafo.nos() if n != ALVO} == {"{}", "{0}"}


def test_bonus_e_fonte_sem_correcao_tem_ciclo_negativo():
    g = construir(BONUS_E_FONTE)
    with pytest.raises(ValueError):
        dijkstra(g.grafo, g.inicial)
    assert bellman_ford(g.grafo, g.inicial)[2] is not None


def test_bonus_e_fonte_com_fonte_consumivel_fica_finito():
    g = construir(BONUS_E_FONTE, fonte_consumivel=True)
    dist, _, ciclo = bellman_ford(g.grafo, g.inicial)
    assert ciclo is None and ALVO in dist
    assert any(n.endswith("|{0,1}") for n in g.grafo.nos())


def test_chave_e_bonus_convivem_no_mesmo_estado():
    assert "(1,4)|a|{0}" in construir(CHAVE_E_BONUS).grafo.nos()


def test_pegar_a_chave_preserva_os_bonus():
    g = construir(CHAVE_E_BONUS)
    assert any(a.origem == "(1,2)|-|{0}" and a.destino == "(1,3)|a|{0}" for a in g.arcos)


def test_bonus_ja_consumido_custa_1():
    g = construir(CHAVE_E_BONUS)
    assert ("(1,2)|-|{0}", 1) in g.grafo.arcos("(1,1)|-|{0}")


@pytest.mark.parametrize("nome", TODOS)
def test_pipeline_nao_quebra_nos_mapas_extras(nome):
    g = construir(TODOS[nome])
    bfs(g.grafo, g.inicial)
    bellman_ford(g.grafo, g.inicial)
    try:
        dijkstra(g.grafo, g.inicial)
    except ValueError as erro:
        assert "negativ" in str(erro)
