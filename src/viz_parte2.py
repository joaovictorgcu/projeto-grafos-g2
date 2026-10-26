"""Gráficos da Parte 2. Precisa do out/parte2/parte2_report.json (rode o --benchmark antes)."""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, PercentFormatter

from .avd_parte2 import SEM_LIGA, enriquecer, iqr
from .graphs.dataset import carregar_dataset, temporada

CORES = ["#2a78d6", "#eb6834", "#1baf7a", "#e87ba4"]
DESTAQUE = "#eb6834"
NEUTRO = "#b9b8b3"
TEXTO = "#0b0b0b"
TEXTO_2 = "#52514e"
GRADE = "#e4e3df"

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


def br(n):
    return f"{n:,.0f}".replace(",", ".")


def milhoes(x, _=None):
    return f"{br(x / 1e6)} mi"


def salvar(fig, caminho):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return caminho


def rodape(fig, texto):
    fig.text(0.01, -0.02, texto, fontsize=8, color=TEXTO_2, ha="left", va="top")


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
    fig, eixos = plt.subplots(2, 1, figsize=(8.5, 5.6), sharex=True)
    limite = 2e8
    bordas = np.concatenate([-np.logspace(8.4, 3, 28), [0], np.logspace(3, 8.4, 28)])
    grupos = [("saída gratuita (valor pago = 0): peso = − valor de mercado", t[t["gratuita"]], CORES[1]),
              ("venda paga: peso = valor pago − valor de mercado", t[~t["gratuita"]], CORES[0])]
    for ax, (rotulo, g, cor) in zip(eixos, grupos):
        ax.hist(g["peso"].clip(-limite, limite), bins=bordas, color=cor, edgecolor="white", linewidth=0.5)
        ax.set_xscale("symlog", linthresh=1e5)
        ax.axvline(0, color=TEXTO, lw=1)
        neg = (g["peso"] < 0).mean()
        ax.set_title(f"{rotulo} · {len(g):,} transferências · {neg:.0%} negativas".replace(",", "."),
                     fontsize=10, color=TEXTO_2)
        ax.set_ylabel("transferências")
    eixos[1].xaxis.set_major_formatter(FuncFormatter(lambda x, _: milhoes(x) if abs(x) >= 1e6 else f"{x:,.0f}".replace(",", ".")))
    eixos[1].set_xlabel("peso da transferência em EUR (escala symlog: linear entre −100 mil e +100 mil)")
    fig.suptitle("Distribuição dos pesos: a maior parte da rede é negativa", x=0.01, ha="left",
                 fontsize=12, color=TEXTO)
    fig.tight_layout()
    rodape(fig, "Peso negativo = o jogador saiu por menos que o valor de mercado. Fonte: Transfermarkt Datasets.")
    return salvar(fig, Path(saida) / "e2_pesos.png")


def faltantes(d, saida):
    b = d.brutas.assign(temporada=d.brutas["transfer_season"].map(temporada))
    b = b[b["temporada"].between(2000, 2025)]
    pct = b.groupby("temporada")[["transfer_fee", "market_value_in_eur"]].apply(lambda x: x.isna().mean())
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    for col, rotulo, cor in (("market_value_in_eur", "valor de mercado", CORES[0]),
                             ("transfer_fee", "valor pago", CORES[1])):
        ax.plot(pct.index, pct[col], color=cor, lw=2, marker="o", ms=4, label=rotulo)
        ax.annotate(rotulo, (pct.index[-1], pct[col].iloc[-1]), xytext=(6, 0), textcoords="offset points",
                    va="center", color=TEXTO_2)
    ax.set_ylim(0, 1.02)
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_xlabel("temporada (ano de início)")
    ax.set_ylabel("% das transferências sem o valor")
    ax.set_title("Faltantes por temporada: o valor de mercado some quanto mais antiga a transferência;\n"
                 "o valor pago falta em cerca de 1/3 das transferências em todas as épocas")
    ax.legend(loc="upper right")
    rodape(fig, "Sobre as 175.165 transferências brutas, temporadas 2000/01 a 2025/26. Sem os dois valores não "
                "existe peso, então essas transferências ficam fora do grafo. Fonte: Transfermarkt Datasets.")
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
    fig, eixos = plt.subplots(2, 2, figsize=(10, 6.4))
    for ax, (col, titulo, nomes) in zip(eixos.flat, paineis):
        g = t.groupby(col, observed=True).agg(neg=("negativo", "mean"), n=("negativo", "size"))
        if col != "faixa_idade":
            g = g.sort_values("neg")
        rotulos = [(nomes or {}).get(str(i), str(i)) for i in g.index]
        y = np.arange(len(g))
        ax.hlines(y, 0, g["neg"], color=GRADE, lw=2)
        ax.plot(g["neg"], y, "o", color=CORES[0], ms=8)
        for yi, (v, n) in enumerate(zip(g["neg"], g["n"])):
            ax.text(v + 0.012, yi, f"{v:.0%}  (n={n:,})".replace(",", "."), va="center", fontsize=8.5,
                    color=TEXTO_2, clip_on=False)
        ax.axvline(media, color=TEXTO_2, ls="--", lw=1)
        ax.set_yticks(y, rotulos)
        ax.set_xlim(0.5, 1.0)
        ax.xaxis.set_major_formatter(PercentFormatter(1))
        ax.set_title(titulo, fontsize=10.5)
        ax.grid(axis="y", visible=False)
    for ax in eixos[1]:
        ax.set_xlabel("% das transferências com peso negativo")
    fig.suptitle("Relação do peso com os atributos do jogador: a idade é o que mais separa",
                 x=0.01, ha="left", fontsize=12, color=TEXTO)
    fig.tight_layout()
    rodape(fig, f"Linha tracejada: média geral ({media:.0%}). Posição, pé e empresário vêm de players.csv; "
                "faltantes desses atributos (≤ 2,3%, empresário 32,8%) aparecem como categoria ou ficam fora do painel.")
    return salvar(fig, Path(saida) / "e4_relacoes.png")


