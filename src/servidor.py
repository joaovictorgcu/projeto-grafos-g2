# [IA] Claude Code (Claude Opus 5.5) – servidor local do labirinto interativo: entrega o frontend React e os dados do grafo de estados em JSON
import argparse
import json
import re
import threading
import webbrowser

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from .graphs.algorithms import bellman_ford, bfs, caminho, dijkstra, estados_armadilha
from .graphs.estados import ALVO, construir_estados, metricas
from .graphs.io import MapaInvalido, interpretar_mapa


RAIZ = Path(__file__).resolve().parent.parent
PASTAS = (("enunciado", RAIZ / "data" / "mapas"), ("grupo", RAIZ / "data" / "mapas_grupo"))
SITE = RAIZ / "frontend" / "dist"
PARTE1 = RAIZ / "out" / "parte1"
PARTE2 = RAIZ / "out" / "parte2"
NOTAS_PARTE1 = RAIZ / "docs" / "parte1" / "notas_visualizacoes.md"
RELATORIO_PARTE2 = RAIZ / "docs" / "parte2" / "relatorio_parte2.md"
NOMES_DOS_MAPAS = {"m01": "Terreno", "m02": "Uma chave", "m03": "Três chaves", "m04": "Esteiras", "m05": "Bônus",
                   "m06": "Fonte", "m07": "Impossível", "m08": "Grande"}
SECAO_PARTE1 = re.compile(r"^## `([^`]+\.png)` \(([^)]*)\)\s*$", re.M)
NOTA = re.compile(r"\*\*([A-Z]\d)\S*\s*\S*\s*`([^`]+)` \(([^)]*)\)\.\*\*(.*?)(?=\n\s*\n|\Z)", re.S)
ROTULO = re.compile(r"^\((\d+),(\d+)\)\|([a-z]+|-)\|\{([\d,]*)\}$")
LIMITE_DO_MAPA = 200_000
TIPOS = {".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml",
         ".woff2": "font/woff2", ".woff": "font/woff", ".png": "image/png", ".ico": "image/x-icon",
         ".json": "application/json"}


def titulo_do_mapa(nome, origem="enunciado"):
    codigo, _, resto = nome.partition("_")
    if origem != "enviado" and codigo in NOMES_DOS_MAPAS:
        return NOMES_DOS_MAPAS[codigo]
    texto = (resto if origem == "grupo" and resto else nome).replace("_", " ")
    return texto[:1].upper() + texto[1:]


# [IA] Claude Code (Claude Opus 5.5) – dados da Parte 2 para o frontend: relatório dos experimentos, figuras e as notas escritas pelo grupo
def dados_da_parte2():
    relatorio = json.loads((PARTE2 / "parte2_report.json").read_text(encoding="utf-8"))
    notas = {}
    if RELATORIO_PARTE2.is_file():
        texto = RELATORIO_PARTE2.read_text(encoding="utf-8")
        for codigo, arquivo, tipo, nota in NOTA.findall(texto):
            notas[arquivo] = {"codigo": codigo, "tipo": tipo, "nota": " ".join(nota.split())}
    figuras = []
    for arquivo in sorted(PARTE2.glob("*.png")):
        info = notas.get(arquivo.name, {"codigo": arquivo.stem.split("_")[0].upper(), "tipo": "", "nota": ""})
        figuras.append({"arquivo": arquivo.name, **info})
    ordem = {"E": 0, "X": 1, "A": 2}
    figuras.sort(key=lambda f: (ordem.get(f["codigo"][:1], 3), f["codigo"]))
    return {"relatorio": relatorio, "figuras": figuras}


# [IA] Claude Code (Claude Opus 5.5) – figuras da Parte 1 para o frontend, com as notas do grupo em docs/parte1/notas_visualizacoes.md
def blocos_da_nota(texto):
    blocos = []
    for trecho in re.split(r"\n\s*\n", texto.strip()):
        linhas = [l.strip() for l in trecho.strip().splitlines()]
        if not linhas:
            continue
        if all(l.startswith("|") for l in linhas):
            celulas = [[c.strip() for c in l.strip("|").split("|")] for l in linhas]
            celulas = [c for c in celulas if not all(re.fullmatch(r":?-+:?", x) for x in c)]
            blocos.append({"tipo": "tabela", "linhas": celulas})
        else:
            blocos.append({"tipo": "paragrafo", "texto": " ".join(linhas)})
    return blocos


