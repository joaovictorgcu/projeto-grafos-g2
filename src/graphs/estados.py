"""Representacoes de mapas por posicoes e por estados alcançaveis."""

import argparse
import csv
from collections import deque
from dataclasses import dataclass
from pathlib import Path

from .graph import Grafo
from .io import CHAVES, ESTEIRAS, PAREDE, PORTAS, Mapa, ler_mapa


ALVO = "ALVO"

# A insercao do dicionario define a ordem em que os vizinhos sao visitados.
PASSOS = {
    "N": (-1, 0),
    "L": (0, 1),
    "S": (1, 0),
    "O": (0, -1),
}
SENTIDO = dict(zip(ESTEIRAS, ("L", "O", "N", "S")))
COLUNAS_CSV = ("origem", "destino", "movimento", "casa_destino", "peso")


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

    def registrar(self, origem, destino, movimento, simbolo, custo):
        """Mantem o grafo e o relatorio de arcos sincronizados."""
        self.grafo.adicionar_arco(origem, destino, custo)
        self.arcos.append(ArcoDetalhado(origem, destino, movimento, simbolo, custo))


def rotulo(estado: Estado) -> str:
    letras = "".join(sorted(estado.chaves))
    identificadores = ",".join(str(item) for item in sorted(estado.bonus))
    return f"({estado.linha},{estado.coluna})|{letras or '-'}|{{{identificadores}}}"


def _coordenada(posicao):
    return f"({posicao[0]},{posicao[1]})"


def _movimentos(mapa, posicao):
    """Percorre a grade em N-L-S-O, considerando paredes e esteiras."""
    linha, coluna = posicao
    restricao = SENTIDO.get(mapa.casa(linha, coluna))

    for letra, (dl, dc) in PASSOS.items():
        if restricao is not None and restricao != letra:
            continue

        chegada = (linha + dl, coluna + dc)
        if not mapa.dentro(*chegada):
            continue

        terreno = mapa.casa(*chegada)
        if terreno != PAREDE:
            yield letra, chegada, terreno


def _custo_terreno(simbolo):
    if simbolo == ",":
        return 3
    if simbolo == "~":
        return 5
    if simbolo == "*":
        return -2
    if simbolo == "+":
        return -4
    return 1


def _visitar(mapa, origem, destino, simbolo, usar_fontes, fontes_por_posicao):
    """Atualiza o inventario ao entrar numa casa e devolve (estado, custo)."""
    novas_chaves = origem.chaves
    visitados = origem.bonus
    custo = _custo_terreno(simbolo)

    if simbolo in CHAVES:
        novas_chaves = origem.chaves | frozenset((simbolo,))

    identificador = None
    if simbolo == "+":
        identificador = mapa.bonus[destino]
    if simbolo == "*" and usar_fontes:
        identificador = len(mapa.bonus) + fontes_por_posicao[destino]

    if identificador is not None:
        if identificador in visitados:
            custo = 1
        else:
            visitados = visitados | frozenset((identificador,))

    novo = Estado(destino[0], destino[1], novas_chaves, visitados)
    return novo, custo


def construir_estados(mapa: Mapa, fonte_consumivel: bool = False) -> GrafoConstruido:
    """Expande a partir de S, sem materializar combinacoes inacessiveis."""
    if mapa.inicio is None:
        raise ValueError("O mapa precisa ter uma posicao inicial S.")

    partida = Estado(*mapa.inicio)
    resultado = GrafoConstruido(Grafo(), [], rotulo(partida))
    resultado.grafo.adicionar_no(resultado.inicial)

    fila = deque((partida,))
    catalogados = {partida}
    fontes_por_posicao = {pos: indice for indice, pos in enumerate(mapa.fontes)}

    while fila:
        presente = fila.popleft()
        nome = rotulo(presente)
        posicao = (presente.linha, presente.coluna)

        if mapa.casa(*posicao) == "G":
            resultado.registrar(nome, ALVO, "-", "-", 0)
            continue

        for passo, destino, terreno in _movimentos(mapa, posicao):
            if terreno in PORTAS and terreno.lower() not in presente.chaves:
                continue

            proximo, peso = _visitar(
                mapa, presente, destino, terreno, fonte_consumivel, fontes_por_posicao
            )
            resultado.registrar(nome, rotulo(proximo), passo, terreno, peso)

            if proximo not in catalogados:
                catalogados.add(proximo)
                fila.append(proximo)

    resultado.grafo.adicionar_no(ALVO)
    return resultado


