"""Experimentos da Parte 2: BFS, DFS, Dijkstra e Bellman-Ford na rede de transferências."""
import gc
import json
import random
import statistics
import time
import tracemalloc
from collections import Counter
from pathlib import Path

import pandas as pd

from .graphs.algorithms import bellman_ford, bfs, caminho, dfs, dijkstra
from .graphs.dataset import Dataset, grafo_de_clubes, grafo_temporal
from .graphs.graph import Grafo

FONTES = [294, 418, 221]  # Benfica (maior grau de saída), Real Madrid, Santos
PARES_DIJKSTRA = [
    (221, 583),   # Santos -> PSG
    (614, 131),   # Flamengo -> Barcelona
    (209, 27),    # River Plate -> Bayern Munich
    (189, 418),   # Boca Juniors -> Real Madrid
    (610, 294),   # Ajax -> Benfica
    (614, 985),   # Flamengo -> Man Utd
]
CLUBES_DO_RECORTE = 40
FONTE_TEMPORAL = (294, 2015)  # (Benfica, 15/16)
TAMANHOS = (10, 25, 50, 75, 100)
REPETICOES = 5
SEMENTE = 42
LIMITE_MEMORIA_BF = 30_000_000


def resolver_clube(d: Dataset, texto) -> int:
    if isinstance(texto, int) or str(texto).isdigit():
        clube = int(texto)
        if clube not in d.nomes:
            raise ValueError(f"não existe clube com id {clube} no dataset.")
        return clube
    alvo = str(texto).strip().casefold()
    exatos = [c for c, n in d.nomes.items() if n.casefold() == alvo]
    if not exatos:
        parecidos = sorted(n for n in d.nomes.values() if alvo in n.casefold())[:10]
        dica = f" Parecidos: {', '.join(parecidos)}." if parecidos else ""
        raise ValueError(f"não achei o clube {texto!r}.{dica}")
    no_grafo = [c for c in exatos if c in set(d.arcos["origem"]) | set(d.arcos["destino"])]
    return (no_grafo or exatos)[0]


def deslocamento(d: Dataset) -> int:
    return -int(d.arcos["peso"].min())


def peso_original(grafo_original: Grafo, rota) -> int:
    return sum(next(p for w, p in grafo_original.arcos(u) if w == v) for u, v in zip(rota, rota[1:]))


def ciclo_da_dfs(tipo, inicio=None):
    pai = {v: u for (u, v), t in tipo.items() if t == "arvore"}
    for (u, v), t in tipo.items():
        if t == "retorno":
            ciclo = [u]
            while ciclo[-1] != v:
                ciclo.append(pai[ciclo[-1]])
            ciclo.reverse()
            return ciclo + [v]
    return None


def transferencias_do_arco(d: Dataset, u, v, n=3) -> list:
    t = d.usadas
    if isinstance(u, tuple):
        m = (t["from_club_id"] == u[0]) & (t["to_club_id"] == v[0]) & (t["temporada"] == u[1])
    else:
        m = (t["from_club_id"] == u) & (t["to_club_id"] == v)
    linhas = t[m].sort_values("peso").head(n)
    return [f"{r.player_name} ({r.transfer_season}): {int(r.peso):,}".replace(",", ".")
            for r in linhas.itertuples()]


def subgrafo_induzido(arcos: pd.DataFrame, nos) -> pd.DataFrame:
    nos = set(nos)
    return arcos[arcos["origem"].isin(nos) & arcos["destino"].isin(nos)]


def tarefa_bfs(d: Dataset, g: Grafo, fonte) -> dict:
    dist, pai = bfs(g, fonte)
    camadas = Counter(dist.values())
    ordem = sorted(dist, key=lambda v: dist[v])  # a BFS descobre por nível
    return {
        "fonte": fonte, "nome": d.nome(fonte),
        "alcancados": len(dist), "nao_alcancados": g.ordem() - len(dist),
        "excentricidade": max(dist.values()),
        "camadas": [camadas[k] for k in range(max(dist.values()) + 1)],
        "ordem_primeiros": [d.nome(v) for v in ordem[:12]],
    }


