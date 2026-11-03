"""Gráficos da Parte 2. Precisa do out/parte2/parte2_report.json (rode o --benchmark antes)."""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patheffects import withStroke
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter, PercentFormatter

from .avd_parte2 import SEM_LIGA, enriquecer, iqr
from .graphs.dataset import carregar_dataset, temporada

# Identidade visual. CORES é a ordem fixa dos algoritmos (BFS, DFS, Dijkstra, Bellman-Ford) nos
# gráficos A1 e A2; DESTAQUE é a cor da mensagem nos gráficos explanatórios; o resto é cinza.
CORES = ["#2a78d6", "#eb6834", "#1baf7a", "#e87ba4"]
DESTAQUE = "#eb6834"
NEUTRO = "#b9b8b3"
TEXTO = "#0b0b0b"
TEXTO_2 = "#52514e"
GRADE = "#e4e3df"
MENOS = "−"  # sinal de menos tipográfico, o mesmo que o matplotlib usa nos eixos

LIGAS = {
    "GB1": "Premier League (ING)", "ES1": "LaLiga (ESP)", "IT1": "Serie A (ITA)", "L1": "Bundesliga (ALE)",
    "FR1": "Ligue 1 (FRA)", "PO1": "Liga Portugal (POR)", "NL1": "Eredivisie (HOL)", "TR1": "Süper Lig (TUR)",
    "RU1": "Premier Liga (RUS)", "GR1": "Super League (GRE)", "UKR1": "Premier Liga (UCR)",
    "BE1": "Pro League (BEL)", "SC1": "Premiership (ESC)", "DK1": "Superliga (DIN)",
    "ARG1": "Liga Profesional (ARG)", "BRA1": "Brasileirão (BRA)", "MLS1": "MLS (EUA)", "A1": "Bundesliga (AUT)",
    "COL1": "Liga BetPlay (COL)", "SER1": "Super Liga (SRB)", "RO1": "Liga 1 (ROM)", "PL1": "Ekstraklasa (POL)",
    "JAP1": "J1 League (JAP)", "KR1": "K League 1 (COR)", "SE1": "Allsvenskan (SUE)", "C1": "Super League (SUI)",
    "NO1": "Eliteserien (NOR)", "TS1": "Chance Liga (TCH)", "SA1": "Saudi Pro League (ARS)", "MEX1": "Liga MX (MEX)",
    SEM_LIGA: "fora das ligas cobertas",
}

plt.rcParams.update({
    "axes.edgecolor": TEXTO_2, "axes.labelcolor": TEXTO_2, "xtick.color": TEXTO_2, "ytick.color": TEXTO_2,
    "axes.titlelocation": "left", "axes.titlesize": 12, "axes.titlecolor": TEXTO,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRADE,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False, "font.size": 9.5,
})


# --- formatação em pt-BR (ponto de milhar, vírgula decimal, menos tipográfico) ---

def br(n, decimais=0):
    s = f"{n:,.{decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s.replace("-", MENOS)


def pct(v, decimais=0):
    return br(100 * v, decimais) + "%"


def pct_eixo(v, _=None):
    """Para eixos: 100%, 10%, 1%, 0,1% (sem casas decimais fixas)."""
    return f"{100 * v:g}".replace(".", ",") + "%"


def milhoes(x, _=None):
    """EUR em milhões; uma casa decimal só quando ela existe (−3,5 mi, mas −180 mi)."""
    v = x / 1e6
    return f"{br(v, 0 if abs(v - round(v)) < 0.05 else 1)} mi"


def eur(x, _=None):
    """Rótulo de eixo em EUR: 0, 1 mil, 100 mil, 1 mi, 100 mi."""
    if x == 0:
        return "0"
    if abs(x) >= 1e6:
        return milhoes(x)
    if abs(x) >= 1e3:
        return f"{br(x / 1e3)} mil"
    return br(x)


