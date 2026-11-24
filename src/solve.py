"""Execução de mapas pela interface de linha de comando (Parte 1)."""

import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

from .graphs.algorithms import bellman_ford, bfs, caminho, dfs, dijkstra, estados_armadilha
from .graphs.estados import ALVO, construir_estados, nome_curto
from .graphs.io import MapaInvalido, ler_mapa


ALGORITMOS_DE_CAMINHO = {
    "BFS": bfs,
    "DIJKSTRA": dijkstra,
    "BELLMAN_FORD": bellman_ford,
}
TIPOS_DFS = ("arvore", "retorno", "avanco", "cruzamento")


class Saidas:
    """Gerencia os arquivos de saída sem depender do algoritmo executado."""

    def __init__(self, pasta, identificador):
        self.pasta = Path(pasta or "out/parte1")
        self.identificador = identificador

    def gravar_csv(self, nome, colunas, registros):
        arquivo = self.pasta / nome
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        with arquivo.open("w", encoding="utf-8", newline="") as destino:
            tabela = csv.writer(destino)
            tabela.writerow(colunas)
            tabela.writerows(registros)
        return arquivo

    def gravar_resultado(self, algoritmo, dados):
        arquivo = self.pasta / f"{algoritmo.lower()}_{self.identificador}.json"
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        conteudo = json.dumps(dados, indent=2, ensure_ascii=False)
        arquivo.write_text(conteudo, encoding="utf-8")
        print(conteudo)
        print(f"\ngravado em {arquivo}", file=sys.stderr)


class AnaliseDeMapa:
    """Executa operações opcionais sobre um único grafo de estados."""

    def __init__(self, mapa, argumentos):
        self.argumentos = argumentos
        self.construido = construir_estados(mapa, argumentos.fonte_consumivel)
        self.saidas = Saidas(argumentos.out, nome_curto(argumentos.mapa))

    def salvar_armadilhas(self):
        lista = estados_armadilha(self.construido.grafo, ALVO)
        registros = []
        for estado in lista:
            coordenadas, chaves, bonus = estado.split("|", 2)
            linha, coluna = coordenadas[1:-1].split(",")
            registros.append((estado, linha, coluna, chaves, bonus[1:-1]))

        arquivo = self.saidas.gravar_csv(
            f"armadilhas_{self.saidas.identificador}.csv",
            ("estado", "linha", "coluna", "chaves", "bonus"),
            registros,
        )
        print(f"{len(lista)} estados-armadilha em {self.saidas.identificador} (gravado em {arquivo})")

    def _classificar_dfs(self):
        classificacao, _, _, possui_ciclo = dfs(
            self.construido.grafo, [self.construido.inicial]
        )
        contagem = Counter(classificacao.values())
        self.saidas.gravar_csv(
            f"dfs_classificacao_{self.saidas.identificador}.csv",
            ("origem", "destino", "tipo"),
            ((u, v, classe) for (u, v), classe in classificacao.items()),
        )
        return {
            "status": "OK",
            "tem_ciclo": possui_ciclo,
            "classificacao": {tipo: contagem[tipo] for tipo in TIPOS_DFS},
        }

    def _buscar_caminho(self, algoritmo):
        grafo = self.construido.grafo
        ponto_inicial = self.construido.inicial
        executar_busca = ALGORITMOS_DE_CAMINHO[algoritmo]

        try:
            retorno = executar_busca(grafo, ponto_inicial)
        except ValueError as erro:
            if algoritmo != "DIJKSTRA":
                raise
            return {"status": "RECUSA", "motivo": str(erro)}

        if algoritmo == "BELLMAN_FORD":
            _, pais, ciclo = retorno
            if ciclo:
                estados, custo = ciclo
                return {
                    "status": "CICLO_NEGATIVO",
                    "motivo": f"Existe um ciclo de custo {custo}; o custo pode diminuir indefinidamente.",
                    "ciclo": estados,
                    "custo_do_ciclo": custo,
                }
        else:
            _, pais = retorno

        percurso = caminho(pais, ALVO)
        if percurso is None:
            return {
                "status": "SEM_SOLUCAO",
                "motivo": "Não há percurso alcançável entre S e uma saída G.",
            }

        # O último arco chega a um nó auxiliar, que não corresponde a um passo.
        percurso = percurso[:-1]
        custo_total = 0
        for anterior, posterior in zip(percurso, percurso[1:]):
            pesos = [p for v, p in grafo.arcos(anterior) if v == posterior]
            custo_total += min(pesos)

        return {
            "status": "OK",
            "passos": len(percurso) - 1,
            "custo": custo_total,
            "caminho": percurso,
        }

    def salvar_algoritmo(self, algoritmo):
        resultado = (
            self._classificar_dfs()
            if algoritmo == "DFS"
            else self._buscar_caminho(algoritmo)
        )
        dados = {
            "mapa": self.saidas.identificador,
            "algoritmo": algoritmo,
            "fonte_consumivel": self.argumentos.fonte_consumivel,
            **resultado,
        }
        self.saidas.gravar_resultado(algoritmo, dados)


def executar(args):
    """Entrada de src.cli: devolve 0 para sucesso ou 2 para erro de entrada."""
    algoritmo = str(args.alg).upper().replace("-", "_") if args.alg else None

    if not (algoritmo or args.armadilhas or args.interactive):
        print("erro: informe --alg, --armadilhas ou --interactive para usar --mapa.", file=sys.stderr)
        return 2

    if algoritmo and algoritmo not in (*ALGORITMOS_DE_CAMINHO, "DFS"):
        print(f"erro: algoritmo não reconhecido: {algoritmo}", file=sys.stderr)
        return 2

    try:
        mapa = ler_mapa(args.mapa)
    except (MapaInvalido, OSError, UnicodeError) as erro:
        print(f"erro ao abrir o mapa {args.mapa}: {erro}", file=sys.stderr)
        return 2

    if args.interactive:
        comando = [sys.executable, "-m", "src.servidor", "--mapa", str(Path(args.mapa).resolve())]
        return subprocess.run(comando).returncode

    operacao = AnaliseDeMapa(mapa, args)
    if args.armadilhas:
        operacao.salvar_armadilhas()
    if algoritmo:
        operacao.salvar_algoritmo(algoritmo)
    return 0
