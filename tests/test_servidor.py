# [IA] Claude Code (Claude Opus 5.5) – testes do servidor do labirinto interativo: dados de cada algoritmo e mapa inválido
import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from src.graphs.io import MapaInvalido
from src.servidor import Servidor, analisar, mapas_do_projeto

MAPAS = Path(__file__).resolve().parent.parent / "data" / "mapas"


def dados(nome, fonte=False):
    arquivo = next(MAPAS.glob(f"{nome}_*.txt"))
    return analisar(arquivo.read_text(encoding="utf-8"), arquivo.stem, fonte)


def test_m03_dijkstra_e_bfs_batem_com_o_gabarito():
    algoritmos = dados("m03")["algoritmos"]
    assert (algoritmos["DIJKSTRA"]["passos"], algoritmos["DIJKSTRA"]["custo"]) == (91, 99)
    assert (algoritmos["BFS"]["passos"], algoritmos["BFS"]["custo"]) == (87, 119)


def test_custos_acumulados_terminam_no_custo_do_caminho():
    r = dados("m01")["algoritmos"]["DIJKSTRA"]
    assert r["custos"][0] == 0 and r["custos"][-1] == r["custo"] == 20
    assert len(r["custos"]) == len(r["caminho"]) == r["passos"] + 1


def test_m05_dijkstra_recusa_e_bellman_ford_resolve():
    algoritmos = dados("m05")["algoritmos"]
    assert algoritmos["DIJKSTRA"]["status"] == "RECUSA"
    assert (algoritmos["BELLMAN_FORD"]["status"], algoritmos["BELLMAN_FORD"]["custo"]) == ("OK", 5)


def test_m06_ciclo_negativo_e_fonte_consumivel():
    d = dados("m06")
    ciclo = d["algoritmos"]["BELLMAN_FORD"]["ciclo"]
    assert d["algoritmos"]["BELLMAN_FORD"]["status"] == "CICLO_NEGATIVO" and ciclo["custo"] == -1
    assert [d["estados"][i]["rotulo"] for i in ciclo["estados"]] == ["(3,5)|-|{}", "(3,6)|-|{}", "(3,5)|-|{}"]
    assert dados("m06", fonte=True)["algoritmos"]["BELLMAN_FORD"]["status"] == "OK"


def test_m07_sem_solucao_e_todos_os_estados_sao_armadilha():
    d = dados("m07")
    assert all(r["status"] == "SEM_SOLUCAO" for r in d["algoritmos"].values())
    assert all(e["armadilha"] for e in d["estados"])


def test_arcos_nao_incluem_o_alvo_e_batem_com_as_metricas():
    d = dados("m02")
    assert len(d["estados"]) == d["metricas"]["ordem"] == 39
    assert len(d["arcos"]) == d["metricas"]["tamanho"] == 74


def test_mapa_invalido_levanta_erro_claro():
    with pytest.raises(MapaInvalido, match="2 inícios S"):
        analisar("#####\n#S.S#\n#..G#\n#####", "ruim")


def test_rotas_do_servidor():
    servidor = Servidor(("127.0.0.1", 0), mapas_do_projeto())
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{servidor.server_address[1]}"
    try:
        lista = json.load(urllib.request.urlopen(f"{base}/api/mapas"))
        assert "m03_tres_chaves" in [m["id"] for m in lista]
        m04 = json.load(urllib.request.urlopen(f"{base}/api/mapas/m04_esteiras"))
        assert m04["algoritmos"]["BFS"]["status"] == "OK"
        pedido = urllib.request.Request(f"{base}/api/analisar?nome=ruim", data="#####\n#S.S#\n#..G#\n#####".encode(),
                                        method="POST")
        with pytest.raises(urllib.error.HTTPError) as erro:
            urllib.request.urlopen(pedido)
        assert erro.value.code == 400 and "2 inícios S" in json.load(erro.value)["erro"]
    finally:
        servidor.shutdown()
        servidor.server_close()
