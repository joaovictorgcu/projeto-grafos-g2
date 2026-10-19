"""Visualizações da Parte 1 (P5).

Por enquanto: o percurso sobre a grade do mapa, com a cor mudando a cada chave
coletada (uma cor por camada = conjunto de chaves). Recebe o percurso como lista
de rótulos no formato do enunciado, "(3,5)|ab|{0,2}", que é o que sai do grafo
de estados — então não depende de como o caminho foi calculado.

Uso:
    python -m src.viz --mapa data/mapas/m03_tres_chaves.txt \
        --percurso out/parte1/percurso_m03.json --png out/parte1/percurso_m03.png
"""
import argparse
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

# Terreno em tons neutros, para o percurso (colorido) ser o que salta aos olhos.
COR_TERRENO = {
    "#": "#4a4a48",  # parede
    "~": "#d3e4f5",  # água
    ",": "#e6d8c3",  # lama
}
COR_CHAO = "#fcfcfb"
COR_TEXTO = "#0b0b0b"
COR_TEXTO_2 = "#52514e"

# Uma cor por camada, na ordem em que as camadas aparecem no percurso.
# [IA] Claude Code (Claude Opus 5.5) – paleta categórica conferida com validador de daltonismo; revisada por Caio
CORES_CAMADA = ["#2a78d6", "#eb6834", "#1baf7a", "#e87ba4", "#6250d6", "#008300"]

CUSTO = {",": 3, "~": 5, "*": -2}

_ROTULO = re.compile(r"^\((\d+),(\d+)\)\|([a-z]+|-)\|\{([\d,]*)\}$")


def ler_mapa(caminho):
    """Linhas do mapa, sem os comentários (;) e sem linhas vazias."""
    # Só o necessário para desenhar; a leitura/validação de verdade é do src/graphs/io.py.
    with open(caminho, encoding="utf-8") as f:
        return [l.rstrip("\r\n") for l in f if l.strip() and not l.startswith(";")]


def ler_rotulo(rotulo):
    """'(3,5)|ab|{0,2}' -> ((3, 5), 'ab', frozenset({0, 2}))."""
    m = _ROTULO.match(rotulo.strip())
    if not m:
        raise ValueError(f"Rótulo fora do formato (l,c)|chaves|{{bônus}}: {rotulo!r}")
    linha, coluna, chaves, bonus = m.groups()
    chaves = "" if chaves == "-" else chaves
    bonus = frozenset(int(b) for b in bonus.split(",") if b)
    return (int(linha), int(coluna)), chaves, bonus


def custo_do_percurso(linhas, estados):
    """Soma dos custos das casas de destino (o + só vale -4 quando é consumido)."""
    total = 0
    for (_, _, bon_u), ((l, c), _, bon_v) in zip(estados, estados[1:]):
        casa = linhas[l][c]
        if casa == "+":
            total += -4 if len(bon_v) > len(bon_u) else 1
        else:
            total += CUSTO.get(casa, 1)
    return total


def _lado_da_casa(largura):
    """Polegadas por casa: 0,55 nos mapas pequenos, encolhendo para o m08 caber em ~16 pol."""
    return min(0.55, 16 / largura)


def _desenhar_grade(ax, linhas, dy=0, fonte=11, alpha=1.0):
    for l, linha in enumerate(linhas):
        for c, casa in enumerate(linha):
            ax.add_patch(Rectangle((c - 0.5, l + dy - 0.5), 1, 1,
                                   facecolor=COR_TERRENO.get(casa, COR_CHAO),
                                   edgecolor="#e4e3df", linewidth=0.4, alpha=alpha, zorder=1))
            if casa in "SGABCD" or casa in "abcd" or casa in "+*<>^v":
                ax.text(c, l + dy, casa, ha="center", va="center", fontsize=fonte,
                        fontweight="bold" if casa.isupper() else "normal",
                        color=COR_TEXTO, alpha=0.55 * alpha, zorder=2)