def outliers(t, saida):
    pagas = t[~t["gratuita"]].copy()
    pagas["log_razao"] = np.log10(pagas["razao"])
    lim = iqr(pagas["log_razao"])
    fora = (pagas["log_razao"] < lim["limite_inferior"]) | (pagas["log_razao"] > lim["limite_superior"])
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    ax.scatter(pagas.loc[~fora, "market_value_in_eur"], pagas.loc[~fora, "transfer_fee"], s=6, alpha=0.25,
               color=NEUTRO, linewidths=0, label=f"dentro do IQR ({(~fora).sum():,})".replace(",", "."))
    ax.scatter(pagas.loc[fora, "market_value_in_eur"], pagas.loc[fora, "transfer_fee"], s=10, alpha=0.7,
               color=DESTAQUE, linewidths=0, label=f"outlier pela regra do IQR ({fora.sum():,})".replace(",", "."))
    x = np.array([1e4, 3e8])
    ax.plot(x, x, color=TEXTO, lw=1, ls="--", label="valor pago = valor de mercado (peso 0)")
    for r in pagas.reindex(pagas["peso"].abs().sort_values(ascending=False).index).head(5).itertuples():
        ax.annotate(r.player_name, (r.market_value_in_eur, r.transfer_fee), xytext=(-6, 6),
                    textcoords="offset points", ha="right", fontsize=8, color=TEXTO)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(milhoes_ou_mil))
    ax.yaxis.set_major_formatter(FuncFormatter(milhoes_ou_mil))
    ax.set_xlabel("valor de mercado (EUR, escala log)")
    ax.set_ylabel("valor pago (EUR, escala log)")
    ax.set_title("Outliers nas vendas pagas: valor pago contra valor de mercado\n"
                 "acima da diagonal, pagou-se mais que o mercado; abaixo, menos")
    ax.legend(loc="upper left", markerscale=2)
    rodape(fig, f"IQR sobre log10(valor pago / valor de mercado): fora de [{lim['limite_inferior']:.2f}; "
                f"{lim['limite_superior']:.2f}]. Nomes: as 5 maiores diferenças em módulo. "
                f"{br(len(pagas))} vendas pagas.")
    return salvar(fig, Path(saida) / "e5_outliers.png")


def milhoes_ou_mil(x, _=None):
    if x >= 1e6:
        return f"{x / 1e6:g} mi"
    return f"{x / 1e3:g} mil"


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


NOMES_ALG = {"BFS": "BFS", "DFS": "DFS", "DIJKSTRA": "Dijkstra", "BELLMAN_FORD": "Bellman-Ford"}


def tempos(relatorio, saida):
    linhas = [l for l in relatorio["desempenho"] if l["tamanho_pct"] == 100]
    linhas.sort(key=lambda l: l["media_s"])
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    y = np.arange(len(linhas))
    ms = [l["media_s"] * 1000 for l in linhas]
    ax.barh(y, ms, xerr=[l["desvio_s"] * 1000 for l in linhas], color=[CORES[list(NOMES_ALG).index(l["algoritmo"])]
                                                                      for l in linhas],
            height=0.6, error_kw={"ecolor": TEXTO_2, "capsize": 3, "lw": 1})
    for yi, (v, l) in enumerate(zip(ms, linhas)):
        ax.text((v + l["desvio_s"] * 1000) * 1.15, yi, f"{v:,.1f} ms".replace(",", "X").replace(".", ",").replace("X", "."),
                va="center", fontsize=9, color=TEXTO)
    ax.set_xscale("log")
    ax.set_yticks(y, [f"{NOMES_ALG[l['algoritmo']]}\n{l['tarefa']}" for l in linhas], fontsize=8.5)
    ax.set_xlim(right=max(ms) * 12)
    ax.set_xlabel("tempo médio por execução (ms, escala log); barra de erro = desvio padrão")
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
    for b, cor in zip(relatorio["bfs"], CORES):
        ax.plot(range(len(b["camadas"])), b["camadas"], "o-", color=cor, lw=2, ms=6,
                label=f"{b['nome']} · {b['alcancados']:,} alcançados".replace(",", "."))
    ax.set_xlabel("nível da BFS (número de transferências desde a fonte)")
    ax.set_ylabel("clubes descobertos no nível")
    ax.set_title("BFS a partir de três clubes: a rede é um 'mundo pequeno'\n"
                 "quase todos os clubes alcançáveis estão a 2-4 transferências de distância")
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