def tarefa_dfs(d: Dataset, g: Grafo, fonte) -> dict:
    tipo, desc, fim, tem_ciclo = dfs(g, [fonte])
    ordem = sorted(desc, key=desc.get)
    ciclo = ciclo_da_dfs(tipo)
    contagem = Counter(tipo.values())
    resultado = {
        "fonte": fonte, "nome": d.nome(fonte),
        "alcancados": len(desc),
        "arcos": {t: contagem.get(t, 0) for t in ("arvore", "retorno", "avanco", "cruzamento")},
        "tem_ciclo": tem_ciclo,
        "ordem_primeiros": [d.nome(v) for v in ordem[:12]],
    }
    if ciclo:
        resultado["exemplo_ciclo"] = {"clubes": [d.nome(v) for v in ciclo],
                                      "peso_original": peso_original(g, ciclo)}
    return resultado


def tarefa_dijkstra(d: Dataset, g: Grafo, g_desl: Grafo, origem, destino) -> dict:
    dist, pai = dijkstra(g_desl, origem)
    rota = caminho(pai, destino)
    _, pai_bfs = bfs(g, origem)
    rota_bfs = caminho(pai_bfs, destino)
    if rota is None:
        return {"origem": d.nome(origem), "destino": d.nome(destino), "status": "SEM_CAMINHO"}
    return {
        "origem": d.nome(origem), "destino": d.nome(destino), "status": "OK",
        "arcos": len(rota) - 1,
        "custo_transformado": dist[destino],
        "custo_original": peso_original(g, rota),
        "caminho": [d.nome(v) for v in rota],
        "passos_bfs": len(rota_bfs) - 1,
        "transferencias": {f"{d.nome(u)} -> {d.nome(v)}": transferencias_do_arco(d, u, v)
                           for u, v in zip(rota, rota[1:])},
    }


def johnson(g: Grafo):
    virtual = ("__virtual__", 0)
    aux = Grafo()
    for u in g.nos():
        aux.adicionar_arco(virtual, u, 0)
    for u in g.nos():
        for v, p in g.arcos(u):
            aux.adicionar_arco(u, v, p)
    h, _, ciclo = bellman_ford(aux, virtual)
    if ciclo is not None:
        raise ValueError("Johnson exige grafo sem ciclo negativo.")
    repesado = Grafo()
    for u in g.nos():
        repesado.adicionar_no(u)
        for v, p in g.arcos(u):
            repesado.adicionar_arco(u, v, p + h[u] - h[v])
    return repesado, h


def tarefa_bf_sem_ciclo(d: Dataset, gt: Grafo, fonte) -> dict:
    dist, pai, ciclo = bellman_ford(gt, fonte)
    alvos = sorted((v for v in dist if v != fonte), key=lambda v: (dist[v], v))
    mais_barato = alvos[0]
    rota = caminho(pai, mais_barato)

    repesado, h = johnson(gt)
    dist_j, _ = dijkstra(repesado, fonte)
    dist_j = {v: c - h[fonte] + h[v] for v, c in dist_j.items()}
    divergencias = sum(1 for v in dist if dist_j.get(v) != dist[v])

    return {
        "grafo": "temporal (clube, temporada)",
        "ordem": gt.ordem(), "tamanho": gt.tamanho(),
        "arcos_negativos": sum(1 for u in gt.nos() for _, p in gt.arcos(u) if p < 0),
        "fonte": d.nome(fonte),
        "ciclo_negativo": ciclo is not None,
        "alcancados": len(dist),
        "distancias_negativas": sum(1 for c in dist.values() if c < 0),
        "menor_custo": {
            "destino": d.nome(mais_barato), "custo": dist[mais_barato], "arcos": len(rota) - 1,
            "caminho": [d.nome(v) for v in rota],
            "transferencias": {f"{d.nome(u)} -> {d.nome(v)}": transferencias_do_arco(d, u, v)
                               for u, v in zip(rota, rota[1:]) if u[0] != v[0]},
        },
        "dijkstra_johnson_confere": {"nos_comparados": len(dist), "divergencias": divergencias},
    }


def tarefa_bf_com_ciclo(d: Dataset, arcos: pd.DataFrame, fonte, rotulo: str) -> dict:
    g = grafo_de_clubes(arcos)
    t0 = time.perf_counter()
    dist, _, ciclo = bellman_ford(g, fonte)
    segundos = time.perf_counter() - t0
    resultado = {"grafo": rotulo, "ordem": g.ordem(), "tamanho": g.tamanho(),
                 "fonte": d.nome(fonte), "alcancados": len(dist),
                 "ciclo_negativo": ciclo is not None, "segundos": round(segundos, 3)}
    if ciclo:
        nos, custo = ciclo
        resultado["ciclo"] = {
            "clubes": [d.nome(v) for v in nos], "custo": custo, "arcos": len(nos) - 1,
            "transferencias": {f"{d.nome(u)} -> {d.nome(v)}": transferencias_do_arco(d, u, v)
                               for u, v in zip(nos, nos[1:])},
        }
    return resultado


