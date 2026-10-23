"""Linha de comando do projeto. --mapa vai para o src/solve.py (Parte 1); --dataset roda a Parte 2.

    python -m src.cli --dataset ./data/dataset_parte2/ --alg DIJKSTRA --source Santos --target PSG --out ./out/parte2/
    python -m src.cli --dataset ./data/dataset_parte2/ --benchmark --out ./out/parte2/
"""
import argparse
import json
import sys
from pathlib import Path

ALGORITMOS = ("BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD")


def montar_parser():
    p = argparse.ArgumentParser(prog="python -m src.cli", description="Projeto Final de Grafos — Grupo 2")
    entrada = p.add_mutually_exclusive_group(required=True)
    entrada.add_argument("--mapa", help="Parte 1: arquivo .txt do labirinto")
    entrada.add_argument("--dataset", help="Parte 2: pasta com o snapshot do Transfermarkt")
    p.add_argument("--alg", type=str.upper, choices=ALGORITMOS)
    p.add_argument("--out", default=None, help="pasta de saída")
    p.add_argument("--fonte-consumivel", action="store_true")
    p.add_argument("--armadilhas", action="store_true")
    p.add_argument("--interactive", action="store_true")
    p.add_argument("--source", help="clube de origem (nome ou id)")
    p.add_argument("--target", help="clube de destino (nome ou id)")
    p.add_argument("--benchmark", action="store_true", help="roda todos os experimentos e grava o parte2_report.json")
    p.add_argument("--repeticoes", type=int, default=5, help="execuções por medida de tempo (mínimo 5 no enunciado)")
    p.add_argument("--tamanhos", default="10,25,50,75,100", help="tamanhos do grafo, em %% dos nós")
    return p


def parte2(args, p):
    from . import parte2 as exp
    from .graphs.dataset import DatasetInvalido, carregar_dataset

    saida = Path(args.out or "out/parte2")
    try:
        d = carregar_dataset(args.dataset)
    except DatasetInvalido as erro:
        p.error(str(erro))

    if args.benchmark:
        tamanhos = tuple(int(x) for x in args.tamanhos.split(","))
        caminho = exp.gerar_relatorio(d, saida, tamanhos, args.repeticoes)
        print(f"relatório gravado em {caminho}")
        return 0

    if not args.alg or not args.source:
        p.error("na Parte 2, use --benchmark ou --alg com --source (e --target no DIJKSTRA)")
    try:
        origem = exp.resolver_clube(d, args.source)
        destino = exp.resolver_clube(d, args.target) if args.target else None
    except ValueError as erro:
        p.error(str(erro))

    g = d.grafo()
    if args.alg == "BFS":
        resultado = exp.tarefa_bfs(d, g, origem)
    elif args.alg == "DFS":
        resultado = exp.tarefa_dfs(d, g, origem)
    elif args.alg == "DIJKSTRA":
        if destino is None:
            p.error("o DIJKSTRA precisa de --target")
        resultado = exp.tarefa_dijkstra(d, g, d.grafo(exp.deslocamento(d)), origem, destino)
        resultado["transformacao"] = f"w' = w - min(w) = w + {exp.deslocamento(d):,} EUR".replace(",", ".")
    else:
        resultado = exp.tarefa_bf_com_ciclo(d, d.arcos, origem, "grafo de clubes completo")
        resultado["status"] = "CICLO_NEGATIVO" if resultado["ciclo_negativo"] else "OK"

    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    print(texto)
    saida.mkdir(parents=True, exist_ok=True)
    nome = f"{args.alg.lower()}_{origem}" + (f"_{destino}" if destino is not None else "") + ".json"
    (saida / nome).write_text(texto, encoding="utf-8")
    print(f"\ngravado em {saida / nome}", file=sys.stderr)
    return 0


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = montar_parser()
    args = p.parse_args(argv)
    if args.dataset:
        return parte2(args, p)
    try:
        from . import solve
    except ImportError:
        p.error("a Parte 1 ainda não está ligada ao cli: falta o src/solve.py")
    return solve.executar(args)


if __name__ == "__main__":
    sys.exit(main())
