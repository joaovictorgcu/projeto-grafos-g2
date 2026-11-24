# [IA] Claude Code (Claude Opus 5.5) – testes do gerador do labirinto interativo
import json
import re
from pathlib import Path

import pytest

from src.viz import dados_do_mapa, gerar_interativo, main

MAPAS = Path(__file__).resolve().parent.parent / "data" / "mapas"


def test_status_de_cada_algoritmo():
    esperado = {
        "m03_tres_chaves": ("OK", "OK", "OK"),
        "m05_bonus": ("OK", "RECUSA", "OK"),
        "m06_fonte": ("OK", "RECUSA", "CICLO_NEGATIVO"),
        "m07_impossivel": ("SEM_SOLUCAO", "SEM_SOLUCAO", "SEM_SOLUCAO"),
    }
    for nome, status in esperado.items():
        algoritmos = dados_do_mapa(MAPAS / f"{nome}.txt")["algoritmos"]
        assert tuple(algoritmos[a]["status"] for a in ("BFS", "DIJKSTRA", "BELLMAN_FORD")) == status, nome


def test_camadas_e_armadilhas_nao_incluem_o_alvo():
    dados = dados_do_mapa(MAPAS / "m04_esteiras.txt")
    assert sum(len(nos) for nos in dados["camadas"].values()) == 37
    assert len(dados["armadilhas"]) == 4 and "ALVO" not in dados["armadilhas"]


def test_pagina_gerada_traz_os_dados_dos_mapas(tmp_path):
    saida = gerar_interativo([MAPAS / "m02_uma_chave.txt"], tmp_path / "labirinto.html")
    dados = re.search(r"const DADOS = (.*);\n", saida.read_text(encoding="utf-8")).group(1)
    mapa = json.loads(dados)["mapas"][0]
    assert mapa["id"] == "m02_uma_chave" and len(mapa["algoritmos"]["BFS"]["caminho"]) == 35


def test_figura_sem_mapa_e_recusada():
    with pytest.raises(SystemExit):
        main(["--png", "x.png"])
