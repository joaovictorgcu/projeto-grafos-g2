# [IA] Claude Code (Claude Opus 5.5) – leitura do mapa .txt e localização de S, G, chaves, portas, bônus, fontes e esteiras
from dataclasses import dataclass, field
from pathlib import Path

PAREDE = "#"
CHAVES = "abcd"
PORTAS = "ABCD"
ESTEIRAS = "><^v"
SIMBOLOS = set("#.SG,~+*") | set(CHAVES) | set(PORTAS) | set(ESTEIRAS)


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
        return len(self.grade[0]) if self.grade else 0

    @property
    def inicio(self) -> tuple[int, int] | None:
        return self.inicios[0] if self.inicios else None

    @property
    def livres(self) -> int:
        return sum(1 for linha in self.grade for casa in linha if casa != PAREDE)

    @property
    def tipos_de_chave(self) -> list[str]:
        return sorted(self.chaves)

    def casa(self, l: int, c: int) -> str:
        return self.grade[l][c]

    def dentro(self, l: int, c: int) -> bool:
        return 0 <= l < self.altura and 0 <= c < len(self.grade[l])


def validar_mapa(mapa: Mapa) -> None:
    nome = f"{mapa.nome}: " if mapa.nome else ""
    if not mapa.grade:
        raise MapaInvalido(f"{nome}o mapa está vazio.")

    largura = len(mapa.grade[0])
    for l, linha in enumerate(mapa.grade):
        if not linha:
            raise MapaInvalido(f"{nome}a linha {l} está vazia. O mapa precisa ser retangular.")
        if len(linha) != largura:
            raise MapaInvalido(
                f"{nome}o mapa não é retangular: a linha {l} tem {len(linha)} casas, "
                f"mas a linha 0 tem {largura}."
            )

    for l, linha in enumerate(mapa.grade):
        for c, casa in enumerate(linha):
            if casa not in SIMBOLOS:
                raise MapaInvalido(
                    f"{nome}símbolo desconhecido {casa!r} na posição ({l},{c}). "
                    f"Os símbolos válidos são: # . S G , ~ + * a-d A-D > < ^ v"
                )

    if not mapa.inicios:
        raise MapaInvalido(f"{nome}o mapa não tem início S; precisa ter exatamente um.")
    if len(mapa.inicios) > 1:
        posicoes = ", ".join(f"({l},{c})" for l, c in mapa.inicios)
        raise MapaInvalido(
            f"{nome}o mapa tem {len(mapa.inicios)} inícios S, em {posicoes}; precisa ter exatamente um."
        )
    if not mapa.saidas:
        raise MapaInvalido(f"{nome}o mapa não tem saída G; precisa ter pelo menos uma.")


def interpretar_mapa(texto: str, nome: str = "") -> Mapa:
    texto = texto.removeprefix("\ufeff")
    linhas = [l for l in texto.splitlines() if not l.startswith(";")]
    while linhas and not linhas[0].strip():
        linhas.pop(0)
    while linhas and not linhas[-1].strip():
        linhas.pop()

    mapa = Mapa(nome=nome, grade=linhas)
    for l, linha in enumerate(linhas):
        for c, casa in enumerate(linha):
            pos = (l, c)
            if casa == "S":
                mapa.inicios.append(pos)
            elif casa == "G":
                mapa.saidas.append(pos)
            elif casa in CHAVES:
                mapa.chaves.setdefault(casa, []).append(pos)
            elif casa in PORTAS:
                mapa.portas.setdefault(casa, []).append(pos)
            elif casa == "+":
                mapa.bonus[pos] = len(mapa.bonus)
            elif casa == "*":
                mapa.fontes.append(pos)
            elif casa in ESTEIRAS:
                mapa.esteiras[pos] = casa
    validar_mapa(mapa)
    return mapa


def ler_mapa(caminho) -> Mapa:
    caminho = Path(caminho)
    texto = caminho.read_text(encoding="utf-8-sig")
    return interpretar_mapa(texto, nome=caminho.stem)