def construir_posicoes(mapa: Mapa, portas: str = "chao") -> GrafoConstruido:
    """Considera cada casa transitavel um no, sem inventario."""
    if portas not in {"chao", "parede"}:
        raise ValueError(f"portas deve ser 'chao' ou 'parede', não {portas!r}")
    if mapa.inicio is None:
        raise ValueError("O mapa precisa ter uma posicao inicial S.")

    bloquear = portas == "parede"
    transitaveis = set()
    resultado = GrafoConstruido(Grafo(), [], _coordenada(mapa.inicio))

    # Nos primeiro, em ordem de leitura: linhas da esquerda para a direita.
    for l, linha in enumerate(mapa.grade):
        for c, terreno in enumerate(linha):
            if terreno == PAREDE or (bloquear and terreno in PORTAS):
                continue
            posicao = (l, c)
            transitaveis.add(posicao)
            resultado.grafo.adicionar_no(_coordenada(posicao))

    # Usa a mesma ordem para os arcos, mantendo os CSVs deterministas.
    for l, linha in enumerate(mapa.grade):
        for c, terreno in enumerate(linha):
            atual = (l, c)
            if atual not in transitaveis:
                continue

            origem = _coordenada(atual)
            if terreno == "G":
                resultado.registrar(origem, ALVO, "-", "-", 0)
                continue

            for direcao, vizinho, destino in _movimentos(mapa, atual):
                if vizinho not in transitaveis:
                    continue
                resultado.registrar(
                    origem, _coordenada(vizinho), direcao, destino,
                    _custo_terreno(destino)
                )

    resultado.grafo.adicionar_no(ALVO)
    return resultado


def metricas(construido: GrafoConstruido) -> dict:
    grafo = construido.grafo
    vertices = tuple(vertice for vertice in grafo.nos() if vertice != ALVO)
    numero_vertices = len(vertices)
    numero_arcos = sum(
        destino != ALVO
        for vertice in vertices
        for destino, _ in grafo.arcos(vertice)
    )
    divisor = numero_vertices * (numero_vertices - 1)
    return {
        "ordem": numero_vertices,
        "tamanho": numero_arcos,
        "densidade": numero_arcos / divisor if divisor else 0.0,
    }


def escrever_arestas_csv(arcos, caminho) -> Path:
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)

    with destino.open("w", newline="", encoding="utf-8") as arquivo:
        tabela = csv.writer(arquivo)
        tabela.writerow(COLUNAS_CSV)
        tabela.writerows(
            (arco.origem, arco.destino, arco.movimento, arco.casa_destino, arco.peso)
            for arco in arcos
        )

    return destino


def nome_curto(arquivo) -> str:
    nome = Path(arquivo).stem
    comeco, separador, _ = nome.partition("_")
    if comeco.startswith("m") and comeco[1:].isdigit():
        return comeco
    return nome


def exportar_arestas(pastas, saida) -> list:
    resultados = []
    pasta_saida = Path(saida)

    for diretorio in map(Path, pastas):
        for arquivo in sorted(diretorio.glob("*.txt")):
            arcos = construir_estados(ler_mapa(arquivo)).arcos
            caminho = pasta_saida / f"arestas_{nome_curto(arquivo)}.csv"
            resultados.append(escrever_arestas_csv(arcos, caminho))

    return resultados


def main(argv=None):
    parser = argparse.ArgumentParser(description="Exporta os arcos dos mapas .txt em CSV.")
    parser.add_argument("--out", default="out/parte1", help="pasta de saida")
    parametros = parser.parse_args(argv)

    for destino in exportar_arestas(("data/mapas", "data/mapas_grupo"), parametros.out):
        print(destino)


if __name__ == "__main__":
    main()
