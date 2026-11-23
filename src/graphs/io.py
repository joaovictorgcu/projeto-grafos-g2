
from dataclasses import dataclass, field
from pathlib import Path


PAREDE = "#"
CHAVES = "abcd"
PORTAS = "ABCD"
ESTEIRAS = "><^v"

SIMBOLOS = set("#.SG,~+*") | set(CHAVES + PORTAS + ESTEIRAS)


class MapaInvalido(ValueError):
    pass


@dataclass
class Mapa:
    nome: str
    grade: list[str]

    inicios: list[tuple[int, int]] = field(default_factory=list)
    saidas: list[tuple[int, int]] = field(default_factory=list)
    chaves: dict[str, list[tuple[int, int]]] = field(default_factory=dict)
    portas: dict[str, list[tuple[int, int]]] = field(default_factory=dict)
    bonus: dict[tuple[int, int], int] = field(default_factory=dict)
    fontes: list[tuple[int, int]] = field(default_factory=list)
    esteiras: dict[tuple[int, int], str] = field(default_factory=dict)

    @property
    def altura(self) -> int:
        return len(self.grade)

    @property
    def largura(self) -> int:
        return len(self.grade[0]) if self.altura else 0

    @property
    def inicio(self) -> tuple[int, int] | None:
        if len(self.inicios) == 0:
            return None
        return self.inicios[0]

    @property
    def livres(self) -> int:
        quantidade = 0

        for linha in self.grade:
            quantidade += len(linha) - linha.count(PAREDE)

        return quantidade

    @property
    def tipos_de_chave(self) -> list[str]:
        return sorted(self.chaves.keys())

    def casa(self, l: int, c: int) -> str:
        return self.grade[l][c]

    def dentro(self, l: int, c: int) -> bool:
        if l < 0 or l >= self.altura:
            return False

        return 0 <= c < len(self.grade[l])


def validar_mapa(mapa: Mapa) -> None:
    prefixo = f"{mapa.nome}: " if mapa.nome else ""

    if len(mapa.grade) == 0:
        raise MapaInvalido(prefixo + "o mapa está vazio.")

    colunas = mapa.largura

    for indice, conteudo in enumerate(mapa.grade):
        quantidade = len(conteudo)

        if quantidade == 0:
            raise MapaInvalido(
                f"{prefixo}a linha {indice} está vazia."
            )

        if quantidade != colunas:
            raise MapaInvalido(
                f"{prefixo}o mapa não é retangular: "
                f"a linha {indice} tem {quantidade} casas, "
                f"mas a primeira tem {colunas}."
            )

    desconhecidos = (
        (linha, coluna, simbolo)
        for linha, conteudo in enumerate(mapa.grade)
        for coluna, simbolo in enumerate(conteudo)
        if simbolo not in SIMBOLOS
    )

    primeiro_erro = next(desconhecidos, None)

    if primeiro_erro is not None:
        linha, coluna, simbolo = primeiro_erro

        raise MapaInvalido(
            f"{prefixo}símbolo desconhecido {simbolo!r} "
            f"na posição ({linha},{coluna})."
        )

    quantidade_inicios = len(mapa.inicios)

    if quantidade_inicios != 1:
        if quantidade_inicios == 0:
            raise MapaInvalido(
                f"{prefixo}o mapa não tem início S."
            )

        coordenadas = ", ".join(
            f"({linha},{coluna})"
            for linha, coluna in mapa.inicios
        )

        raise MapaInvalido(
            f"{prefixo}o mapa tem {quantidade_inicios} "
            f"inícios S, em {coordenadas}."
        )

    if len(mapa.saidas) == 0:
        raise MapaInvalido(
            f"{prefixo}o mapa não tem saída G."
        )


def interpretar_mapa(texto: str, nome: str = "") -> Mapa:
    conteudo = texto.removeprefix("\ufeff").splitlines()

    linhas = [
        linha for linha in conteudo
        if not linha.startswith(";")
    ]

    primeira = 0
    ultima = len(linhas)

    while primeira < ultima and not linhas[primeira].strip():
        primeira += 1

    while ultima > primeira and not linhas[ultima - 1].strip():
        ultima -= 1

    grade = linhas[primeira:ultima]

    # Agrupa todas as posições pelo símbolo encontrado.
    posicoes = {}

    for l, linha in enumerate(grade):
        for c, simbolo in enumerate(linha):
            if simbolo not in posicoes:
                posicoes[simbolo] = []

            posicoes[simbolo].append((l, c))

    # Separa as posições conforme o tipo de elemento.
    inicios = posicoes.get("S", [])
    saidas = posicoes.get("G", [])
    fontes = posicoes.get("*", [])

    chaves = {
        letra: posicoes[letra]
        for letra in CHAVES
        if letra in posicoes
    }

    portas = {
        letra: posicoes[letra]
        for letra in PORTAS
        if letra in posicoes
    }

    esteiras = {
        coordenada: direcao
        for direcao in ESTEIRAS
        for coordenada in posicoes.get(direcao, [])
    }

    bonus = {
        coordenada: numero
        for numero, coordenada in enumerate(
            posicoes.get("+", [])
        )
    }

    mapa = Mapa(
        nome=nome,
        grade=grade,
        inicios=inicios,
        saidas=saidas,
        chaves=chaves,
        portas=portas,
        bonus=bonus,
        fontes=fontes,
        esteiras=esteiras
    )

    validar_mapa(mapa)

    return mapa


def ler_mapa(caminho) -> Mapa:
    arquivo = Path(caminho)

    try:
        conteudo = arquivo.read_text(encoding="utf-8-sig")
    except OSError as erro:
        raise MapaInvalido(
            f"Não foi possível ler o mapa '{arquivo}': {erro}"
        ) from erro

    return interpretar_mapa(conteudo, nome=arquivo.stem)


def ler_dataset(pasta):
    from .dataset import carregar_dataset

    return carregar_dataset(pasta)
