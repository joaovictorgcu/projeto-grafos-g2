"""Visualizações da Parte 1 (P5).

Por enquanto: o percurso sobre a grade do mapa, com a cor mudando a cada chave
coletada (uma cor por camada = conjunto de chaves). Recebe o percurso como lista
de rótulos no formato do enunciado, "(3,5)|ab|{0,2}", que é o que sai do grafo
de estados — então não depende de como o caminho foi calculado.

Também desenha, a partir do grafo de estados (src/graphs/estados.py), a árvore
BFS por níveis e o heatmap de multiplicidade das casas.

Uso (o percurso é calculado pelo grafo de estados; --percurso JSON é opcional):
    python -m src.viz --mapa data/mapas/m03_tres_chaves.txt --png out/parte1/percurso_m03.png
    python -m src.viz --mapa data/mapas/m02_uma_chave.txt --camadas out/parte1/camadas_m02.png
    python -m src.viz --mapa data/mapas/m02_uma_chave.txt --arvore-bfs out/parte1/arvore_bfs_m02.png
    python -m src.viz --mapa data/mapas/m08_grande.txt --multiplicidade out/parte1/multiplicidade_m08.png
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


# [IA] Claude Code (Claude Opus 5.5) – árvore BFS desenhada por níveis, com layout de árvore arrumada; revisado por Caio
def desenhar_arvore_bfs(grafo, inicial, saida, nome_mapa=""):
    """Desenha a árvore BFS do grafo de estados a partir de `inicial`, um nível por linha.

    O eixo vertical é o nível (passos desde o início); cada estado fica na linha
    do seu nível. Os filhos aparecem na ordem em que o BFS os descobriu (N, L, S, O),
    e o pai fica centrado sobre eles. O caminho até o ALVO vai em traço grosso.
    """
    from .graphs.algorithms import bfs, caminho

    dist, pai = bfs(grafo, inicial)
    filhos = {u: [] for u in dist}
    for v in dist:  # dist preserva a ordem de descoberta
        if pai[v] is not None:
            filhos[pai[v]].append(v)

    # Folhas ganham x = 0, 1, 2... da esquerda para a direita; pai = média dos filhos.
    x, prox = {}, [0]

    def posicionar(u):
        if not filhos[u]:
            x[u] = prox[0]
            prox[0] += 1
        else:
            for v in filhos[u]:
                posicionar(v)
            x[u] = sum(x[v] for v in filhos[u]) / len(filhos[u])

    import sys
    sys.setrecursionlimit(max(sys.getrecursionlimit(), 4 * len(dist)))
    posicionar(inicial)

    camada = {u: ler_rotulo(u)[1] for u in dist if u != "ALVO"}
    camadas = sorted(set(camada.values()), key=lambda k: (len(k), k))
    if len(camadas) > len(CORES_CAMADA):
        raise ValueError(f"Árvore com {len(camadas)} camadas; a paleta tem {len(CORES_CAMADA)}.")
    cor = {k: CORES_CAMADA[i] for i, k in enumerate(camadas)}
    no_caminho = set(caminho(pai, "ALVO") or [])

    niveis = max(dist.values()) + 1
    largura = prox[0]
    fig, ax = plt.subplots(figsize=(max(7.0, 2.6 * largura + 4), niveis * 0.3 + 2), dpi=150)
    for n in range(0, niveis, 2):  # faixas alternadas para o olho seguir o nível
        ax.axhspan(n - 0.5, n + 0.5, color="#f1f0ec", zorder=0, lw=0)

    n_troca = 0
    for v in dist:
        u = pai[v]
        if u is None:
            continue
        troca = v != "ALVO" and camada[u] != camada[v]
        n_troca += troca
        ax.plot([x[u], x[v]], [dist[u], dist[v]], zorder=2, solid_capstyle="round",
                color=COR_TEXTO if troca or v == "ALVO" else cor[camada[u]],
                lw=3.2 if v in no_caminho else 1.4,
                ls="--" if v == "ALVO" else "-")
        if troca:
            nova = "".join(sorted(set(camada[v]) - set(camada[u])))
            ax.annotate(f"pega {nova}", (x[v], dist[v] - 0.5), xytext=(-12, 0), textcoords="offset points",
                        ha="right", va="center", fontsize=9, color=COR_TEXTO, fontweight="bold", zorder=7,
                        bbox=dict(boxstyle="round,pad=0.25", fc=COR_CHAO, ec="none", alpha=0.95))

    for u in dist:
        if u == "ALVO":
            ax.plot(x[u], dist[u], "D", ms=9, color=COR_TEXTO, zorder=4)
            ax.text(x[u] + 0.12, dist[u], "ALVO", ha="left", va="center", fontsize=8.5,
                    color=COR_TEXTO, fontweight="bold")
            continue
        folha = not filhos[u]
        ax.plot(x[u], dist[u], "o", ms=7, zorder=4, color=COR_CHAO if folha else cor[camada[u]],
                mec=cor[camada[u]], mew=1.8 if folha else 1.2)
        ax.text(x[u] + 0.12, dist[u], u, ha="left", va="center", fontsize=8, color=COR_TEXTO,
                family="monospace", zorder=5)

    passos = dist["ALVO"] - 1 if "ALVO" in dist else None
    titulo = f"{nome_mapa}: árvore BFS de estados" if nome_mapa else "Árvore BFS de estados"
    sub = (f"{len(dist) - ('ALVO' in dist)} estados em {niveis} níveis · "
           + (f"menor número de passos até G: {passos}" if passos is not None else "G inalcançável")
           + f" · {n_troca} arco(s) da árvore mudam de camada")
    ax.set_title(f"{titulo}\n{sub}", fontsize=12, color=COR_TEXTO, loc="left")
    ax.set_ylabel("nível BFS (passos desde o início S)", color=COR_TEXTO_2)
    ax.set_xlabel("ramos da árvore (filhos na ordem de descoberta N, L, S, O)", color=COR_TEXTO_2)
    ax.set_ylim(niveis - 0.5, -0.8)
    ax.set_xlim(-0.6, largura - 1 + 1.9)
    ax.set_yticks(range(niveis))
    ax.set_xticks([])
    ax.tick_params(labelsize=8, colors=COR_TEXTO_2, length=0)
    for lado_ax in ax.spines.values():
        lado_ax.set_visible(False)

    legenda = [Line2D([0], [0], marker="o", ls="", color=cor[k], ms=7,
                      label=f"estado com chaves {{{','.join(k)}}}" if k else "estado sem chaves")
               for k in camadas]
    legenda += [
        Line2D([0], [0], marker="o", ls="", color=COR_CHAO, mec=COR_TEXTO_2, mew=1.8, ms=7,
               label="folha (o BFS não descobre nada novo dali)"),
        Line2D([0], [0], color=COR_TEXTO_2, lw=3.2, label="caminho BFS até o ALVO"),
        Line2D([0], [0], color=COR_TEXTO, lw=1.4, label="arco que muda de camada"),
        Line2D([0], [0], color=COR_TEXTO, lw=1.4, ls="--", label="arco de custo 0 até o ALVO"),
    ]
    ax.legend(handles=legenda, loc="upper center", bbox_to_anchor=(0.5, -0.03),
              ncol=2, frameon=False, fontsize=9, labelcolor=COR_TEXTO)

    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(saida, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return saida


# Rampa sequencial azul (clara -> escura) para contagens pequenas e discretas. Começa no
# passo 250, não no mais claro, para "1 estado" não sumir no fundo; a parede fica em
# cinza claro, para não competir com os azuis escuros.
# [IA] Claude Code (Claude Opus 5.5) – passos da rampa ordinal escolhidos com o skill de dataviz; revisado por Caio
RAMPA_MULTIPLICIDADE = ["#86b6ef", "#6da7ec", "#3987e5", "#2a78d6", "#256abf", "#1c5cab",
                        "#184f95", "#104281", "#0d366b"]
COR_PAREDE_CLARA = "#dcdbd6"


def multiplicidade_por_casa(grafo):
    """(l, c) -> quantos estados alcançáveis estão naquela casa."""
    mult = {}
    for u in grafo.nos():
        if u != "ALVO":
            pos, _, _ = ler_rotulo(u)
            mult[pos] = mult.get(pos, 0) + 1
    return mult


# [IA] Claude Code (Claude Opus 5.5) – heatmap discreto da multiplicidade sobre a grade; revisado por Caio
def desenhar_multiplicidade(linhas, grafo, saida, nome_mapa=""):
    """Heatmap da multiplicidade de cada casa: quantos estados alcançáveis ficam nela.

    Uma casa com multiplicidade 3 é visitada em 3 combinações diferentes de chaves
    (e bônus). Paredes em cinza escuro; casas livres que nenhum estado alcança
    vão hachuradas.
    """
    mult = multiplicidade_por_casa(grafo)
    maximo = max(mult.values())
    if maximo > len(RAMPA_MULTIPLICIDADE):
        raise ValueError(f"Multiplicidade {maximo}; a rampa tem {len(RAMPA_MULTIPLICIDADE)} passos.")
    # Passos espalhados pela rampa inteira, para 1 e o máximo ficarem bem distintos.
    n = len(RAMPA_MULTIPLICIDADE) - 1
    passos = [RAMPA_MULTIPLICIDADE[round(i * n / max(1, maximo - 1))] for i in range(maximo)]

    altura, largura = len(linhas), max(len(l) for l in linhas)
    lado = _lado_da_casa(largura)
    escala = lado / 0.55
    fig, ax = plt.subplots(figsize=(max(6.0, largura * lado), max(4.0, altura * lado + 1.8)),
                           dpi=150 if escala == 1 else 200)

    sem_estado = 0
    no_maximo = []
    for l, linha in enumerate(linhas):
        for c, casa in enumerate(linha):
            if casa == "#":
                ax.add_patch(Rectangle((c - 0.5, l - 0.5), 1, 1, facecolor=COR_PAREDE_CLARA,
                                       edgecolor="none", zorder=1))
                continue
            m = mult.get((l, c), 0)
            if m == 0:
                sem_estado += 1
                ax.add_patch(Rectangle((c - 0.5, l - 0.5), 1, 1, facecolor=COR_CHAO, edgecolor="#bdbcb7",
                                       hatch="////", linewidth=0, zorder=1))
            else:
                ax.add_patch(Rectangle((c - 0.5, l - 0.5), 1, 1, facecolor=passos[m - 1],
                                       edgecolor=COR_CHAO, linewidth=0.5 * escala, zorder=1))
                if m == maximo:
                    no_maximo.append((l, c))
            if casa in "SGABCDabcd":
                escura = m > 0 and passos[m - 1] in RAMPA_MULTIPLICIDADE[3:]
                ax.text(c, l, casa, ha="center", va="center", fontsize=max(5, 11 * escala),
                        fontweight="bold" if casa.isupper() else "normal",
                        color=COR_CHAO if escura else COR_TEXTO, zorder=3)

    titulo = f"{nome_mapa}: multiplicidade das casas" if nome_mapa else "Multiplicidade das casas"
    ax.set_title(f"{titulo}\nquantos estados alcançáveis (combinações de chaves e bônus) caem em cada casa · "
                 f"máxima {maximo}, em {len(no_maximo)} casas",
                 fontsize=12, color=COR_TEXTO, loc="left")
    ax.set_xlabel("coluna", color=COR_TEXTO_2)
    ax.set_ylabel("linha", color=COR_TEXTO_2)
    ax.set_xlim(-0.5, largura - 0.5)
    ax.set_ylim(altura - 0.5, -0.5)
    passo_tick = 1 if largura <= 20 else 5
    ax.set_xticks(range(0, largura, passo_tick))
    ax.set_yticks(range(0, altura, passo_tick))
    ax.tick_params(labelsize=8, colors=COR_TEXTO_2, length=0)
    ax.set_aspect("equal")
    for lado_ax in ax.spines.values():
        lado_ax.set_visible(False)

    contagem = {m: sum(1 for v in mult.values() if v == m) for m in range(1, maximo + 1)}
    legenda = [Patch(facecolor=passos[m - 1], edgecolor="#bdbcb7", linewidth=0.5,
                     label=f"{m} estado{'s' if m > 1 else ''} · {contagem[m]} casas")
               for m in range(1, maximo + 1)]
    legenda.append(Patch(facecolor=COR_PAREDE_CLARA, label="parede"))
    if sem_estado:
        legenda.append(Patch(facecolor=COR_CHAO, edgecolor="#bdbcb7", hatch="////",
                             label=f"livre, nunca alcançada · {sem_estado} casas"))
    ax.legend(handles=legenda, loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=min(4, len(legenda)),
              frameon=False, fontsize=9, labelcolor=COR_TEXTO, title="multiplicidade (estados na casa)",
              title_fontsize=9)

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


# [IA] Claude Code (Claude Opus 5.5) – percurso calculado pelo pipeline do grupo (estados.py + Dijkstra), sem JSON de fora
def percurso_de_menor_custo(construido):
    """Rótulos do caminho de menor custo do início ao ALVO (sem o ALVO), e o algoritmo usado.

    Usa Dijkstra; se o grafo tiver peso negativo (bônus, fonte), cai para Bellman-Ford.
    """
    from .graphs.algorithms import bellman_ford, caminho, dijkstra

    try:
        _, pai = dijkstra(construido.grafo, construido.inicial)
        algoritmo = "Dijkstra"
    except ValueError:
        _, pai, ciclo = bellman_ford(construido.grafo, construido.inicial)
        if ciclo:
            raise ValueError("O grafo de estados tem ciclo negativo: não há caminho de menor custo.")
        algoritmo = "Bellman-Ford"
    rotulos = caminho(pai, "ALVO")
    if rotulos is None:
        raise ValueError("Nenhum estado em G é alcançável: o mapa não tem solução.")
    return rotulos[:-1], algoritmo


# [IA] Claude Code (Claude Opus 5.5) – liga o labirinto interativo aos mapas reais: caminhos dos algoritmos e estados-armadilha
def estados_armadilha(construido):
    from .graphs.algorithms import bfs

    chegam_ao_alvo, _ = bfs(construido.grafo.transposto(), "ALVO")
    return [n for n in construido.grafo.nos() if n != "ALVO" and n not in chegam_ao_alvo]


def caminhos_dos_algoritmos(construido):
    from .graphs.algorithms import bellman_ford, bfs, caminho, dijkstra

    g, inicio = construido.grafo, construido.inicial
    _, pai = bfs(g, inicio)
    resultado = {"BFS": {"caminho": caminho(pai, "ALVO") or []}}
    try:
        _, pai = dijkstra(g, inicio)
        resultado["DIJKSTRA"] = {"caminho": caminho(pai, "ALVO") or []}
    except ValueError as erro:
        resultado["DIJKSTRA"] = {"caminho": [], "status": "RECUSA", "motivo": str(erro)}
    _, pai, ciclo = bellman_ford(g, inicio)
    if ciclo:
        nos, custo = ciclo
        resultado["BELLMAN_FORD"] = {
            "caminho": [], "status": "CICLO_NEGATIVO",
            "motivo": f"Ciclo negativo de custo {custo}: {' → '.join(nos)}",
        }
    else:
        resultado["BELLMAN_FORD"] = {"caminho": caminho(pai, "ALVO") or []}
    return resultado


def titulo_do_mapa(arquivo):
    codigo, _, resto = Path(arquivo).stem.partition("_")
    return f"{codigo} · {resto.replace('_', ' ')}" if resto else codigo


def main(argv=None):
    p = argparse.ArgumentParser(description="Figuras da Parte 1 sobre um mapa.")
    p.add_argument("--mapa", required=True, help="arquivo .txt do mapa")
    p.add_argument("--png", help="desenha o percurso de menor custo neste arquivo")
    p.add_argument("--percurso", help="JSON com os rótulos do percurso; sem ele, o percurso é calculado "
                                      "pelo grafo de estados (Dijkstra, ou Bellman-Ford com peso negativo)")
    p.add_argument("--algoritmo", help="nome que vai no título do percurso")
    p.add_argument("--camadas", metavar="PNG", help="desenha o grafo de estados em camadas neste arquivo")
    p.add_argument("--arvore-bfs", metavar="PNG", help="desenha a árvore BFS de estados neste arquivo")
    p.add_argument("--multiplicidade", metavar="PNG", help="desenha o heatmap de multiplicidade neste arquivo")
    args = p.parse_args(argv)
    if args.percurso and not args.png:
        p.error("--percurso precisa de --png.")
    if not (args.png or args.camadas or args.arvore_bfs or args.multiplicidade):
        p.error("nada a desenhar: use --png, --camadas, --arvore-bfs ou --multiplicidade.")

    from .graphs.estados import construir_estados
    from .graphs.io import ler_mapa as ler_mapa_validado

    nome = Path(args.mapa).stem
    linhas = ler_mapa(args.mapa)
    construido = construir_estados(ler_mapa_validado(args.mapa))
    saidas = []
    if args.png:
        if args.percurso:
            rotulos, algoritmo = _ler_percurso(args.percurso), "menor custo"
        else:
            rotulos, usado = percurso_de_menor_custo(construido)
            algoritmo = f"menor custo ({usado})"
        saidas.append(desenhar_percurso(linhas, rotulos, args.png, nome_mapa=nome,
                                        algoritmo=args.algoritmo or algoritmo))
    if args.camadas:
        saidas.append(desenhar_camadas(linhas, construido.grafo, args.camadas, nome))
    if args.arvore_bfs:
        saidas.append(desenhar_arvore_bfs(construido.grafo, construido.inicial, args.arvore_bfs, nome))
    if args.multiplicidade:
        saidas.append(desenhar_multiplicidade(linhas, construido.grafo, args.multiplicidade, nome))
    for saida in saidas:
        print(f"Figura salva em {saida}")


if __name__ == "__main__":
    main()
