from pathlib import Path

from src.graphs.estados import construir_estados, escrever_arestas_csv, exportar_arestas, metricas
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
