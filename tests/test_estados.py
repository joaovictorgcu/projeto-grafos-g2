import re
from pathlib import Path

from src.graphs.estados import (ALVO, Estado, construir_estados, escrever_arestas_csv, exportar_arestas, metricas,
                                rotulo)
from src.graphs.io import interpretar_mapa, ler_mapa

MAPAS = Path(__file__).resolve().parent.parent / "data" / "mapas"


# [IA] Claude Code (Claude Opus 5.5) – testes das métricas sem o ALVO e do formato do arestas_<mapa>.csv
def test_metricas_nao_contam_o_alvo():
    m = metricas(construir_estados(interpretar_mapa("#####\n#S.G#\n#####")))
    assert (m["ordem"], m["tamanho"]) == (3, 3)
    assert m["densidade"] == 3 / (3 * 2)


def test_densidade_zero_com_menos_de_dois_estados():
    m = metricas(construir_estados(interpretar_mapa("#####\n#S#G#\n#####")))
    assert (m["ordem"], m["tamanho"], m["densidade"]) == (1, 0, 0.0)


def test_metricas_do_m02_batem_com_a_figura_do_caio():
    m = metricas(construir_estados(ler_mapa(MAPAS / "m02_uma_chave.txt")))
    assert (m["ordem"], m["tamanho"]) == (39, 74)


def test_csv_do_m02_tem_as_linhas_do_exemplo_do_enunciado(tmp_path):
    arcos = construir_estados(ler_mapa(MAPAS / "m02_uma_chave.txt")).arcos
    linhas = escrever_arestas_csv(arcos, tmp_path / "a.csv").read_text(encoding="utf-8").splitlines()
    assert linhas[0] == "origem,destino,movimento,casa_destino,peso"
    for linha in ['"(1,1)|-|{}","(2,1)|-|{}",S,.,1',
                  '"(3,10)|-|{}","(3,11)|a|{}",L,a,1',
                  '"(1,5)|a|{}","(1,6)|a|{}",L,A,1']:
        assert linha in linhas


def test_exportar_gera_um_csv_por_mapa(tmp_path):
    gerados = exportar_arestas([MAPAS], tmp_path)
    assert sorted(p.name for p in gerados) == [f"arestas_m0{i}.csv" for i in range(1, 9)]


# [IA] Claude Code (Claude Opus 5.5) – testes das regras do grafo de estados num mapa mínimo calculado à mão; contas conferidas por Caio
#
# Mapa mínimo, 5x7: 1 chave (a), 1 porta (A), 1 esteira (^), lama (,) e água (~).
#
#     0123456
#   0 #######
#   1 #S,a~^#     a esteira em (1,5) aponta para a parede de cima
#   2 #.#####
#   3 #.A.G##     a porta A tranca o corredor de baixo
#   4 #######
#
# Estados alcançáveis, contados à mão:
#   camada "-": (1,1) (1,2) (2,1) (3,1)                                   ->  4
#   camada "a": (1,3) (1,4) (1,5) (1,2) (1,1) (2,1) (3,1) (3,2) (3,3) (3,4) -> 10
#   total: 14 estados (sem o ALVO)
#
# Arcos de G_est, contados à mão (N, L, S, O; parede, porta trancada e borda não geram arco):
#   camada "-": (1,1)->2  (1,2)->2  (2,1)->2  (3,1)->1 (a porta barra o L)            =  7
#   camada "a": (1,3)->2  (1,4)->2  (1,5)->0 (esteira contra a parede)  (1,2)->2
#               (1,1)->2  (2,1)->2  (3,1)->2  (3,2)->2  (3,3)->2  (3,4)->0 (é G)      = 16
#   total: 23 arcos de movimento + 1 arco (3,4)|a|{} -> ALVO = 24 arcos no grafo
MINIMO = (
    "#######\n"
    "#S,a~^#\n"
    "#.#####\n"
    "#.A.G##\n"
    "#######\n"
)

ESTEIRA_PARA_A_DIREITA = (
    "#####\n"
    "#S..#\n"
    "#.>.#\n"
    "#..G#\n"
    "#####\n"
)

CRUZAMENTO = (
    "#####\n"
    "#...#\n"
    "#.S.#\n"
    "#...#\n"
    "#..G#\n"
    "#####\n"
)