def pares_ciclo_2(d: Dataset, n=10) -> list:
    a = d.arcos
    volta = a.rename(columns={"origem": "destino", "destino": "origem", "peso": "peso_volta",
                              "transferencias": "transf_volta"})
    par = a.merge(volta, on=["origem", "destino"])
    par = par[par["origem"] < par["destino"]].assign(soma=lambda x: x["peso"] + x["peso_volta"])
    neg = par[par["soma"] < 0].sort_values("soma")
    return {
        "total": int(len(neg)),
        "mais_negativos": [
            {"clubes": [d.nome(r.origem), d.nome(r.destino)], "ida": int(r.peso),
             "volta": int(r.peso_volta), "soma": int(r.soma)}
            for r in neg.head(n).itertuples()
        ],
    }


def _medir(funcao, repeticoes, memoria=True):
    tempos = []
    gc.disable()
    try:
        for _ in range(repeticoes):
            t0 = time.perf_counter()
            resultado = funcao()
            tempos.append(time.perf_counter() - t0)
    finally:
        gc.enable()
    pico = None
    if memoria:
        tracemalloc.start()
        funcao()
        pico = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
    return tempos, pico, resultado


def benchmark(d: Dataset, tamanhos=TAMANHOS, repeticoes=REPETICOES, semente=SEMENTE, log=print) -> list:
    todos = sorted(set(d.arcos["origem"]) | set(d.arcos["destino"]))
    sorteio = random.Random(semente)
    embaralhados = todos[:]
    sorteio.shuffle(embaralhados)
    desl = deslocamento(d)
    linhas = []
    for pct in tamanhos:
        nos = embaralhados[: round(len(todos) * pct / 100)]
        arcos = subgrafo_induzido(d.arcos, nos)
        g = grafo_de_clubes(arcos)
        g_desl = grafo_de_clubes(arcos, desl)
        fonte = max(g.nos(), key=lambda n: (g.grau_saida(n), -n))
        tarefas = {
            "BFS": ("a partir do clube de maior grau de saída", lambda: bfs(g, fonte)),
            "DFS": ("todos os nós (floresta DFS completa)", lambda: dfs(g)),
            "DIJKSTRA": ("a partir da mesma fonte, pesos deslocados", lambda: dijkstra(g_desl, fonte)),
            "BELLMAN_FORD": ("a partir da mesma fonte, pesos originais", lambda: bellman_ford(g, fonte)),
        }
        for alg, (tarefa, funcao) in tarefas.items():
            # tracemalloc deixa o BF muito lento no grafo grande
            medir_memoria = alg != "BELLMAN_FORD" or g.ordem() * g.tamanho() <= LIMITE_MEMORIA_BF
            tempos, pico, resultado = _medir(funcao, repeticoes, medir_memoria)
            extra = {}
            if alg == "BELLMAN_FORD":
                extra["ciclo_negativo"] = resultado[2] is not None
            linha = {
                "algoritmo": alg, "tarefa": tarefa, "tamanho_pct": pct,
                "V": g.ordem(), "E": g.tamanho(), "fonte": d.nome(fonte),
                "execucoes": repeticoes,
                "media_s": statistics.mean(tempos), "mediana_s": statistics.median(tempos), "desvio_s": statistics.stdev(tempos),
                "min_s": min(tempos), "max_s": max(tempos),
                "memoria_pico_kb": round(pico / 1024, 1) if pico is not None else None, **extra,
            }
            linhas.append(linha)
            log(f"  {pct:>3}%  {alg:<13} |V|={linha['V']:>5} |E|={linha['E']:>6}  "
                f"{linha['media_s'] * 1000:>10.2f} ms ± {linha['desvio_s'] * 1000:.2f}")
    return linhas