def figuras_da_parte1():
    notas = {}
    if NOTAS_PARTE1.is_file():
        texto = NOTAS_PARTE1.read_text(encoding="utf-8")
        cabecalhos = list(SECAO_PARTE1.finditer(texto))
        for i, m in enumerate(cabecalhos):
            fim = cabecalhos[i + 1].start() if i + 1 < len(cabecalhos) else len(texto)
            notas[m.group(1)] = {"tipo": m.group(2), "blocos": blocos_da_nota(texto[m.end():fim])}
    ordem = list(notas)
    figuras = []
    for arquivo in sorted(PARTE1.glob("*.png"), key=lambda a: (ordem.index(a.name) if a.name in ordem else len(ordem), a.name)):
        info = notas.get(arquivo.name, {"tipo": "", "blocos": []})
        figuras.append({"arquivo": arquivo.name, "codigo": f"P{len(figuras) + 1}", **info})
    return figuras


def ler_rotulo(rotulo):
    l, c, chaves, bonus = ROTULO.match(rotulo).groups()
    return int(l), int(c), "" if chaves == "-" else chaves, [int(b) for b in bonus.split(",") if b]


def mapas_do_projeto(extras=()):
    mapas = []
    for origem, pasta in PASTAS:
        for arquivo in sorted(pasta.glob("*.txt")):
            mapas.append((arquivo.stem, origem, arquivo))
    for arquivo in extras:
        if all(arquivo.resolve() != a.resolve() for _, _, a in mapas):
            mapas.append((arquivo.stem, "enviado", arquivo))
    return mapas


def resumo_dos_mapas(mapas):
    lista = []
    for nome, origem, arquivo in mapas:
        try:
            grade = interpretar_mapa(arquivo.read_text(encoding="utf-8"), nome).grade
        except (MapaInvalido, OSError, UnicodeDecodeError):
            grade = []
        lista.append({"id": nome, "titulo": titulo_do_mapa(nome, origem), "origem": origem, "grade": grade})
    return lista


def percurso(grafo, rotulos, indice):
    custos, total = [0], 0
    for u, v in zip(rotulos, rotulos[1:]):
        total += dict(grafo.arcos(u))[v]
        custos.append(total)
    return {"caminho": [indice[r] for r in rotulos], "custos": custos, "passos": len(rotulos) - 1, "custo": total}


def exploracao(dist, indice):
    ordem = sorted((d, n, no) for n, (no, d) in enumerate(dist.items()) if no != ALVO)
    return [[indice[no], d] for d, _, no in ordem]


def resultado(dist, pai, grafo, indice):
    rotulos = caminho(pai, ALVO)
    base = {"exploracao": exploracao(dist, indice)}
    if rotulos is None:
        return {**base, "status": "SEM_SOLUCAO", "motivo": "nenhum estado em G é alcançável a partir do início"}
    return {**base, "status": "OK", **percurso(grafo, rotulos[:-1], indice)}


def rodar_algoritmos(grafo, inicio, indice):
    algoritmos = {}
    dist, pai = bfs(grafo, inicio)
    algoritmos["BFS"] = resultado(dist, pai, grafo, indice)
    try:
        dist, pai = dijkstra(grafo, inicio)
        algoritmos["DIJKSTRA"] = resultado(dist, pai, grafo, indice)
    except ValueError as erro:
        algoritmos["DIJKSTRA"] = {"status": "RECUSA", "motivo": str(erro), "exploracao": []}
    dist, pai, ciclo = bellman_ford(grafo, inicio)
    if ciclo:
        nos, custo = ciclo
        algoritmos["BELLMAN_FORD"] = {
            "status": "CICLO_NEGATIVO", "exploracao": [],
            "motivo": f"ciclo negativo de custo {custo}: não existe caminho de menor custo",
            "ciclo": {"estados": [indice[n] for n in nos], "custo": custo},
        }
    else:
        algoritmos["BELLMAN_FORD"] = resultado(dist, pai, grafo, indice)
    return algoritmos


def analisar(texto, nome, fonte_consumivel=False, origem="enviado"):
    mapa = interpretar_mapa(texto, nome)
    construido = construir_estados(mapa, fonte_consumivel)
    grafo = construido.grafo
    nos = [n for n in grafo.nos() if n != ALVO]
    indice = {n: i for i, n in enumerate(nos)}
    armadilhas = set(estados_armadilha(grafo, ALVO))
    estados = []
    for n in nos:
        l, c, chaves, bonus = ler_rotulo(n)
        estados.append({"rotulo": n, "l": l, "c": c, "chaves": chaves, "bonus": bonus, "armadilha": n in armadilhas,
                        "saida": mapa.casa(l, c) == "G"})
    return {
        "id": nome,
        "titulo": titulo_do_mapa(nome, origem),
        "origem": origem,
        "fonte_consumivel": fonte_consumivel,
        "grade": mapa.grade,
        "chaves": sorted(mapa.chaves),
        "bonus": [[l, c, i] for (l, c), i in sorted(mapa.bonus.items(), key=lambda par: par[1])],
        "inicial": indice[construido.inicial],
        "estados": estados,
        "arcos": [[indice[u], indice[v], p] for u in nos for v, p in grafo.arcos(u) if v != ALVO],
        "metricas": metricas(construido),
        "algoritmos": rodar_algoritmos(grafo, construido.inicial, indice),
    }