def tempo_ms(ms):
    if ms >= 1000:
        return f"{br(ms)} ms (≈ {br(ms / 1000)} s)"
    return f"{br(ms, 1)} ms"


def resumo_camadas(camadas):
    """Fração dos alcançados nos níveis 2 a 4 e fração até o nível 5."""
    c = np.asarray(camadas, dtype=float)
    n = c.sum()
    return c[2:5].sum() / n, c[:6].sum() / n


def salvar(fig, caminho):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return caminho


def rodape(fig, texto):
    fig.text(0.01, -0.02, texto, fontsize=8, color=TEXTO_2, ha="left", va="top")


def rotular_sem_sobrepor(ax, pontos, evitar=()):
    """Anota cada ponto na primeira posição candidata em que o texto não cobre outro rótulo,
    a legenda, nem sai do eixo."""
    fig = ax.figure
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    caixa_eixo = ax.get_window_extent(r)
    ocupados = [e.get_window_extent(r) for e in evitar]
    candidatos = [(-7, 7, "right"), (7, 7, "left"), (-7, -9, "right"), (7, -9, "left"),
                  (-7, 18, "right"), (7, 18, "left"), (0, 20, "center"), (0, -20, "center")]

    def anotar(x, y, texto, dx, dy, ha):
        return ax.annotate(texto, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center",
                           fontsize=8, color=TEXTO, path_effects=[withStroke(linewidth=2.5, foreground="white")])

    for x, y, texto in pontos:
        for dx, dy, ha in candidatos:
            a = anotar(x, y, texto, dx, dy, ha)
            caixa = a.get_window_extent(r)
            dentro = (caixa.x0 >= caixa_eixo.x0 and caixa.x1 <= caixa_eixo.x1
                      and caixa.y0 >= caixa_eixo.y0 and caixa.y1 <= caixa_eixo.y1)
            if dentro and not any(caixa.overlaps(o) for o in ocupados):
                break
            a.remove()
        else:
            a = anotar(x, y, texto, *candidatos[0])
            caixa = a.get_window_extent(r)
        ocupados.append(caixa)


# --- exploratórias ---

def graus(d, saida):
    a = d.arcos
    nos = sorted(set(a["origem"]) | set(a["destino"]))
    series = {
        "grau de saída (clubes para onde vende)": a.groupby("origem").size().reindex(nos, fill_value=0),
        "grau de entrada (clubes de quem compra)": a.groupby("destino").size().reindex(nos, fill_value=0),
    }
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for (rotulo, s), cor in zip(series.items(), CORES):
        valores = np.sort(s[s > 0].to_numpy())
        ccdf = (len(valores) - np.arange(len(valores))) / len(s)
        ax.step(valores, ccdf, where="post", color=cor, lw=2, label=rotulo)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=1))
    ax.set_xlabel("grau k (escala log)")
    ax.set_ylabel("% dos clubes com grau ≥ k (escala log)")
    ax.set_title(f"Graus da rede de transferências: poucos clubes concentram as conexões\n"
                 f"{len(nos):,} clubes · {len(a):,} arcos".replace(",", "."))
    ax.legend(loc="lower left")
    rodape(fig, "Grau = número de clubes distintos (arcos), não de transferências. Clubes com grau 0 contam no "
                "denominador. Fonte: Transfermarkt Datasets, recorte do grupo.")
    return salvar(fig, Path(saida) / "e1_graus.png")


