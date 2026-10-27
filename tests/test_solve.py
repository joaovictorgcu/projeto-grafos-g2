"""CLI da Parte 1 (--mapa): algoritmos, fonte consumível, armadilhas, mapa surpresa e erros."""
# — [IA] Claude – testes do src/solve.py gerados pela IA; executados e integrados por mim
import csv
import json
from pathlib import Path

import pytest

from src import solve
from src.cli import main

MAPAS = Path(__file__).resolve().parent.parent / "data" / "mapas"


def rodar(mapa, saida, *extra):
    codigo = main(["--mapa", str(mapa), "--out", str(saida), *extra])
    return codigo


def resultado(saida, alg, nome):
    return json.loads((saida / f"{alg.lower()}_{nome}.json").read_text(encoding="utf-8"))


def test_bfs_acha_caminho(tmp_path):
    assert rodar(MAPAS / "m03_tres_chaves.txt", tmp_path, "--alg", "BFS") == 0
    r = resultado(tmp_path, "BFS", "m03")
    assert r["status"] == "OK" and r["passos"] > 0
    assert r["caminho"][0].startswith("(") and "ALVO" not in r["caminho"]


def test_dijkstra_recusa_peso_negativo(tmp_path):
    assert rodar(MAPAS / "m05_bonus.txt", tmp_path, "--alg", "dijkstra") == 0
    r = resultado(tmp_path, "DIJKSTRA", "m05")
    assert r["status"] == "RECUSA" and "negativos" in r["motivo"]


def test_bellman_ford_resolve_peso_negativo(tmp_path):
    rodar(MAPAS / "m05_bonus.txt", tmp_path, "--alg", "BELLMAN_FORD")
    assert resultado(tmp_path, "BELLMAN_FORD", "m05")["status"] == "OK"


def test_fonte_infinita_gera_ciclo_negativo(tmp_path):
    rodar(MAPAS / "m06_fonte.txt", tmp_path, "--alg", "BELLMAN_FORD")
    r = resultado(tmp_path, "BELLMAN_FORD", "m06")
    assert r["status"] == "CICLO_NEGATIVO" and r["custo_do_ciclo"] < 0
    assert r["ciclo"][0] == r["ciclo"][-1]


def test_fonte_consumivel_remove_o_ciclo(tmp_path):
    rodar(MAPAS / "m06_fonte.txt", tmp_path, "--alg", "BELLMAN_FORD", "--fonte-consumivel")
    r = resultado(tmp_path, "BELLMAN_FORD", "m06")
    assert r["status"] == "OK" and r["fonte_consumivel"] is True


def test_mapa_sem_solucao(tmp_path):
    rodar(MAPAS / "m07_impossivel.txt", tmp_path, "--alg", "BFS")
    assert resultado(tmp_path, "BFS", "m07")["status"] == "SEM_SOLUCAO"


def test_dfs_grava_classificacao(tmp_path):
    rodar(MAPAS / "m03_tres_chaves.txt", tmp_path, "--alg", "DFS")
    r = resultado(tmp_path, "DFS", "m03")
    assert set(r["classificacao"]) == {"arvore", "retorno", "avanco", "cruzamento"}
    with (tmp_path / "dfs_classificacao_m03.csv").open(encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))
    assert len(linhas) == sum(r["classificacao"].values())


@pytest.mark.parametrize("mapa, esperado", [("m02_uma_chave", 0), ("m04_esteiras", 4), ("m07_impossivel", 16)])
def test_armadilhas(tmp_path, mapa, esperado):
    assert rodar(MAPAS / f"{mapa}.txt", tmp_path, "--armadilhas") == 0
    nome = mapa.split("_")[0]
    with (tmp_path / f"armadilhas_{nome}.csv").open(encoding="utf-8") as f:
        assert len(list(csv.DictReader(f))) == esperado


def test_mapa_surpresa_em_qualquer_caminho(tmp_path):
    estranho = tmp_path / "pasta qualquer" / "meu mapa novo.txt"
    estranho.parent.mkdir()
    estranho.write_text("#######\n#S.~.G#\n#.###.#\n#a..A.#\n#######\n", encoding="utf-8")
    assert rodar(estranho, tmp_path / "saida", "--alg", "DIJKSTRA") == 0
    assert resultado(tmp_path / "saida", "DIJKSTRA", "meu mapa novo")["status"] == "OK"


@pytest.mark.parametrize("conteudo", ["#####\n#S.X#\n#####\n", "#####\n#...#\n#####\n", "", "###\n#S#G\n###\n"])
def test_mapa_invalido_nao_quebra(tmp_path, capsys, conteudo):
    ruim = tmp_path / "ruim.txt"
    ruim.write_text(conteudo, encoding="utf-8")
    assert rodar(ruim, tmp_path, "--alg", "BFS") == 2
    assert "erro" in capsys.readouterr().err


def test_arquivo_inexistente_nao_quebra(tmp_path, capsys):
    assert rodar(tmp_path / "nao_existe.txt", tmp_path, "--alg", "BFS") == 2
    assert "erro" in capsys.readouterr().err


def test_sem_acao_pede_alg(tmp_path, capsys):
    assert rodar(MAPAS / "m01_terreno.txt", tmp_path) == 2
    assert "--alg" in capsys.readouterr().err


def test_interactive_chama_o_streamlit_com_o_mapa(tmp_path, monkeypatch):
    chamadas = []

    class Retorno:
        returncode = 0

    monkeypatch.setattr(solve.subprocess, "run", lambda cmd: chamadas.append(cmd) or Retorno())
    assert rodar(MAPAS / "m03_tres_chaves.txt", tmp_path, "--interactive") == 0
    assert "streamlit" in chamadas[0] and chamadas[0][-2] == "--mapa"
    assert chamadas[0][-1].endswith("m03_tres_chaves.txt")