class Servidor(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, endereco, mapas):
        super().__init__(endereco, Atendente)
        self.mapas = mapas


class Atendente(BaseHTTPRequestHandler):
    def log_message(self, formato, *args):
        pass

    def responder(self, codigo, corpo, tipo="application/json"):
        dados = corpo if isinstance(corpo, bytes) else json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", f"{tipo}; charset=utf-8" if tipo.startswith("text") or "json" in tipo else tipo)
        self.send_header("Content-Length", str(len(dados)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(dados)

    def do_GET(self):
        url = urlparse(self.path)
        fonte = parse_qs(url.query).get("fonte", ["0"])[0] == "1"
        if url.path == "/api/mapas":
            return self.responder(200, resumo_dos_mapas(self.server.mapas))
        if url.path == "/api/parte2":
            if not (PARTE2 / "parte2_report.json").is_file():
                return self.responder(404, {"erro": "falta o out/parte2/parte2_report.json (rode o --benchmark)"})
            return self.responder(200, dados_da_parte2())
        if url.path == "/api/parte1/figuras":
            return self.responder(200, figuras_da_parte1())
        if url.path.startswith(("/parte1/", "/parte2/")):
            arquivo = (PARTE1 if url.path.startswith("/parte1/") else PARTE2) / Path(unquote(url.path)).name
            if arquivo.suffix == ".png" and arquivo.is_file():
                return self.responder(200, arquivo.read_bytes(), "image/png")
            return self.responder(404, {"erro": "figura não encontrada"})
        if url.path.startswith("/api/mapas/"):
            nome = unquote(url.path.removeprefix("/api/mapas/"))
            for id_, origem, arquivo in self.server.mapas:
                if id_ == nome:
                    try:
                        return self.responder(200, analisar(arquivo.read_text(encoding="utf-8"), id_, fonte, origem))
                    except MapaInvalido as erro:
                        return self.responder(400, {"erro": str(erro)})
            return self.responder(404, {"erro": f"mapa {nome!r} não encontrado"})
        self.entregar_arquivo(url.path)

    def do_POST(self):
        url = urlparse(self.path)
        if url.path != "/api/analisar":
            return self.responder(404, {"erro": "rota inexistente"})
        tamanho = int(self.headers.get("Content-Length") or 0)
        if tamanho > LIMITE_DO_MAPA:
            return self.responder(413, {"erro": "arquivo grande demais para um mapa"})
        consulta = parse_qs(url.query)
        nome = consulta.get("nome", ["enviado"])[0] or "enviado"
        fonte = consulta.get("fonte", ["0"])[0] == "1"
        try:
            texto = self.rfile.read(tamanho).decode("utf-8")
        except UnicodeDecodeError:
            return self.responder(400, {"erro": f"{nome}: o arquivo não está em UTF-8"})
        try:
            return self.responder(200, analisar(texto, nome, fonte))
        except MapaInvalido as erro:
            return self.responder(400, {"erro": str(erro)})

    def entregar_arquivo(self, caminho_pedido):
        if not (SITE / "index.html").is_file():
            aviso = "<h1>Frontend não compilado</h1><p>Rode <code>npm install</code> e <code>npm run build</code> em frontend/.</p>"
            return self.responder(503, aviso.encode("utf-8"), "text/html")
        alvo = (SITE / unquote(caminho_pedido).lstrip("/")).resolve()
        if not alvo.is_file() or SITE.resolve() not in alvo.parents:
            alvo = SITE / "index.html"
        self.responder(200, alvo.read_bytes(), TIPOS.get(alvo.suffix, "application/octet-stream"))


def main(argv=None):
    p = argparse.ArgumentParser(description="Abre o labirinto interativo no navegador.")
    p.add_argument("--mapa", help="mapa .txt para abrir direto (pode ser um mapa novo, como o surpresa)")
    p.add_argument("--porta", type=int, default=8000)
    p.add_argument("--sem-navegador", action="store_true", help="não abre o navegador sozinho")
    args = p.parse_args(argv)
    extras = [Path(args.mapa)] if args.mapa else []
    servidor = Servidor(("127.0.0.1", args.porta), mapas_do_projeto(extras))
    endereco = f"http://127.0.0.1:{args.porta}/"
    if args.mapa:
        endereco += f"?mapa={quote(Path(args.mapa).stem)}"
    print(f"Labirinto interativo em {endereco}  (Ctrl+C para fechar)")
    if not args.sem_navegador:
        threading.Timer(0.6, webbrowser.open, [endereco]).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