def pesos(t, saida):
    fig, eixos = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    # o menor |peso| diferente de zero no recorte é 1 mil; a partir daí a escala é log e os bins
    # têm a mesma largura na tela. A faixa linear fica só entre −1 mil e +1 mil, e o bin central
    # [−500, 500) contém apenas as transferências de peso exatamente zero.
    linthresh = 1e3
    bordas = np.concatenate([-np.logspace(8.4, 3, 28), [-500, 500], np.logspace(3, 8.4, 28)])
    ticks = [-1e8, -1e6, -1e4, 0, 1e4, 1e6, 1e8]
    grupos = [("saída gratuita (valor pago = 0): peso = − valor de mercado", t[t["gratuita"]], DESTAQUE),
              ("venda paga: peso = valor pago − valor de mercado", t[~t["gratuita"]], CORES[0])]
    for ax, (rotulo, g, cor) in zip(eixos, grupos):
        ax.hist(g["peso"], bins=bordas, color=cor, edgecolor="white", linewidth=0.5)
        ax.set_xscale("symlog", linthresh=linthresh, linscale=0.5)
        ax.axvline(0, color=TEXTO, lw=1)
        neg = (g["peso"] < 0).mean()
        ax.set_title(f"{rotulo} · {br(len(g))} transferências · {pct(neg)} negativas",
                     fontsize=10, color=TEXTO_2)
        ax.set_ylabel("transferências")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: br(v)))
    pagas = grupos[1][1]
    zero = int((pagas["peso"] == 0).sum())
    eixos[1].annotate(f"{br(zero)} vendas pagas exatamente\npelo valor de mercado (peso 0)", (0, zero),
                      xytext=(28, 22), textcoords="offset points", fontsize=8, color=TEXTO_2, ha="left",
                      arrowprops={"arrowstyle": "-", "color": TEXTO_2, "lw": 0.7})
    eixos[1].xaxis.set_major_locator(FixedLocator(ticks))
    eixos[1].xaxis.set_major_formatter(FuncFormatter(eur))
    eixos[1].xaxis.set_minor_locator(FixedLocator([s * 10 ** k for s in (-1, 1) for k in range(3, 9)]))
    eixos[1].xaxis.set_minor_formatter(NullFormatter())
    eixos[1].set_xlim(-2.5e8, 2.5e8)
    eixos[1].set_xlabel("peso da transferência em EUR (escala symlog: logarítmica a partir de ±1 mil)")
    fig.suptitle("Distribuição dos pesos: a maior parte da rede é negativa", x=0.01, ha="left",
                 fontsize=12, color=TEXTO)
    fig.tight_layout()
    rodape(fig, "Peso negativo = o jogador saiu por menos que o valor de mercado. Fonte: Transfermarkt Datasets.")
    return salvar(fig, Path(saida) / "e2_pesos.png")


def faltantes(d, saida):
    b = d.brutas.assign(temporada=d.brutas["transfer_season"].map(temporada))
    b = b[b["temporada"].between(2000, 2025)]
    faltas = b.groupby("temporada")[["transfer_fee", "market_value_in_eur"]].apply(lambda x: x.isna().mean())
    mv, fee = faltas["market_value_in_eur"], faltas["transfer_fee"]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    for col, rotulo, cor in (("market_value_in_eur", "valor de mercado", CORES[0]),
                             ("transfer_fee", "valor pago", CORES[1])):
        ax.plot(faltas.index, faltas[col], color=cor, lw=2, marker="o", ms=4, label=rotulo)
        ax.annotate(f"{rotulo}: {pct(faltas[col].iloc[-1])}", (faltas.index[-1], faltas[col].iloc[-1]),
                    xytext=(6, 0), textcoords="offset points", va="center", color=TEXTO_2)
    ax.set_ylim(0, 1.02)
    ax.yaxis.set_major_formatter(FuncFormatter(pct_eixo))
    ax.set_xlabel("temporada (ano de início)")
    ax.set_ylabel("% das transferências sem o valor")
    ax.set_title("Faltantes por temporada: os dois valores faltam menos quanto mais recente a transferência\n"
                 f"valor de mercado: {pct(mv.iloc[0])} em {mv.index[0]} → {pct(mv.iloc[-1])} em {mv.index[-1]}; "
                 f"valor pago: {pct(fee.iloc[0])} → {pct(fee.iloc[-1])}")
    ax.legend(loc="upper right")
    rodape(fig, f"Sobre as {br(len(b))} transferências brutas das temporadas 2000/01 a 2025/26 "
                f"({br(len(d.brutas))} no arquivo). Sem os dois valores não existe peso, então essas "
                "transferências ficam fora do grafo. Fonte: Transfermarkt Datasets.")
    return salvar(fig, Path(saida) / "e3_faltantes.png")