def escalabilidade(linhas: list) -> list:
    import math
    teoria = {
        "BFS": ("O(V + E)", lambda v, e: v + e),
        "DFS": ("O(V + E)", lambda v, e: v + e),
        "DIJKSTRA": ("O((V + E) log V)", lambda v, e: (v + e) * math.log2(max(v, 2))),
        "BELLMAN_FORD": ("O(V · E)", lambda v, e: v * e),
    }
    saida = []
    for alg, (notacao, f) in teoria.items():
        serie = [l for l in linhas if l["algoritmo"] == alg]
        base = serie[-1]
        for l in serie:
            saida.append({
                "algoritmo": alg, "complexidade": notacao, "tamanho_pct": l["tamanho_pct"],
                "V": l["V"], "E": l["E"], "media_s": l["media_s"],
                "tempo_relativo": l["media_s"] / base["media_s"],
                "teoria_relativa": f(l["V"], l["E"]) / f(base["V"], base["E"]),
                "ns_por_operacao": l["media_s"] / f(l["V"], l["E"]) * 1e9,
            })
    return saida


def resumo_do_dataset(d: Dataset, gt: Grafo) -> dict:
    a = d.arcos
    v = len(set(a["origem"]) | set(a["destino"]))
    e = len(a)
    return {
        "fonte": "Transfermarkt Datasets (dcaribou), snapshot de 05/09/2026",
        "funil": [{"etapa": n, "linhas": k} for n, k in d.funil],
        "V": v, "E": e, "densidade": e / (v * (v - 1)),
        "arcos_peso_negativo_pct": round(100 * float((a["peso"] < 0).mean()), 2),
        "peso_min": int(a["peso"].min()), "peso_mediana": float(a["peso"].median()),
        "peso_max": int(a["peso"].max()),
        "temporal": {"V": gt.ordem(), "E": gt.tamanho()},
    }


def gerar_relatorio(d: Dataset, saida, tamanhos=TAMANHOS, repeticoes=REPETICOES, log=print) -> Path:
    saida = Path(saida)
    saida.mkdir(parents=True, exist_ok=True)
    g = d.grafo()
    desl = deslocamento(d)
    g_desl = d.grafo(desl)
    gt = grafo_temporal(d.usadas)

    log("BFS e DFS")
    buscas_bfs = [tarefa_bfs(d, g, f) for f in FONTES]
    buscas_dfs = [tarefa_dfs(d, g, f) for f in FONTES]
    log("Dijkstra")
    pares = [tarefa_dijkstra(d, g, g_desl, o, t) for o, t in PARES_DIJKSTRA]
    log("Bellman-Ford (temporal, sem ciclo)")
    bf_sem = tarefa_bf_sem_ciclo(d, gt, FONTE_TEMPORAL)
    log("Bellman-Ford (com ciclo negativo)")
    grau = (d.arcos.groupby("origem").size().add(d.arcos.groupby("destino").size(), fill_value=0)
            .sort_values(ascending=False, kind="stable"))
    grandes = grau.index[:CLUBES_DO_RECORTE].tolist()
    bf_com = [
        tarefa_bf_com_ciclo(d, d.arcos, 418, "grafo de clubes completo"),
        tarefa_bf_com_ciclo(d, subgrafo_induzido(d.arcos, grandes), max(grandes, key=lambda c: grau[c]),
                            f"recorte: os {CLUBES_DO_RECORTE} clubes de maior grau total"),
    ]
    log(f"Desempenho ({repeticoes} execuções por medida)")
    desempenho = benchmark(d, tamanhos, repeticoes, log=log)

    relatorio = {
        "dataset": resumo_do_dataset(d, gt),
        "bfs": buscas_bfs,
        "dfs": buscas_dfs,
        "dijkstra": {
            "transformacao": {
                "formula": "w' = w - min(w)", "deslocamento_eur": desl,
                "motivo": "Dijkstra recusa pesos negativos e 79% dos arcos são negativos; "
                          "o deslocamento torna todo peso >= 0, mas soma a mesma constante "
                          "por arco e por isso favorece caminhos com menos arcos.",
            },
            "pares": pares,
        },
        "bellman_ford": {"sem_ciclo_negativo": bf_sem, "com_ciclo_negativo": bf_com},
        "ciclos_de_comprimento_2": pares_ciclo_2(d),
        "desempenho": desempenho,
        "escalabilidade": escalabilidade(desempenho),
        "parametros": {"tamanhos_pct": list(tamanhos), "repeticoes": repeticoes, "semente": SEMENTE},
    }
    caminho_json = saida / "parte2_report.json"
    caminho_json.write_text(json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame(desempenho).to_csv(saida / "desempenho.csv", index=False)
    return caminho_json
