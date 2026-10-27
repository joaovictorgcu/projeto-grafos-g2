"""Parte 1 pelo CLI (--mapa): roda um algoritmo sobre o grafo de estados de qualquer mapa .txt.

    python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --alg BFS --out ./out/parte1/
    python -m src.cli --mapa ./data/mapas/m06_fonte.txt --alg BELLMAN_FORD --fonte-consumivel --out ./out/parte1/
    python -m src.cli --mapa ./data/mapas/m04_esteiras.txt --armadilhas --out ./out/parte1/
    python -m src.cli --mapa ./data/mapas/m03_tres_chaves.txt --interactive
"""
# — [IA] Claude – despacho do --mapa (algoritmos, armadilhas, interativo) gerado pela IA; testado e integrado por mim
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

from .graphs.algorithms import bellman_ford, bfs, caminho, dfs, dijkstra, estados_armadilha
from .graphs.estados import ALVO, construir_estados, nome_curto
from .graphs.io import MapaInvalido, ler_mapa

TIPOS_DE_ARCO = ("arvore", "retorno", "avanco", "cruzamento")
ROTULO = re.compile(r"\((\d+),(\d+)\)\|([^|]*)\|\{(.*)\}")


def custo_do_caminho(grafo, rotulos):
    return sum(min(p for v, p in grafo.arcos(u) if v == w) for u, w in zip(rotulos, rotulos[1:]))


def resolver(alg, construido):
    """Roda o algoritmo no grafo de estados. Retorna (resultado, arcos_classificados)."""
    g, inicio = construido.grafo, construido.inicial
    if alg == "DFS":
        tipo, _, _, tem_ciclo = dfs(g, [inicio])
        contagem = {t: sum(1 for x in tipo.values() if x == t) for t in TIPOS_DE_ARCO}
        return {"status": "OK", "tem_ciclo": tem_ciclo, "classificacao": contagem}, tipo

    if alg == "BFS":
        _, pai = bfs(g, inicio)
    elif alg == "DIJKSTRA":
        try:
            _, pai = dijkstra(g, inicio)
        except ValueError as erro:
            return {"status": "RECUSA", "motivo": str(erro)}, None
    else:
        _, pai, ciclo = bellman_ford(g, inicio)
        if ciclo:
            nos, custo = ciclo
            return {
                "status": "CICLO_NEGATIVO",
                "motivo": f"ciclo negativo de custo {custo}: não existe caminho de menor custo",
                "ciclo": nos,
                "custo_do_ciclo": custo,
            }, None

    rotulos = caminho(pai, ALVO)
    if rotulos is None:
        return {"status": "SEM_SOLUCAO", "motivo": "nenhum estado com G é alcançável a partir do início"}, None
    rotulos = rotulos[:-1]  # tira o ALVO
    return {
        "status": "OK",
        "passos": len(rotulos) - 1,
        "custo": custo_do_caminho(g, rotulos),
        "caminho": rotulos,
    }, None


def gravar_armadilhas(construido, destino):
    armadilhas = estados_armadilha(construido.grafo, ALVO)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["estado", "linha", "coluna", "chaves", "bonus"])
        for rotulo in armadilhas:
            linha, coluna, chaves, bonus = ROTULO.fullmatch(rotulo).groups()
            escritor.writerow([rotulo, linha, coluna, chaves, bonus])
    return len(armadilhas)


def gravar_classificacao(tipo, destino):
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["origem", "destino", "tipo"])
        for (u, v), t in tipo.items():
            escritor.writerow([u, v, t])


def abrir_interativo(mapa):
    raiz = Path(__file__).resolve().parent
    comando = [sys.executable, "-m", "streamlit", "run", str(raiz / "interativo.py"), "--", "--mapa", str(mapa)]
    return subprocess.run(comando).returncode


def executar(args):
    """Ponto de entrada chamado pelo src/cli.py. Devolve o código de saída."""
    if not (args.alg or args.armadilhas or args.interactive):
        print("erro: com --mapa, use --alg, --armadilhas ou --interactive.", file=sys.stderr)
        return 2
    try:
        mapa = ler_mapa(args.mapa)
    except (MapaInvalido, OSError, UnicodeDecodeError) as erro:
        print(f"erro: não foi possível ler o mapa {args.mapa}: {erro}", file=sys.stderr)
        return 2

    if args.interactive:
        return abrir_interativo(args.mapa)

    nome = nome_curto(args.mapa)
    saida = Path(args.out or "out/parte1")
    construido = construir_estados(mapa, args.fonte_consumivel)

    if args.armadilhas:
        destino = saida / f"armadilhas_{nome}.csv"
        n = gravar_armadilhas(construido, destino)
        print(f"{n} estados-armadilha em {nome} (gravado em {destino})")

    if args.alg:
        resultado, tipo = resolver(args.alg, construido)
        resultado = {"mapa": nome, "algoritmo": args.alg, "fonte_consumivel": args.fonte_consumivel, **resultado}
        texto = json.dumps(resultado, indent=2, ensure_ascii=False)
        print(texto)
        saida.mkdir(parents=True, exist_ok=True)
        destino = saida / f"{args.alg.lower()}_{nome}.json"
        destino.write_text(texto, encoding="utf-8")
        if tipo is not None:
            gravar_classificacao(tipo, saida / f"dfs_classificacao_{nome}.csv")
        print(f"\ngravado em {destino}", file=sys.stderr)
    return 0