def relacoes(t, saida):
    paineis = [
        ("faixa_idade", "idade na transferência", None),
        ("position", "posição", {"Attack": "atacante", "Midfield": "meio-campo", "Defender": "defensor",
                                 "Goalkeeper": "goleiro"}),
        ("foot", "pé preferido", {"right": "direito", "left": "esquerdo", "both": "ambos"}),
        ("tem_empresario", "empresário", None),
    ]
    media = t["negativo"].mean()
    grupos = []
    for col, titulo, nomes in paineis:
        g = t.groupby(col, observed=True).agg(neg=("negativo", "mean"), n=("negativo", "size"))
        if col != "faixa_idade":
            g = g.sort_values("neg")
        grupos.append((titulo, nomes, g))
    # painéis empilhados com o mesmo eixo x; a altura de cada um segue o número de categorias
    alturas = [len(g) + 0.9 for _, _, g in grupos]
    fig, eixos = plt.subplots(len(grupos), 1, figsize=(8.5, 0.38 * sum(alturas) + 1.2), sharex=True,
                              gridspec_kw={"height_ratios": alturas})
    for ax, (titulo, nomes, g) in zip(eixos, grupos):
        rotulos = [(nomes or {}).get(str(i), str(i)) for i in g.index]
        y = np.arange(len(g))
        ax.hlines(y, 0, g["neg"], color=GRADE, lw=2)
        ax.plot(g["neg"], y, "o", color=CORES[0], ms=8)
        for yi, (v, n) in enumerate(zip(g["neg"], g["n"])):
            ax.text(v + 0.012, yi, f"{pct(v)}  (n={br(n)})", va="center", fontsize=8.5, color=TEXTO_2,
                    clip_on=False)
        ax.axvline(media, color=TEXTO_2, ls="--", lw=1)
        ax.set_yticks(y, rotulos)
        ax.set_ylim(-0.7, len(g) - 0.3)
        ax.set_title(titulo, fontsize=10.5)
        ax.grid(axis="y", visible=False)
    eixos[0].annotate(f"média geral: {pct(media)}", (media, 1), xycoords=("data", "axes fraction"),
                      xytext=(4, -1), textcoords="offset points", va="top", fontsize=8, color=TEXTO_2)
    eixos[-1].set_xlim(0.5, 1.0)
    eixos[-1].xaxis.set_major_formatter(FuncFormatter(pct_eixo))
    eixos[-1].set_xlabel("% das transferências com peso negativo (saída abaixo do valor de mercado)")
    fig.suptitle("Relação do peso com os atributos do jogador: a idade é o que mais separa",
                 x=0.01, ha="left", fontsize=12, color=TEXTO)
    fig.tight_layout()
    rodape(fig, f"Linha tracejada: média geral ({pct(media)}). Posição, pé e empresário vêm de players.csv; "
                "faltantes desses atributos (≤ 2,3%, empresário 32,8%) aparecem como categoria ou ficam fora do painel.")
    return salvar(fig, Path(saida) / "e4_relacoes.png")


