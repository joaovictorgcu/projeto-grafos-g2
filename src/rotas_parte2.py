# [IA] Claude Code (Claude Opus 5.5) – grafo interativo da Visão geral da Parte 2: o usuário escolhe o grafo, a origem, o destino e o algoritmo, e o site roda os algoritmos do src/graphs/algorithms.py (sem mudar nada neles)
"""Rotas da Parte 2 calculadas na hora, para o site (src/servidor.py)."""
import threading
import time
from collections import defaultdict
from pathlib import Path

from .graphs.algorithms import bellman_ford, bfs, caminho, dfs, dijkstra
from .graphs.dataset import carregar_dataset, grafo_temporal
from .parte2 import deslocamento, johnson, peso_original, transferencias_do_arco

PASTA = Path(__file__).resolve().parent.parent / "data" / "dataset_parte2"
CLUBES_DO_CONTEXTO = 20
ALGORITMOS = ("BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD")
GRAFOS = ("clubes", "temporal")


class PedidoInvalido(ValueError):
    pass


def pai_da_dfs(tipo, origem):
    pai = {origem: None}
    for (u, v), t in tipo.items():
        if t == "arvore":
            pai[v] = u
    return pai


def temporada(s):
    return f"{s % 100:02d}/{(s + 1) % 100:02d}"