# [IA] Claude Code (Claude Opus 5.5) – desenho do percurso em camadas com deslocamento por camada; revisado por Caio
def desenhar_percurso(linhas, rotulos, saida, nome_mapa="", algoritmo="menor custo"):
    """Desenha o percurso sobre a grade e salva em `saida` (PNG).

    Cada trecho do percurso tem a cor da camada (conjunto de chaves) em que o
    jogador está. Como o caminho costuma voltar pelo mesmo corredor depois de
    pegar uma chave, cada camada é levemente deslocada para os trechos não se
    sobreporem.
    """
    estados = [ler_rotulo(r) for r in rotulos]
    if len(estados) < 2:
        raise ValueError("O percurso precisa de pelo menos dois estados.")

    camadas = []  # na ordem em que aparecem
    for _, chaves, _ in estados:
        if chaves not in camadas:
            camadas.append(chaves)
    if len(camadas) > len(CORES_CAMADA):
        raise ValueError(f"Percurso com {len(camadas)} camadas; a paleta tem {len(CORES_CAMADA)}.")
    cor = {k: CORES_CAMADA[i] for i, k in enumerate(camadas)}
    passo_desloc = min(0.13, 0.6 / len(camadas))  # todas as camadas cabem dentro da casa
    desloc = {k: (i - (len(camadas) - 1) / 2) * passo_desloc for i, k in enumerate(camadas)}

    altura, largura = len(linhas), max(len(l) for l in linhas)
    lado = _lado_da_casa(largura)
    escala = lado / 0.55  # 1 nos mapas pequenos; linhas e marcadores encolhem junto no m08
    fig, ax = plt.subplots(figsize=(max(6.0, largura * lado), max(4.0, altura * lado + 1.6)),
                           dpi=150 if escala == 1 else 200)
    _desenhar_grade(ax, linhas, fonte=max(5, 11 * escala))

    # Trechos contínuos de uma mesma camada. O trecho que pega a chave termina
    # na casa da chave com a cor antiga; a cor nova começa a partir dela.
    passos_por_camada = {k: 0 for k in camadas}
    trecho = [estados[0]]
    for anterior, atual in zip(estados, estados[1:]):
        if atual[1] != anterior[1]:
            _desenhar_trecho(ax, trecho + [atual], cor[anterior[1]], desloc[anterior[1]], desloc[atual[1]],
                             lw=2.6 * escala)
            passos_por_camada[anterior[1]] += len(trecho)
            trecho = [atual]
        else:
            trecho.append(atual)
    _desenhar_trecho(ax, trecho, cor[trecho[0][1]], desloc[trecho[0][1]], lw=2.6 * escala)
    passos_por_camada[trecho[0][1]] += len(trecho) - 1

    # Marcos: início, cada chave coletada e chegada.
    (l0, c0), k0, _ = estados[0]
    ax.plot(c0 + desloc[k0], l0 + desloc[k0], "o", ms=10 * escala ** 0.5, color=cor[k0],
            mec=COR_CHAO, mew=2, zorder=5)
    for anterior, atual in zip(estados, estados[1:]):
        if atual[1] != anterior[1]:
            (l, c), k, _ = atual
            nova = "".join(sorted(set(k) - set(anterior[1])))
            ax.plot(c, l, "*", ms=17 * escala ** 0.5, color=cor[k], mec=COR_TEXTO, mew=0.8, zorder=6)
            ax.annotate(f"pega {nova}", (c, l), xytext=(0, 12), textcoords="offset points",
                        ha="center", fontsize=9, color=COR_TEXTO, zorder=7,
                        bbox=dict(boxstyle="round,pad=0.2", fc=COR_CHAO, ec="none", alpha=0.9))
    (lf, cf), kf, _ = estados[-1]
    ax.plot(cf + desloc[kf], lf + desloc[kf], "s", ms=10 * escala ** 0.5, color=cor[kf],
            mec=COR_CHAO, mew=2, zorder=5)

    passos = len(estados) - 1
    custo = custo_do_percurso(linhas, estados)
    titulo = f"{nome_mapa}: percurso de {algoritmo}" if nome_mapa else f"Percurso de {algoritmo}"
    ax.set_title(f"{titulo}\n{passos} passos · custo {custo} · a cor muda a cada chave coletada",
                 fontsize=12, color=COR_TEXTO, loc="left")
    ax.set_xlabel("coluna", color=COR_TEXTO_2)
    ax.set_ylabel("linha", color=COR_TEXTO_2)
    ax.set_xlim(-0.5, largura - 0.5)
    ax.set_ylim(altura - 0.5, -0.5)  # linha 0 em cima, como no arquivo
    ax.set_xticks(range(largura))
    ax.set_yticks(range(altura))
    ax.tick_params(labelsize=8, colors=COR_TEXTO_2, length=0)
    ax.set_aspect("equal")
    for lado in ax.spines.values():
        lado.set_visible(False)

    legenda = [Line2D([0], [0], color=cor[k], lw=3,
                      label=f"chaves {{{','.join(k)}}} · {passos_por_camada[k]} passos" if k
                      else f"sem chaves · {passos_por_camada[k]} passos")
               for k in camadas]
    legenda += [
        Line2D([0], [0], marker="o", ls="", color=COR_TEXTO_2, ms=8, label="início"),
        Line2D([0], [0], marker="*", ls="", color=COR_TEXTO_2, ms=12, label="chave coletada"),
        Line2D([0], [0], marker="s", ls="", color=COR_TEXTO_2, ms=8, label="chegada (G)"),
        Patch(facecolor=COR_TERRENO["#"], label="parede"),
        Patch(facecolor=COR_TERRENO["~"], label="água (custo 5)"),
        Patch(facecolor=COR_TERRENO[","], label="lama (custo 3)"),
    ]
    ax.legend(handles=legenda, loc="upper center", bbox_to_anchor=(0.5, -0.1),
              ncol=3, frameon=False, fontsize=9, labelcolor=COR_TEXTO)

    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(saida, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return saida


def _desenhar_trecho(ax, trecho, cor, desloc, desloc_fim=None, lw=2.6):
    if desloc_fim is None:
        desloc_fim = desloc
    xs = [c + desloc for (_, c), _, _ in trecho]
    ys = [l + desloc for (l, _), _, _ in trecho]
    # o último ponto encosta na posição da camada seguinte, para a linha não ter buraco
    (lf, cf), _, _ = trecho[-1]
    xs[-1], ys[-1] = cf + desloc_fim, lf + desloc_fim
    ax.plot(xs, ys, color=cor, lw=lw, solid_capstyle="round", solid_joinstyle="round", zorder=4)


# [IA] Claude Code (Claude Opus 5.5) – layout do grafo de estados em faixas, uma por camada; revisado por Caio
def desenhar_camadas(linhas, grafo, saida, nome_mapa=""):
    """Desenha o grafo de estados com uma faixa por camada (conjunto de chaves).

    `grafo` é um Grafo (src/graphs/graph.py) cujos nós são rótulos
    "(l,c)|chaves|{bônus}" mais o nó virtual "ALVO". Dentro de cada faixa o
    estado fica na posição da sua casa no mapa, então a faixa lembra o próprio
    labirinto; os arcos que mudam de camada (pegar uma chave) atravessam de uma
    faixa para outra e vão destacados. Pensado para mapas pequenos como o m02:
    estados que diferem só nos bônus caem no mesmo ponto.
    """
    estados = {u: ler_rotulo(u) for u in grafo.nos() if u != "ALVO"}
    camadas = sorted({k for _, k, _ in estados.values()}, key=lambda k: (len(k), k))
    if len(camadas) > len(CORES_CAMADA):
        raise ValueError(f"Grafo com {len(camadas)} camadas; a paleta tem {len(CORES_CAMADA)}.")
    cor = {k: CORES_CAMADA[i] for i, k in enumerate(camadas)}

    altura, largura = len(linhas), max(len(l) for l in linhas)
    vao = 2.0  # espaço entre as faixas, onde passam os arcos que trocam de camada
    dy = {k: i * (altura + vao) for i, k in enumerate(camadas)}
    alvo_xy = (largura + 1.5, (len(camadas) * (altura + vao) - vao) / 2 - 0.5)

    def xy(u):
        if u == "ALVO":
            return alvo_xy
        (l, c), k, _ = estados[u]
        return c, l + dy[k]

    lado = 0.5
    total_y = len(camadas) * (altura + vao) - vao
    fig, ax = plt.subplots(figsize=((largura + 3) * lado + 1, total_y * lado + 2.2), dpi=150)
    for k in camadas:
        _desenhar_grade(ax, linhas, dy=dy[k], fonte=9, alpha=0.45)
        n = sum(1 for _, kk, _ in estados.values() if kk == k)
        nome = f"chaves {{{','.join(k)}}}" if k else "sem chaves"
        ax.text(-0.7, dy[k] - 0.75, f"camada {k or '-'} ({nome}) · {n} estados",
                ha="left", va="bottom", fontsize=10, color=COR_TEXTO, fontweight="bold")

    # Arcos. Ida e volta entre o mesmo par vira um traço só; mão única ganha seta.
    arcos = {(u, v) for u in grafo.nos() for v in grafo.vizinhos(u)}
    n_dentro = n_troca = n_alvo = 0
    for u, v in sorted(arcos):
        if u == "ALVO":
            continue
        (x0, y0), (x1, y1) = xy(u), xy(v)
        if v == "ALVO":
            n_alvo += 1
            ax.annotate("", (x1, y1), (x0, y0), zorder=3,
                        arrowprops=dict(arrowstyle="-|>", color=COR_TEXTO_2, lw=1.2, ls="--",
                                        shrinkA=6, shrinkB=12, mutation_scale=12))
        elif estados[u][1] != estados[v][1]:
            n_troca += 1
            ax.annotate("", (x1, y1), (x0, y0), zorder=5,
                        arrowprops=dict(arrowstyle="-|>", color=COR_TEXTO, lw=2.4,
                                        shrinkA=6, shrinkB=6, mutation_scale=16,
                                        connectionstyle="arc3,rad=-0.25"))
            nova = "".join(sorted(set(estados[v][1]) - set(estados[u][1])))
            meio_do_vao = dy[estados[v][1]] - vao / 2 - 0.5
            ax.annotate(f"pega {nova}: {u} → {v}", ((x0 + x1) / 2, meio_do_vao),
                        xytext=(-10, 0), textcoords="offset points", ha="right", va="center",
                        fontsize=9, color=COR_TEXTO, zorder=7,
                        bbox=dict(boxstyle="round,pad=0.25", fc=COR_CHAO, ec="none", alpha=0.95))
        else:
            n_dentro += 1
            if (v, u) in arcos:
                if u < v:
                    ax.plot([x0, x1], [y0, y1], color=cor[estados[u][1]], lw=1.6, alpha=0.75, zorder=3)
            else:
                ax.annotate("", (x1, y1), (x0, y0), zorder=3,
                            arrowprops=dict(arrowstyle="-|>", color=cor[estados[u][1]], lw=1.6,
                                            shrinkA=5, shrinkB=5, mutation_scale=11))

    for u in estados:
        x, y = xy(u)
        ax.plot(x, y, "o", ms=7, color=cor[estados[u][1]], mec=COR_CHAO, mew=1.2, zorder=4)
    if "ALVO" in grafo.adj:
        ax.plot(*alvo_xy, "D", ms=12, color=COR_TEXTO, zorder=6)
        ax.text(alvo_xy[0], alvo_xy[1] + 0.9, "ALVO", ha="center", va="top", fontsize=10,
                color=COR_TEXTO, fontweight="bold")

    titulo = f"{nome_mapa}: grafo de estados em camadas" if nome_mapa else "Grafo de estados em camadas"
    ax.set_title(f"{titulo}\n{len(estados)} estados + ALVO · {n_dentro} arcos dentro das camadas · "
                 f"{n_troca} mudando de camada · {n_alvo} até o ALVO",
                 fontsize=12, color=COR_TEXTO, loc="left")
    ax.set_xlabel("coluna da casa no mapa", color=COR_TEXTO_2)
    ax.set_ylabel("linha da casa no mapa (uma faixa por camada)", color=COR_TEXTO_2)
    ax.set_xlim(-1, alvo_xy[0] + 1.2)
    ax.set_ylim(total_y - 0.3, -1.6)
    ax.set_xticks(range(largura))
    ax.set_yticks([l + dy[k] for k in camadas for l in range(altura)],
                  [str(l) for _ in camadas for l in range(altura)])
    ax.tick_params(labelsize=8, colors=COR_TEXTO_2, length=0)
    ax.set_aspect("equal")
    for lado_ax in ax.spines.values():
        lado_ax.set_visible(False)

    legenda = [Line2D([0], [0], marker="o", ls="", color=cor[k], ms=7,
                      label=f"estado com chaves {{{','.join(k)}}}" if k else "estado sem chaves")
               for k in camadas]
    legenda += [
        Line2D([0], [0], color=COR_TEXTO_2, lw=1.6, label="arco dentro da camada (ida e volta)"),
        Line2D([0], [0], color=COR_TEXTO, lw=2.4, marker=">", ms=7, label="arco que muda de camada"),
        Line2D([0], [0], color=COR_TEXTO_2, lw=1.2, ls="--", label="arco de custo 0 até o ALVO"),
        Patch(facecolor=COR_TERRENO["#"], alpha=0.45, label="parede"),
        Patch(facecolor=COR_TERRENO[","], alpha=0.45, label="lama (custo 3)"),
    ]
    ax.legend(handles=legenda, loc="upper center", bbox_to_anchor=(0.5, -0.08),
              ncol=2, frameon=False, fontsize=9, labelcolor=COR_TEXTO)

    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(saida, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return saida


def _ler_percurso(caminho):
    """Aceita uma lista de rótulos ou um objeto com a lista em 'caminho'."""
    with open(caminho, encoding="utf-8") as f:
        dados = json.load(f)
    if isinstance(dados, dict):
        dados = dados.get("caminho")
    if not isinstance(dados, list) or not all(isinstance(r, str) for r in dados):
        raise ValueError(f"{caminho}: esperava uma lista de rótulos (ou {{'caminho': [...]}}).")
    return dados


def main(argv=None):
    p = argparse.ArgumentParser(description="Desenha um percurso sobre o mapa.")
    p.add_argument("--mapa", required=True, help="arquivo .txt do mapa")
    p.add_argument("--percurso", required=True, help="JSON com a lista de rótulos do percurso")
    p.add_argument("--png", required=True, help="arquivo de saída")
    p.add_argument("--algoritmo", default="menor custo", help="nome que vai no título")
    args = p.parse_args(argv)
    linhas = ler_mapa(args.mapa)
    saida = desenhar_percurso(linhas, _ler_percurso(args.percurso), args.png,
                              nome_mapa=Path(args.mapa).stem, algoritmo=args.algoritmo)
    print(f"Figura salva em {saida}")


if __name__ == "__main__":
    main()
