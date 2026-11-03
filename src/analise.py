"""Análises e artefatos da Parte 1 (P3).

O módulo somente consome as interfaces de P1/P2.  Os arquivos gerados são
reprodutíveis com ``python -m src.analise`` e não escrevem código nos módulos
dos demais pacotes.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from .graphs.algorithms import bellman_ford, bfs, caminho, dfs, dijkstra, estados_armadilha
from .graphs.estados import ALVO, construir_estados, construir_posicoes
from .graphs.io import ler_mapa

ROOT = Path(__file__).resolve().parents[1]
MAPAS = ROOT / "data" / "mapas"
MAPAS_GRUPO = ROOT / "data" / "mapas_grupo"
OUT = ROOT / "out" / "parte1"
ROTULO = re.compile(r"\((\d+),(\d+)\)\|([^|]*)\|\{([^}]*)\}")


def dumps(data) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def write_csv(path: Path, headers, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)


def maps() -> list[tuple[str, Path]]:
    files = sorted(MAPAS.glob("*.txt")) + sorted(MAPAS_GRUPO.glob("*.txt"))
    return [(p.stem.split("_")[0] if p.parent == MAPAS else p.stem, p) for p in files]


def graph_metrics(grafo, include_target=False):
    nodes = [n for n in grafo.nos() if include_target or n != ALVO]
    node_set = set(nodes)
    edges = sum(1 for u in nodes for v, _ in grafo.arcos(u) if v in node_set)
    order = len(nodes)
    return {
        "ordem": order,
        "tamanho": edges,
        "densidade": edges / (order * (order - 1)) if order > 1 else 0.0,
    }


def metricas_globais():
    result = {}
    for nome, path in maps():
        mapa = ler_mapa(path)
        pos_chao = construir_posicoes(mapa, "chao")
        pos_parede = construir_posicoes(mapa, "parede")
        estados = construir_estados(mapa)
        teto = mapa.livres * (2 ** len(mapa.tipos_de_chave)) * (2 ** len(mapa.bonus))
        est = graph_metrics(estados.grafo)
        result[nome] = {
            "arquivo": str(path.relative_to(ROOT)),
            "chaves": mapa.tipos_de_chave,
            "bonus": len(mapa.bonus),
            "livres": mapa.livres,
            "teto_teorico": teto,
            "G_pos_portas_chao": graph_metrics(pos_chao.grafo),
            "G_pos_portas_parede": graph_metrics(pos_parede.grafo),
            "G_est": est,
            "ocupacao_G_est": est["ordem"] / teto if teto else 0.0,
        }
    (OUT / "metricas_global.json").write_text(dumps(result), encoding="utf-8")
    return result


def camadas():
    result = {}
    for nome, path in maps():
        construido = construir_estados(ler_mapa(path))
        grupos = defaultdict(list)
        for no in construido.grafo.nos():
            if no == ALVO:
                continue
            m = ROTULO.fullmatch(no)
            if not m:
                continue
            chaves = m.group(3) or "-"
            grupos[chaves].append(no)
        camadas_map = {}
        for chave, nos in sorted(grupos.items()):
            internos = [(u, v) for u in nos for v, _ in construido.grafo.arcos(u) if v in grupos[chave]]
            camadas_map[chave] = {
                "estados": len(nos),
                "arcos_internos": len(internos),
                "grau_saida_medio": sum(construido.grafo.grau_saida(n) for n in nos) / len(nos),
            }
        entre = Counter()
        for u in construido.grafo.nos():
            if u == ALVO or not ROTULO.fullmatch(u):
                continue
            ku = ROTULO.fullmatch(u).group(3) or "-"
            for v, _ in construido.grafo.arcos(u):
                if v == ALVO or not ROTULO.fullmatch(v):
                    continue
                kv = ROTULO.fullmatch(v).group(3) or "-"
                if ku != kv:
                    entre[f"{ku}->{kv}"] += 1
        result[nome] = {"camadas": camadas_map, "arcos_entre_camadas": dict(sorted(entre.items()))}
    (OUT / "camadas.json").write_text(dumps(result), encoding="utf-8")
    return result


def graus():
    for nome, path in maps():
        g = construir_estados(ler_mapa(path)).grafo
        rows = [(n, g.grau_entrada(n), g.grau_saida(n)) for n in g.nos()]
        write_csv(OUT / f"graus_{nome}.csv", ["estado", "grau_entrada", "grau_saida"], rows)


def custo_caminho(grafo, nodes):
    return sum(next(p for v, p in grafo.arcos(u) if v == w) for u, w in zip(nodes, nodes[1:]))


def solution_row(nome, alg, construido):
    g, inicio = construido.grafo, construido.inicial
    try:
        if alg == "BFS":
            dist, pai = bfs(g, inicio)
            if ALVO not in dist:
                return [nome, alg, "SEM_SOLUCAO", "", ""]
            path = caminho(pai, ALVO)
            return [nome, alg, "OK", len(path) - 2, custo_caminho(g, path[:-1])]
        if alg == "DIJKSTRA":
            dist, pai = dijkstra(g, inicio)
            if ALVO not in dist:
                return [nome, alg, "SEM_SOLUCAO", "", ""]
            path = caminho(pai, ALVO)
            return [nome, alg, "OK", len(path) - 2, dist[ALVO]]
        dist, pai, ciclo = bellman_ford(g, inicio)
        if ciclo:
            return [nome, alg, "CICLO_NEGATIVO", "", ciclo[1]]
        if ALVO not in dist:
            return [nome, alg, "SEM_SOLUCAO", "", ""]
        path = caminho(pai, ALVO)
        return [nome, alg, "OK", len(path) - 2, dist[ALVO]]
    except (ValueError, KeyError) as exc:
        return [nome, alg, "ERRO", "", str(exc)]


def solucoes():
    rows = []
    for nome, path in maps():
        construido = construir_estados(ler_mapa(path))
        for alg in ("BFS", "DIJKSTRA", "BELLMAN_FORD"):
            rows.append(solution_row(nome, alg, construido))
    write_csv(OUT / "solucoes.csv", ["mapa", "algoritmo", "status", "passos", "custo_ou_motivo"], rows)


def dfs_classificacao():
    rows = []
    for nome, path in maps():
        construido = construir_estados(ler_mapa(path))
        tipos, _, _, _ = dfs(construido.grafo, [construido.inicial])
        for (u, v), tipo in sorted(tipos.items()):
            rows.append([nome, u, v, tipo])
    write_csv(OUT / "dfs_classificacao.csv", ["mapa", "origem", "destino", "tipo"], rows)


def percurso_m03():
    path = MAPAS / "m03_tres_chaves.txt"
    construido = construir_estados(ler_mapa(path))
    dist, pai, ciclo = bellman_ford(construido.grafo, construido.inicial)
    rotulos = caminho(pai, ALVO) if not ciclo else None
    data = {
        "mapa": "m03",
        "algoritmo": "BELLMAN_FORD",
        "status": "OK" if rotulos else "SEM_SOLUCAO",
        "passos": len(rotulos) - 2 if rotulos else None,
        "custo": dist.get(ALVO),
        "caminho": rotulos[:-1] if rotulos else None,
    }
    (OUT / "percurso_m03.json").write_text(dumps(data), encoding="utf-8")


def ciclo_m06():
    construido = construir_estados(ler_mapa(MAPAS / "m06_fonte.txt"))
    _, _, ciclo = bellman_ford(construido.grafo, construido.inicial)
    data = {"mapa": "m06", "status": "CICLO_NEGATIVO" if ciclo else "SEM_CICLO_NEGATIVO"}
    if ciclo:
        data.update({"caminho_do_ciclo": ciclo[0], "custo_do_ciclo": ciclo[1]})
    (OUT / "ciclo_negativo_m06.json").write_text(dumps(data), encoding="utf-8")


def armadilhas():
    for nome in ("m04", "m07"):
        path = MAPAS / next(p.name for p in MAPAS.glob(f"{nome}_*.txt"))
        g = construir_estados(ler_mapa(path)).grafo
        traps = estados_armadilha(g, ALVO)
        rows = []
        for no in traps:
            m = ROTULO.fullmatch(no)
            linha, coluna, chaves, bonus = m.groups() if m else ("", "", "", "")
            rows.append([no, linha, coluna, chaves, bonus])
        write_csv(OUT / f"armadilhas_{nome}.csv", ["estado", "linha", "coluna", "chaves", "bonus"], rows)


def comparacao_modelagem():
    rows = []
    for nome in ("m02", "m03", "m04"):
        path = MAPAS / next(p.name for p in MAPAS.glob(f"{nome}_*.txt"))
        mapa = ler_mapa(path)
        estado = construir_estados(mapa)
        for modelo, construido in (("portas_chao", construir_posicoes(mapa, "chao")), ("portas_parede", construir_posicoes(mapa, "parede")), ("estados", estado)):
            dist, _ = bfs(construido.grafo, construido.inicial)
            rows.append([nome, modelo, len([n for n in construido.grafo.nos() if n != ALVO]), graph_metrics(construido.grafo)["tamanho"], "OK" if ALVO in dist else "SEM_SOLUCAO", dist.get(ALVO, "")])
    write_csv(OUT / "comparacao_modelagem.csv", ["mapa", "modelo", "ordem", "tamanho", "status_bfs", "passos_bfs"], rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    metricas_globais()
    camadas()
    graus()
    comparacao_modelagem()
    solucoes()
    dfs_classificacao()
    percurso_m03()
    ciclo_m06()
    armadilhas()
    print(f"Artefatos do P3 gerados em {OUT}")


if __name__ == "__main__":
    main()