class GrafoDaParte2:
    def __init__(self, pasta=PASTA):
        self.d = carregar_dataset(pasta)
        self.g = self.d.grafo()
        self.desl = deslocamento(self.d)
        self.g_desl = self.d.grafo(self.desl)
        self.gt = grafo_temporal(self.d.usadas)
        self._johnson = None
        self._bf = {}
        self._trava = threading.Lock()

        a = self.d.arcos
        grau = (a.groupby("origem").size().add(a.groupby("destino").size(), fill_value=0)
                .sort_values(ascending=False, kind="stable"))
        self.grau = {int(c): int(n) for c, n in grau.items()}
        self.temporadas = defaultdict(list)
        for c, s in self.gt.nos():
            self.temporadas[int(c)].append(int(s))
        for lista in self.temporadas.values():
            lista.sort()
        topo = [int(c) for c in grau.index[:CLUBES_DO_CONTEXTO]]
        dentro = set(topo)
        self.contexto = {
            "nos": [{"id": c, "nome": self.d.nome(c)} for c in topo],
            "arcos": [[int(u), int(v), int(p)] for u, v, p in zip(a["origem"], a["destino"], a["peso"])
                      if u in dentro and v in dentro],
        }

    def clubes(self):
        return [{"id": c, "nome": self.d.nome(c), "grau": n, "temporadas": self.temporadas.get(c, [])}
                for c, n in self.grau.items()]

    def resumo(self):
        return {"clubes": self.clubes(), "contexto": self.contexto, "deslocamento": self.desl,
                "padrao": {"clubes": {"origem": 221, "destino": 583},
                           "temporal": {"origem": 294, "temporada": 2015, "destino": 989}}}

    # ------------------------------------------------------------------ pedidos
    def rota(self, grafo, algoritmo, origem, destino, temporada_inicial=None):
        if grafo not in GRAFOS:
            raise PedidoInvalido(f"grafo deve ser um de {', '.join(GRAFOS)}.")
        if algoritmo not in ALGORITMOS:
            raise PedidoInvalido(f"algoritmo deve ser um de {', '.join(ALGORITMOS)}.")
        for c in (origem, destino):
            if c not in self.grau:
                raise PedidoInvalido(f"não existe clube com id {c} no grafo.")
        if origem == destino:
            raise PedidoInvalido("escolha clubes diferentes para a origem e o destino.")
        t0 = time.perf_counter()
        if grafo == "clubes":
            r = self._rota_clubes(algoritmo, origem, destino)
        else:
            if temporada_inicial not in self.temporadas[origem]:
                raise PedidoInvalido(f"{self.d.nome(origem)} não tem nó na temporada pedida.")
            r = self._rota_temporal(algoritmo, (origem, temporada_inicial), destino)
        r.update({"grafo": grafo, "algoritmo": algoritmo})
        r.setdefault("segundos", round(time.perf_counter() - t0, 3))
        return r

    def _bellman_ford(self, grafo, chave, fonte):
        """Guarda o resultado por origem: no grafo de clubes o Bellman-Ford leva mais de um minuto."""
        with self._trava:
            guardado = chave in self._bf
            if not guardado:
                t0 = time.perf_counter()
                self._bf[chave] = (bellman_ford(grafo, fonte), round(time.perf_counter() - t0, 3))
            resultado, segundos = self._bf[chave]
            return resultado, {"segundos": segundos, "guardado": guardado}

    def _rota_clubes(self, alg, o, t):
        g = self.g
        if alg == "BFS":
            dist, pai = bfs(g, o)
        elif alg == "DFS":
            tipo, desc, _, _ = dfs(g, [o])
            pai, dist = pai_da_dfs(tipo, o), desc
        elif alg == "DIJKSTRA":
            dist, pai = dijkstra(self.g_desl, o)
        else:
            (dist, pai, ciclo), tempo = self._bellman_ford(g, ("clubes", o), o)
            if ciclo is not None:
                nos, custo = ciclo
                return {"status": "CICLO_NEGATIVO", "alcancados": len(dist),
                        "ciclo": self._descrever(g, nos, custo), **tempo}
        rota = caminho(pai, t)
        if rota is None:
            return {"status": "SEM_CAMINHO", "alcancados": len(dist), **(tempo if alg == "BELLMAN_FORD" else {})}
        r = {"status": "OK", "alcancados": len(dist), **self._descrever(g, rota, peso_original(g, rota))}
        if alg == "BELLMAN_FORD":
            r.update(tempo)
        if alg == "DIJKSTRA":
            r["custo_deslocado"] = dist[t]
        return r

    def _rota_temporal(self, alg, fonte, t):
        gt = self.gt
        alvos = [(t, s) for s in self.temporadas[t]]
        if alg == "BFS":
            dist, pai = bfs(gt, fonte)
            chave = lambda v: (dist[v], v[1])
        elif alg == "DFS":
            tipo, desc, _, _ = dfs(gt, [fonte])
            pai, dist = pai_da_dfs(tipo, fonte), desc
            chave = lambda v: desc[v]
        elif alg == "DIJKSTRA":
            with self._trava:
                if self._johnson is None:
                    self._johnson = johnson(gt)
            repesado, h = self._johnson
            dist_j, pai = dijkstra(repesado, fonte)
            dist = {v: c - h[fonte] + h[v] for v, c in dist_j.items()}
            chave = lambda v: (dist[v], v[1])
        else:
            (dist, pai, _), _ = self._bellman_ford(gt, ("temporal", fonte), fonte)
            chave = lambda v: (dist[v], v[1])
        alcancados = [v for v in alvos if v in dist]
        if not alcancados:
            return {"status": "SEM_CAMINHO", "alcancados": len(dist)}
        alvo = min(alcancados, key=chave)
        rota = caminho(pai, alvo)
        return {"status": "OK", "alcancados": len(dist), **self._descrever(gt, rota, peso_original(gt, rota))}

    def _descrever(self, g, nos, custo):
        temporal = isinstance(nos[0], tuple)
        caminho_json = [{"id": int(v[0] if temporal else v), "nome": self.d.nome(v[0] if temporal else v),
                         "temporada": temporada(int(v[1])) if temporal else None} for v in nos]
        trechos = []
        for u, v in zip(nos, nos[1:]):
            espera = temporal and u[0] == v[0]
            trechos.append({
                "de": self.d.nome(u[0] if temporal else u), "para": self.d.nome(v[0] if temporal else v),
                "peso": int(next(p for w, p in g.arcos(u) if w == v)),
                "temporada": temporada(int(u[1])) if temporal else None,
                "espera": espera,
                "transferencias": [] if espera else transferencias_do_arco(self.d, u, v),
            })
        return {"custo": int(custo), "arcos": len(nos) - 1,
                "transferencias_no_caminho": sum(1 for t in trechos if not t["espera"]),
                "caminho": caminho_json, "trechos": trechos}


class CarregadorDaParte2:
    """Carrega o dataset uma vez só, numa thread, para o site abrir sem esperar."""

    def __init__(self, pasta=PASTA):
        self.pasta = Path(pasta)
        self._grafo = None
        self._erro = None
        self._pronto = threading.Event()
        self._iniciado = False
        self._trava = threading.Lock()

    def iniciar(self):
        with self._trava:
            if self._iniciado:
                return
            self._iniciado = True
        threading.Thread(target=self._carregar, daemon=True).start()

    def _carregar(self):
        try:
            self._grafo = GrafoDaParte2(self.pasta)
        except Exception as e:  # dataset ausente ou inválido: o site mostra a mensagem
            self._erro = str(e)
        finally:
            self._pronto.set()

    def obter(self):
        self.iniciar()
        self._pronto.wait()
        if self._erro:
            raise FileNotFoundError(self._erro)
        return self._grafo
