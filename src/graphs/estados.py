# [IA] Claude Code (Claude Opus 5.5) – grafo de posições e grafo de estados, construído por exploração a partir do início
import argparse
import csv
from collections import deque
from dataclasses import dataclass
from pathlib import Path

from .graph import Grafo
from .io import CHAVES, ESTEIRAS, PAREDE, PORTAS, Mapa, ler_mapa

ALVO = "ALVO"
DIRECOES = (("N", -1, 0), ("L", 0, 1), ("S", 1, 0), ("O", 0, -1))
DIRECAO_DA_ESTEIRA = {"^": "N", ">": "L", "v": "S", "<": "O"}
CUSTO = {",": 3, "~": 5, "*": -2}
VALOR_DO_BONUS = -4


@dataclass(frozen=True)
class Estado:
    linha: int
    coluna: int
    chaves: frozenset = frozenset()
    bonus: frozenset = frozenset()


@dataclass(frozen=True)
class ArcoDetalhado:
    origem: str
    destino: str
    movimento: str
    casa_destino: str
    peso: int


@dataclass
class GrafoConstruido:
    grafo: Grafo
    arcos: list
    inicial: str


def rotulo(estado: Estado) -> str:
    chaves = "".join(sorted(estado.chaves)) or "-"
    bonus = ",".join(str(b) for b in sorted(estado.bonus))
    return f"({estado.linha},{estado.coluna})|{chaves}|{{{bonus}}}"


def direcoes_permitidas(mapa: Mapa, l: int, c: int):
    casa = mapa.casa(l, c)
    if casa in ESTEIRAS:
        return [d for d in DIRECOES if d[0] == DIRECAO_DA_ESTEIRA[casa]]
    return DIRECOES


def custo_e_bonus(mapa: Mapa, pos, casa: str, bonus: frozenset, fonte_consumivel: bool):
    if casa == "+":
        indice, valor = mapa.bonus[pos], VALOR_DO_BONUS
    elif casa == "*" and fonte_consumivel:
        indice, valor = len(mapa.bonus) + mapa.fontes.index(pos), CUSTO["*"]
    else:
        return CUSTO.get(casa, 1), bonus
    if indice in bonus:
        return 1, bonus
    return valor, bonus | {indice}


def sucessores(mapa: Mapa, estado: Estado, fonte_consumivel: bool = False):
    l, c = estado.linha, estado.coluna
    if mapa.casa(l, c) == "G":
        return
    for movimento, dl, dc in direcoes_permitidas(mapa, l, c):
        nl, nc = l + dl, c + dc
        if not mapa.dentro(nl, nc):
            continue
        casa = mapa.casa(nl, nc)
        if casa == PAREDE:
            continue
        if casa in PORTAS and casa.lower() not in estado.chaves:
            continue
        chaves = estado.chaves | {casa} if casa in CHAVES else estado.chaves
        peso, bonus = custo_e_bonus(mapa, (nl, nc), casa, estado.bonus, fonte_consumivel)
        yield movimento, Estado(nl, nc, chaves, bonus), peso, casa


def construir_estados(mapa: Mapa, fonte_consumivel: bool = False) -> GrafoConstruido:
    inicial = Estado(*mapa.inicio)
    grafo = Grafo()
    grafo.adicionar_no(rotulo(inicial))
    arcos = []
    vistos = {inicial}
    fila = deque([inicial])

    while fila:
        estado = fila.popleft()
        origem = rotulo(estado)
        if mapa.casa(estado.linha, estado.coluna) == "G":
            grafo.adicionar_arco(origem, ALVO, 0)
            arcos.append(ArcoDetalhado(origem, ALVO, "-", "-", 0))
            continue
        for movimento, proximo, peso, casa in sucessores(mapa, estado, fonte_consumivel):
            destino = rotulo(proximo)
            grafo.adicionar_arco(origem, destino, peso)
            arcos.append(ArcoDetalhado(origem, destino, movimento, casa, peso))
            if proximo not in vistos:
                vistos.add(proximo)
                fila.append(proximo)

    grafo.adicionar_no(ALVO)
    return GrafoConstruido(grafo, arcos, rotulo(inicial))


def construir_posicoes(mapa: Mapa, portas: str = "chao") -> GrafoConstruido:
    if portas not in ("chao", "parede"):
        raise ValueError(f"portas deve ser 'chao' ou 'parede', não {portas!r}")

    def livre(l, c):
        casa = mapa.casa(l, c)
        return casa != PAREDE and not (portas == "parede" and casa in PORTAS)

    casas = [(l, c) for l in range(mapa.altura) for c in range(mapa.largura) if livre(l, c)]
    grafo = Grafo()
    for l, c in casas:
        grafo.adicionar_no(f"({l},{c})")
    arcos = []

    for l, c in casas:
        origem = f"({l},{c})"
        if mapa.casa(l, c) == "G":
            grafo.adicionar_arco(origem, ALVO, 0)
            arcos.append(ArcoDetalhado(origem, ALVO, "-", "-", 0))
            continue
        for movimento, dl, dc in direcoes_permitidas(mapa, l, c):
            nl, nc = l + dl, c + dc
            if not (mapa.dentro(nl, nc) and livre(nl, nc)):
                continue
            casa = mapa.casa(nl, nc)
            peso = VALOR_DO_BONUS if casa == "+" else CUSTO.get(casa, 1)
            destino = f"({nl},{nc})"
            grafo.adicionar_arco(origem, destino, peso)
            arcos.append(ArcoDetalhado(origem, destino, movimento, casa, peso))

    grafo.adicionar_no(ALVO)
    return GrafoConstruido(grafo, arcos, "({},{})".format(*mapa.inicio))


def escrever_arestas_csv(arcos, caminho) -> Path:
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["origem", "destino", "movimento", "casa_destino", "peso"])
        for a in arcos:
            escritor.writerow([a.origem, a.destino, a.movimento, a.casa_destino, a.peso])
    return caminho


# [IA] Claude Code (Claude Opus 5.5) – métricas sem o ALVO e exportação do arestas_<mapa>.csv de todos os mapas
def metricas(construido: GrafoConstruido) -> dict:
    nos = [n for n in construido.grafo.nos() if n != ALVO]
    tamanho = sum(1 for n in nos for v, _ in construido.grafo.arcos(n) if v != ALVO)
    ordem = len(nos)
    densidade = tamanho / (ordem * (ordem - 1)) if ordem >= 2 else 0.0
    return {"ordem": ordem, "tamanho": tamanho, "densidade": densidade}


def nome_curto(arquivo) -> str:
    return Path(arquivo).stem.split("_")[0]


def exportar_arestas(pastas, saida) -> list:
    gerados = []
    for pasta in pastas:
        for arquivo in sorted(Path(pasta).glob("*.txt")):
            construido = construir_estados(ler_mapa(arquivo))
            destino = Path(saida) / f"arestas_{nome_curto(arquivo)}.csv"
            gerados.append(escrever_arestas_csv(construido.arcos, destino))
    return gerados


def main(argv=None):
    p = argparse.ArgumentParser(description="Gera o arestas_<mapa>.csv de todos os mapas fornecidos e do grupo.")
    p.add_argument("--out", default="out/parte1", help="pasta de saída")
    args = p.parse_args(argv)
    for caminho in exportar_arestas(["data/mapas", "data/mapas_grupo"], args.out):
        print(caminho)


if __name__ == "__main__":
    main()