def outliers(t, saida):
    pagas = t[~t["gratuita"]].copy()
    pagas["log_razao"] = np.log10(pagas["razao"])
    lim = iqr(pagas["log_razao"])
    fora = (pagas["log_razao"] < lim["limite_inferior"]) | (pagas["log_razao"] > lim["limite_superior"])
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    ax.scatter(pagas.loc[~fora, "market_value_in_eur"], pagas.loc[~fora, "transfer_fee"], s=6, alpha=0.25,
               color=NEUTRO, linewidths=0, label=f"dentro do IQR ({br((~fora).sum())})")
    ax.scatter(pagas.loc[fora, "market_value_in_eur"], pagas.loc[fora, "transfer_fee"], s=10, alpha=0.7,
               color=DESTAQUE, linewidths=0, label=f"outlier pela regra do IQR ({br(fora.sum())})")
    x = np.array([1e4, 3e8])
    ax.plot(x, x, color=TEXTO, lw=1, ls="--", label="valor pago = valor de mercado (peso 0)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(eur))
    ax.yaxis.set_major_formatter(FuncFormatter(eur))
    ax.set_xlabel("valor de mercado (EUR, escala log)")
    ax.set_ylabel("valor pago (EUR, escala log)")
    ax.set_title("Outliers nas vendas pagas: valor pago contra valor de mercado\n"
                 "acima da diagonal, pagou-se mais que o mercado; abaixo, menos")
    legenda = ax.legend(loc="upper left", markerscale=2)
    maiores = pagas.reindex(pagas["peso"].abs().sort_values(ascending=False).index).head(5)
    rotular_sem_sobrepor(ax, [(r.market_value_in_eur, r.transfer_fee, r.player_name) for r in maiores.itertuples()],
                         evitar=[legenda])
    rodape(fig, f"IQR sobre log10(valor pago / valor de mercado): fora de [{br(lim['limite_inferior'], 2)}; "
                f"{br(lim['limite_superior'], 2)}]. Nomes: as 5 maiores diferenças em módulo. "
                f"{br(len(pagas))} vendas pagas.")
    return salvar(fig, Path(saida) / "e5_outliers.png")


# --- explanatórias ---

def explanatoria_caminho(relatorio, saida):
    bf = relatorio["bellman_ford"]["sem_ciclo_negativo"]
    menor = bf["menor_custo"]
    rota = menor["caminho"]
    trans = menor["transferencias"]
    custos, rotulos, acumulado = [0], [rota[0]], 0
    passos = []
    for u, v in zip(rota, rota[1:]):
        chave = f"{u} -> {v}"
        if chave in trans:
            valor = sum(int(x.rsplit(": ", 1)[1].replace(".", "")) for x in trans[chave])
            jogador = trans[chave][0].split(" (")[0]
            passos.append((v, valor, jogador))
            acumulado += valor
            custos.append(acumulado)
            rotulos.append(v)
    assert acumulado == menor["custo"], (acumulado, menor["custo"])

    maior = min(passos, key=lambda p: p[1])
    fig, ax = plt.subplots(figsize=(10, 5.4))
    x = np.arange(len(custos))
    ax.step(x, custos, where="post", color=NEUTRO, lw=2)
    ax.plot(x, custos, "o", color=NEUTRO, ms=7)
    i = [p[0] for p in passos].index(maior[0]) + 1
    ax.plot(i, custos[i], "o", color=DESTAQUE, ms=10)
    ax.vlines(i, custos[i], custos[i - 1], color=DESTAQUE, lw=3.2)
    ax.annotate(f"{maior[2]}: {milhoes(maior[1])}\n{maior[1] / menor['custo']:.0%} do custo do caminho inteiro",
                (i, (custos[i] + custos[i - 1]) / 2), xytext=(14, 0), textcoords="offset points",
                va="center", fontsize=10.5, color=TEXTO, fontweight="bold")
    for xi, (clube, valor, jogador) in enumerate(passos, start=1):
        if clube != maior[0]:
            ax.annotate(f"{jogador}\n{milhoes(valor)}", (xi, custos[xi]), xytext=(0, -24),
                        textcoords="offset points", ha="center", va="top", fontsize=7.5, color=TEXTO_2)
    ax.set_xticks(x, [r.replace(" (", "\n(") for r in rotulos], fontsize=8)
    ax.yaxis.set_major_formatter(FuncFormatter(milhoes))
    ax.set_ylabel("custo acumulado do caminho (EUR)")
    ax.set_xlabel("clube e temporada ao longo do caminho (as temporadas de espera foram omitidas)")
    ax.set_title(f"Uma só saída abaixo do valor de mercado define o caminho mais barato\n"
                 f"Bellman-Ford no grafo temporal a partir de {rota[0]}: custo total {milhoes(menor['custo'])} "
                 f"até {rota[-1]}", fontsize=12)
    ax.set_ylim(min(custos) * 1.25, max(custos) + 3e7)
    rodape(fig, "Cada degrau é uma transferência (peso = valor pago − valor de mercado, somado no par e na temporada). "
                "Grafo temporal: nó = (clube, temporada), sem ciclos. Fonte: Transfermarkt Datasets.")
    return salvar(fig, Path(saida) / "x1_explanatoria_caminho.png")


def explanatoria_ligas(t, saida):
    g = t.groupby("liga").agg(neg=("negativo", "mean"), n=("negativo", "size"), mediana=("peso", "median"))
    g = g[g["n"] >= 300].sort_values("neg")
    destaque = g.index[0]
    fig, ax = plt.subplots(figsize=(9, 6.2))
    y = np.arange(len(g))
    cores = [DESTAQUE if i == destaque else NEUTRO for i in g.index]
    ax.barh(y, g["neg"], color=cores, height=0.7)
    for yi, (liga, r) in enumerate(g.iterrows()):
        ax.text(r["neg"] + 0.01, yi, f"{r['neg']:.0%}", va="center", fontsize=8.5,
                color=TEXTO if liga == destaque else TEXTO_2, fontweight="bold" if liga == destaque else "normal")
    ax.set_yticks(y, [LIGAS.get(i, i) for i in g.index])
    ax.axvline(0.5, color=TEXTO_2, lw=1, ls="--")
    ax.text(0.5, len(g) - 0.4, " metade", color=TEXTO_2, fontsize=8, va="bottom")
    ax.set_xlim(0, 1.05)
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.set_xlabel("% das transferências com peso negativo (saída abaixo do valor de mercado)")
    ax.grid(axis="y", visible=False)
    r = g.loc[destaque]
    sinal = "+" if r["mediana"] > 0 else ""
    ax.set_title(f"Só a {LIGAS.get(destaque, destaque)} compra, em geral, acima do valor de mercado\n"
                 f"{r['neg']:.0%} das transferências para lá têm peso negativo; mediana do peso "
                 f"{sinal}{br(r['mediana'] / 1e3)} mil EUR", fontsize=12)
    rodape(fig, "Liga do clube de destino (clubs.csv); ligas com pelo menos 300 transferências no recorte. "
                "'Fora das ligas cobertas' = destino fora das ligas que o dataset acompanha. Fonte: Transfermarkt Datasets.")
    return salvar(fig, Path(saida) / "x2_explanatoria_ligas.png")


# --- algoritmos ---

NOMES_ALG = {"BFS": "BFS", "DFS": "DFS", "DIJKSTRA": "Dijkstra", "BELLMAN_FORD": "Bellman-Ford"}


def cor_do_algoritmo(alg):
    return CORES[list(NOMES_ALG).index(alg)]


def tempos(relatorio, saida):
    linhas = [l for l in relatorio["desempenho"] if l["tamanho_pct"] == 100]
    linhas.sort(key=lambda l: l["media_s"])
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    y = np.arange(len(linhas))
    ms = np.array([l["media_s"] * 1000 for l in linhas])
    desvio = np.array([l["desvio_s"] * 1000 for l in linhas])
    # pontos, não barras: numa escala log o comprimento de uma barra não representa nada
    ax.set_xscale("log")
    ax.set_xlim(1, 2e5)
    ax.hlines(y, 1, 2e5, color=GRADE, lw=1)
    for yi, l in zip(y, linhas):
        ax.errorbar(ms[yi], yi, xerr=desvio[yi], fmt="o", ms=10, color=cor_do_algoritmo(l["algoritmo"]),
                    ecolor=TEXTO_2, capsize=4, elinewidth=1, zorder=3)
    base = ms[0]
    for yi, l in enumerate(linhas):
        razao = ms[yi] / base
        texto = tempo_ms(ms[yi]) if yi == 0 else f"{tempo_ms(ms[yi])} · {br(razao, 1 if razao < 100 else 0)}× a {NOMES_ALG[linhas[0]['algoritmo']]}"
        ax.text(ms[yi] * 1.7 + desvio[yi], yi, texto, va="center", fontsize=9, color=TEXTO)
    ax.set_xticks([1, 10, 100, 1e3, 1e4, 1e5], ["1 ms", "10 ms", "100 ms", "1 s", "10 s", "100 s"])
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_yticks(y, [f"{NOMES_ALG[l['algoritmo']]}\n{l['tarefa']}" for l in linhas], fontsize=8.5)
    ax.set_ylim(-0.6, len(linhas) - 0.4)
    ax.set_xlabel("tempo médio por execução (escala log); ponto = média, barra = desvio padrão")
    ax.grid(axis="y", visible=False)
    l0 = linhas[0]
    ax.set_title(f"Tempo dos quatro algoritmos no grafo completo ({br(l0['V'])} clubes, {br(l0['E'])} arcos)\n"
                 f"média de {l0['execucoes']} execuções")
    rodape(fig, "Bellman-Ford com pesos originais: o ciclo negativo impede a parada antecipada, então ele faz as |V| − 1 "
                "passadas. Medido com time.perf_counter em Python 3.")
    return salvar(fig, Path(saida) / "a1_tempos.png")


def escalabilidade(relatorio, saida):
    esc = relatorio["escalabilidade"]
    fig, eixos = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    for ax, (alg, cor) in zip(eixos.flat, zip(NOMES_ALG, CORES)):
        s = [l for l in esc if l["algoritmo"] == alg]
        x = [l["tamanho_pct"] for l in s]
        ax.plot(x, [l["tempo_relativo"] for l in s], "o-", color=cor, lw=2, ms=7, label="tempo medido")
        ax.plot(x, [l["teoria_relativa"] for l in s], "--", color=TEXTO_2, lw=1.4, label=s[0]["complexidade"])
        ax.set_yscale("log")
        ax.set_title(f"{NOMES_ALG[alg]} · {s[0]['complexidade']}", fontsize=10.5)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
        ax.legend(loc="lower right", fontsize=8.5)
        ax.set_xticks(x, [f"{p}%\n|V|={l['V']:,}\n|E|={l['E']:,}".replace(",", ".") for p, l in zip(x, s)],
                      fontsize=7.5)
    for ax in eixos[:, 0]:
        ax.set_ylabel("relativo ao grafo completo (= 1), escala log")
    for ax in eixos[1]:
        ax.set_xlabel("tamanho do grafo (% dos nós sorteados; subgrafo induzido)")
    fig.suptitle("Escalabilidade: o crescimento do tempo medido acompanha a complexidade teórica",
                 x=0.01, ha="left", fontsize=12, color=TEXTO)
    fig.tight_layout()
    rodape(fig, "Curvas normalizadas pelo valor no grafo completo, para comparar formas de crescimento. "
                "Amostras encaixadas de nós (semente 42); média de 5 execuções por ponto.")
    return salvar(fig, Path(saida) / "a2_escalabilidade.png")


def camadas_bfs(relatorio, saida):
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    resumos = []
    for b, cor in zip(relatorio["bfs"], CORES):
        ax.plot(range(len(b["camadas"])), b["camadas"], "o-", color=cor, lw=2, ms=6,
                label=f"{b['nome']} · {br(b['alcancados'])} alcançados")
        resumos.append(resumo_camadas(b["camadas"]))
    meio = [r[0] for r in resumos]
    ate5 = [r[1] for r in resumos]
    ax.set_xticks(range(max(len(b["camadas"]) for b in relatorio["bfs"])))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: br(v)))
    ax.set_xlabel("nível da BFS (número de transferências desde a fonte)")
    ax.set_ylabel("clubes descobertos no nível")
    ax.set_title("BFS a partir de três clubes: a rede é um 'mundo pequeno'\n"
                 f"{pct(min(meio))}–{pct(max(meio))} dos clubes alcançáveis estão a 2–4 transferências da fonte; "
                 f"{pct(min(ate5))}–{pct(max(ate5))} a até 5")
    ax.legend()
    rodape(fig, "Os três chegam aos mesmos clubes: a fonte muda a forma das camadas, não o conjunto alcançável.")
    return salvar(fig, Path(saida) / "a3_camadas_bfs.png")