ROTULO = re.compile(r"^\(\d+,\d+\)\|([a-d]+|-)\|\{(\d+(,\d+)*)?\}$")


def chaves_do(no):
    return set(no.split("|")[1].replace("-", ""))


def test_mapa_minimo_bate_com_a_conta_feita_a_mao():
    g = construir_estados(interpretar_mapa(MINIMO))
    estados = [n for n in g.grafo.nos() if n != ALVO]
    assert len(estados) == 14
    assert sum(1 for n in estados if chaves_do(n) == set()) == 4
    assert sum(1 for n in estados if chaves_do(n) == {"a"}) == 10
    assert g.grafo.tamanho() == 24
    assert metricas(g)["tamanho"] == 23


def test_rotulo_no_formato_exato_do_enunciado():
    assert rotulo(Estado(3, 5, frozenset("ba"), frozenset({2, 0}))) == "(3,5)|ab|{0,2}"
    assert rotulo(Estado(1, 1)) == "(1,1)|-|{}"
    g = construir_estados(interpretar_mapa(MINIMO))
    assert g.inicial == "(1,1)|-|{}"
    assert all(ROTULO.match(n) for n in g.grafo.nos() if n != ALVO)


def test_esteira_so_sai_na_direcao_da_seta():
    g = construir_estados(interpretar_mapa(ESTEIRA_PARA_A_DIREITA))
    # (2,2) tem casa livre ao norte, ao sul e a oeste, mas a seta só deixa ir para leste
    assert [(a.movimento, a.destino) for a in g.arcos if a.origem == "(2,2)|-|{}"] == [("L", "(2,3)|-|{}")]


def test_esteira_contra_a_parede_tem_grau_de_saida_zero():
    g = construir_estados(interpretar_mapa(MINIMO))
    assert "(1,5)|a|{}" in g.grafo.nos()
    assert g.grafo.grau_saida("(1,5)|a|{}") == 0


def test_pegar_a_chave_troca_de_camada_e_a_chave_nunca_se_perde():
    g = construir_estados(interpretar_mapa(MINIMO))
    trocas = [(a.origem, a.destino) for a in g.arcos
              if a.destino != ALVO and chaves_do(a.origem) != chaves_do(a.destino)]
    assert trocas == [("(1,2)|-|{}", "(1,3)|a|{}")]
    assert all(chaves_do(a.origem) <= chaves_do(a.destino) for a in g.arcos if a.destino != ALVO)


def test_porta_so_abre_com_a_chave():
    g = construir_estados(interpretar_mapa(MINIMO))
    para_a_porta = [a.origem for a in g.arcos if a.destino.startswith("(3,2)|")]
    assert para_a_porta == ["(3,1)|a|{}", "(3,3)|a|{}"]
    assert "(3,2)|-|{}" not in g.grafo.nos()
    assert ("(3,2)|a|{}", 1) in g.grafo.arcos("(3,1)|a|{}")


def test_custo_do_arco_e_o_custo_da_casa_de_destino():
    g = construir_estados(interpretar_mapa(MINIMO)).grafo
    assert ("(1,2)|-|{}", 3) in g.arcos("(1,1)|-|{}")   # entra na lama
    assert ("(1,1)|-|{}", 1) in g.arcos("(1,2)|-|{}")   # sai da lama para o chão
    assert ("(1,4)|a|{}", 5) in g.arcos("(1,3)|a|{}")   # entra na água
    assert ("(1,3)|a|{}", 1) in g.arcos("(1,4)|a|{}")   # sai da água para a chave


def test_estado_em_g_so_tem_o_arco_de_custo_zero_ate_o_alvo():
    g = construir_estados(interpretar_mapa(MINIMO)).grafo
    assert g.arcos("(3,4)|a|{}") == [(ALVO, 0)]
    assert g.arcos(ALVO) == []


def test_vizinhos_na_ordem_n_l_s_o():
    g = construir_estados(interpretar_mapa(CRUZAMENTO))
    assert [a.movimento for a in g.arcos if a.origem == "(2,2)|-|{}"] == ["N", "L", "S", "O"]
    assert g.grafo.vizinhos("(2,2)|-|{}") == ["(1,2)|-|{}", "(2,3)|-|{}", "(3,2)|-|{}", "(2,1)|-|{}"]
