import json
from pathlib import Path

from src.graphs.algorithms import estados_armadilha
from src.graphs.estados import ALVO, construir_estados
from src.graphs.io import ler_mapa

ROOT = Path(__file__).resolve().parents[1]
MAPAS_GRUPO = ROOT / "data" / "mapas_grupo"
OUT = ROOT / "out" / "parte1"


def test_mapa_guilherme_tem_tres_chaves_esteiras_e_bonus():
    mapa = ler_mapa(MAPAS_GRUPO / "guilherme_03_chaves.txt")
    assert len(mapa.tipos_de_chave) >= 3
    assert mapa.esteiras
    assert mapa.bonus


def test_mapa_guilherme_tem_pelo_menos_vinte_porcento_de_armadilhas():
    mapa = ler_mapa(MAPAS_GRUPO / "guilherme_armadilhas.txt")
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
    assert json.loads((OUT / "metricas_global.json").read_text(encoding="utf-8"))