# [IA] Claude Code (Claude Opus 5.5) – comparação dos caminhos do Dijkstra com os da BFS nos pares do relatório; revisado por Caio
def caminhos(relatorio, saida):
    dij = relatorio["dijkstra"]
    pares = [p for p in dij["pares"] if p["status"] == "OK"]
    pares.sort(key=lambda p: p["custo_original"])
    desloc = dij["transformacao"]["deslocamento_eur"]
    iguais = sum(p["arcos"] == p["passos_bfs"] for p in pares)

    fig, ax = plt.subplots(figsize=(10, 0.62 * len(pares) + 1.6))
    y = np.arange(len(pares))
    custos = [p["custo_original"] for p in pares]
    ax.barh(y, custos, color=CORES[2], height=0.55)
    ax.axvline(0, color=TEXTO_2, lw=1)
    for yi, p in enumerate(pares):
        ax.text(p["custo_original"] * 1.02, yi, f"{milhoes(p['custo_original'])}", ha="right", va="center",
                fontsize=9, color=TEXTO)
        ax.text(0.02 * max(abs(c) for c in custos), yi,
                f"{' → '.join(p['caminho'])}   ·   Dijkstra: {p['arcos']} arcos · BFS: {p['passos_bfs']} passos",
                ha="left", va="center", fontsize=8.5, color=TEXTO_2)
    ax.set_yticks(y, [f"{p['origem']} → {p['destino']}" for p in pares], fontsize=9)
    ax.set_xlim(min(custos) * 1.35, abs(min(custos)) * 1.6)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: milhoes(v) if v else "0"))
    ax.set_xlabel("custo original do caminho do Dijkstra (soma de valor pago − valor de mercado, EUR)")
    ax.grid(axis="y", visible=False)
    ax.set_title(f"Caminhos do Dijkstra contra a BFS: em {iguais} de {len(pares)} pares, "
                 f"o caminho mais barato tem o mesmo número de arcos que o mais curto\n"
                 f"o deslocamento de {milhoes(desloc)} por arco pesa mais que a diferença entre as transferências")
    rodape(fig, f"Dijkstra no grafo de clubes com w' = w + {milhoes(desloc)} (todo peso ≥ 0); o custo mostrado é o "
                f"original. BFS = menor número de transferências entre os mesmos clubes. Bellman-Ford não tem "
                f"caminho mínimo aqui: o grafo de clubes tem ciclo negativo (ver o relatório).")
    return salvar(fig, Path(saida) / "a4_caminhos.png")


def gerar_todas(dataset, saida):
    d = carregar_dataset(dataset)
    t = enriquecer(d, dataset)
    relatorio = json.loads((Path(saida) / "parte2_report.json").read_text(encoding="utf-8"))
    return [
        graus(d, saida), pesos(t, saida), faltantes(d, saida), relacoes(t, saida), outliers(t, saida),
        explanatoria_caminho(relatorio, saida), explanatoria_ligas(t, saida),
        tempos(relatorio, saida), escalabilidade(relatorio, saida), camadas_bfs(relatorio, saida),
        caminhos(relatorio, saida),
    ]


def main(argv=None):
    p = argparse.ArgumentParser(description="Gráficos da Parte 2.")
    p.add_argument("--dataset", default="data/dataset_parte2")
    p.add_argument("--out", default="out/parte2")
    args = p.parse_args(argv)
    for caminho in gerar_todas(args.dataset, args.out):
        print(caminho)


if __name__ == "__main__":
    main()
