# [IA] Claude Code (Claude Opus 5.5) – labirinto interativo em Streamlit: escolha de mapa e algoritmo, animação passo a passo, camadas, armadilhas e comparação
import argparse
import io
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from src.graphs.estados import ALVO, construir_estados, metricas
from src.graphs.io import MapaInvalido, interpretar_mapa
from src.viz import (COR_CHAO, COR_TERRENO, COR_TEXTO, COR_TEXTO_2, CORES_CAMADA, caminhos_dos_algoritmos,
                     estados_armadilha, ler_rotulo, titulo_do_mapa)

PASTAS = (RAIZ / "data" / "mapas", RAIZ / "data" / "mapas_grupo")
ALGORITMOS = ("BFS", "DIJKSTRA", "BELLMAN_FORD")
COR_ARMADILHA = "#c62828"
ACOMPANHAR = "acompanhar o passo"
SIMBOLOS_VISIVEIS = "SGabcdABCD+*<>^v"
NOME_ALG = {"BFS": "BFS", "DIJKSTRA": "Dijkstra", "BELLMAN_FORD": "Bellman-Ford"}
MODOS = ("Um algoritmo", "Comparação lado a lado")
COR_LADO = {"A": "#2a78d6", "B": "#eb6834"}
SEM_EXEMPLO = "— escolha um exemplo —"
# (título, lado A, lado B); cada lado é (código do mapa, algoritmo, fonte consumível)
EXEMPLOS = (
    ("m01 · BFS × Dijkstra: menos passos ou menor custo?", ("m01", "BFS", False), ("m01", "DIJKSTRA", False)),
    ("m03 · BFS × Dijkstra com três chaves", ("m03", "BFS", False), ("m03", "DIJKSTRA", False)),
    ("m05 · BFS × Bellman-Ford: o desvio pelos bônus", ("m05", "BFS", False), ("m05", "BELLMAN_FORD", False)),
    ("m05 · Dijkstra × Bellman-Ford: peso negativo", ("m05", "DIJKSTRA", False), ("m05", "BELLMAN_FORD", False)),
    ("m06 · fonte infinita × fonte consumível", ("m06", "BELLMAN_FORD", False), ("m06", "BELLMAN_FORD", True)),
    ("m02 × m07 · com solução e sem solução", ("m02", "BFS", False), ("m07", "BFS", False)),
    ("m08 · BFS × Dijkstra no mapa grande", ("m08", "BFS", False), ("m08", "DIJKSTRA", False)),
)


def ler_argumentos():
    p = argparse.ArgumentParser()
    p.add_argument("--mapa")
    args, _ = p.parse_known_args(sys.argv[1:])
    return args


def mapas_disponiveis(pedido=None):
    opcoes = {}
    for pasta in PASTAS:
        for arquivo in sorted(pasta.glob("*.txt")):
            sufixo = " (grupo)" if pasta.name == "mapas_grupo" else ""
            opcoes[titulo_do_mapa(arquivo) + sufixo] = arquivo
    if not pedido:
        return opcoes, 0
    pedido = Path(pedido)
    for n, arquivo in enumerate(opcoes.values()):
        if arquivo.resolve() == pedido.resolve():
            return opcoes, n
    opcoes[titulo_do_mapa(pedido)] = pedido
    return opcoes, len(opcoes) - 1


def nome_da_camada(chaves):
    return f"chaves {{{','.join(chaves)}}}" if chaves else "sem chaves"


def percorrer(grafo, rotulos):
    passos, total = [], 0
    for i, no in enumerate(rotulos):
        custo = dict(grafo.arcos(rotulos[i - 1]))[no] if i else 0
        total += custo
        pos, chaves, bonus = ler_rotulo(no)
        passos.append({"rotulo": no, "pos": pos, "chaves": chaves, "bonus": bonus, "custo": custo, "total": total})
    return passos


@st.cache_data(show_spinner="Montando o grafo de estados...")
def processar(texto, nome, fonte_consumivel):
    mapa = interpretar_mapa(texto, nome)
    construido = construir_estados(mapa, fonte_consumivel)
    grafo = construido.grafo

    camadas = {}
    for no in grafo.nos():
        if no != ALVO:
            camadas.setdefault(ler_rotulo(no)[1], []).append(no)

    caminhos = {}
    for alg, info in caminhos_dos_algoritmos(construido).items():
        rotulos = [no for no in info["caminho"] if no != ALVO]
        caminhos[alg] = {
            "status": info.get("status", "OK" if rotulos else "SEM_SOLUCAO"),
            "motivo": info.get("motivo", ""),
            "passos": percorrer(grafo, rotulos or [construido.inicial]),
        }

    return {
        "grade": list(mapa.grade),
        "camadas": dict(sorted(camadas.items(), key=lambda par: (len(par[0]), par[0]))),
        "armadilhas": set(estados_armadilha(construido)),
        "caminhos": caminhos,
        "metricas": metricas(construido),
    }


def desenhar_tabuleiro(grade, passos, i, camada, cor, celulas_camada, celulas_armadilha):
    altura, largura = len(grade), len(grade[0])
    lado = min(0.55, 14 / largura)
    fig, ax = plt.subplots(figsize=(max(5.0, largura * lado), max(3.0, altura * lado)))

    terreno = [[to_rgba(COR_TERRENO.get(casa, COR_CHAO)) for casa in linha] for linha in grade]
    destaque = [[to_rgba(cor(camada), 0.22 if (l, c) in celulas_camada else 0) for c in range(largura)]
                for l in range(altura)]
    ax.imshow(terreno, interpolation="nearest", zorder=1)
    ax.imshow(destaque, interpolation="nearest", zorder=2)
    for l, linha in enumerate(grade):
        for c, casa in enumerate(linha):
            if casa in SIMBOLOS_VISIVEIS:
                ax.text(c, l, casa, ha="center", va="center", fontsize=max(5, 20 * lado),
                        fontweight="bold" if casa.isupper() else "normal", color=COR_TEXTO, alpha=0.6, zorder=3)
    if celulas_armadilha:
        ls, cs = zip(*celulas_armadilha)
        ax.scatter(cs, ls, marker="x", s=(30 * lado) ** 2, color=COR_ARMADILHA, linewidths=1.5, zorder=4)

    trechos = [[anterior["pos"][::-1], atual["pos"][::-1]] for anterior, atual in zip(passos[:i], passos[1:i + 1])]
    cores = [cor(anterior["chaves"]) for anterior in passos[:i]]
    ax.add_collection(LineCollection(trechos, colors=cores, linewidths=3, capstyle="round", zorder=5))

    (l, c), chaves = passos[i]["pos"], passos[i]["chaves"]
    ax.plot(c, l, "o", ms=max(6, 26 * lado), color=cor(chaves), mec=COR_TEXTO, mew=1.5, zorder=6)

    ax.set_title(f"passo {i} de {len(passos) - 1} · estado {passos[i]['rotulo']}", fontsize=11,
                 color=COR_TEXTO, loc="left")
    ax.set_xlabel("coluna", color=COR_TEXTO_2)
    ax.set_ylabel("linha", color=COR_TEXTO_2)
    ax.set_xlim(-0.5, largura - 0.5)
    ax.set_ylim(altura - 0.5, -0.5)
    passo_tick = 1 if largura <= 20 else 5
    ax.set_xticks(range(0, largura, passo_tick))
    ax.set_yticks(range(0, altura, passo_tick))
    ax.tick_params(labelsize=8, colors=COR_TEXTO_2, length=0)
    ax.set_aspect("equal")
    for borda in ax.spines.values():
        borda.set_visible(False)

    legenda = [
        Line2D([0], [0], marker="o", ls="", color=cor(chaves), mec=COR_TEXTO, ms=9, label="jogador agora"),
        Line2D([0], [0], color=COR_TEXTO_2, lw=3, label="percurso até aqui (cor = camada)"),
        Patch(facecolor=cor(camada), alpha=0.22, label=f"casas da camada {nome_da_camada(camada)}"),
        Line2D([0], [0], marker="x", ls="", color=COR_ARMADILHA, mew=1.5, ms=8,
               label="estado-armadilha (não chega em G)"),
        Patch(facecolor=COR_TERRENO[","], label="lama (custo 3)"),
        Patch(facecolor=COR_TERRENO["~"], label="água (custo 5)"),
    ]
    ax.legend(handles=legenda, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=False,
              fontsize=8, labelcolor=COR_TEXTO)
    return fig


def mostrar_figura(fig, dpi=110):
    imagem = io.BytesIO()
    fig.savefig(imagem, format="png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    st.image(imagem)


def ir_para(i):
    st.session_state.passo = i
    st.session_state.tocando = False


def reproduzir_ou_pausar(ultimo):
    if st.session_state.passo >= ultimo:
        st.session_state.passo = 0
    st.session_state.tocando = not st.session_state.tocando


def mostrar_status(algoritmo, info, n_estados):
    if info["status"] == "RECUSA":
        st.warning(f"**{algoritmo} recusou o mapa.** {info['motivo']}")
    elif info["status"] == "CICLO_NEGATIVO":
        st.error(f"**{algoritmo} achou um ciclo negativo**, então não existe caminho de menor custo. "
                 f"{info['motivo']}. Experimente marcar *fonte consumível* na barra lateral.")
    elif info["status"] == "SEM_SOLUCAO":
        st.info(f"**Sem solução:** nenhum estado em G é alcançável a partir do início. "
                f"Os {n_estados} estados alcançáveis são armadilhas.")


def tabela_de_comparacao(dados):
    linhas = []
    for alg in ALGORITMOS:
        info = dados["caminhos"][alg]
        ok = info["status"] == "OK"
        linhas.append({
            "algoritmo": alg,
            "status": info["status"],
            "passos": len(info["passos"]) - 1 if ok else None,
            "custo": info["passos"][-1]["total"] if ok else None,
            "chaves coletadas": (info["passos"][-1]["chaves"] or "-") if ok else None,
            "bônus consumidos": len(info["passos"][-1]["bonus"]) if ok else None,
        })
    return pd.DataFrame(linhas).astype({"passos": "Int64", "custo": "Int64", "bônus consumidos": "Int64"})


def ler_mapas(opcoes, enviado):
    """Título -> (nome, texto) de cada mapa disponível, incluindo o enviado, se houver."""
    textos = {}
    for titulo, arquivo in opcoes.items():
        if arquivo.is_file():
            textos[titulo] = (arquivo.stem, arquivo.read_text(encoding="utf-8"))
    if enviado is not None:
        try:
            texto = enviado.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            st.error(f"{enviado.name}: o arquivo não está em UTF-8.")
            st.stop()
        textos = {f"{Path(enviado.name).stem} · enviado": (Path(enviado.name).stem, texto), **textos}
    return textos


def preparar(titulo, nome, texto, fonte_consumivel, algoritmo):
    try:
        dados = processar(texto, nome, fonte_consumivel)
    except MapaInvalido as erro:
        st.error(f"**Mapa inválido ({titulo}).** {erro}")
        st.stop()
    indice = {k: n for n, k in enumerate(dados["camadas"])}
    info = dados["caminhos"][algoritmo]
    return {
        "titulo": titulo, "algoritmo": algoritmo, "fonte": fonte_consumivel, "dados": dados, "info": info,
        "passos": info["passos"], "ultimo": len(info["passos"]) - 1, "ok": info["status"] == "OK",
        "cor": lambda chaves: CORES_CAMADA[indice[chaves] % len(CORES_CAMADA)],
    }


def controles_de_passo(ultimo, tocando_rotulo="▶ Reproduzir"):
    st.slider("Passo", 0, ultimo, key="passo")
    b1, b2, b3, b4 = st.columns(4)
    b1.button("⏮", help="início", on_click=ir_para, args=(0,), width="stretch")
    b2.button("◀", help="voltar um passo", on_click=ir_para,
              args=(max(0, st.session_state.passo - 1),), width="stretch")
    b3.button("▶", help="avançar um passo", on_click=ir_para,
              args=(min(ultimo, st.session_state.passo + 1),), width="stretch")
    b4.button("⏭", help="fim", on_click=ir_para, args=(ultimo,), width="stretch")
    st.button("⏸ Pausar" if st.session_state.tocando else tocando_rotulo, type="primary",
              on_click=reproduzir_ou_pausar, args=(ultimo,), width="stretch")


def reiniciar_se_mudou(chave, ultimo):
    if st.session_state.get("chave") != chave:
        st.session_state.chave = chave
        st.session_state.passo = 0
        st.session_state.tocando = False
    if st.session_state.tocando:
        st.session_state.passo = min(st.session_state.passo + 1, ultimo)
        st.session_state.tocando = st.session_state.passo < ultimo


def modo_um_algoritmo(textos, inicial):
    titulos = list(textos)
    with st.sidebar:
        st.header("Mapa")
        titulo = st.selectbox("Mapa do projeto", titulos, index=min(inicial, len(titulos) - 1))
        fonte_consumivel = st.checkbox("Fonte consumível (* vale −2 só na 1ª passagem)")
        st.header("Algoritmo")
        algoritmo = st.radio("Algoritmo", ALGORITMOS, format_func=NOME_ALG.get, label_visibility="collapsed")

    nome, texto = textos[titulo]
    lado = preparar(titulo, nome, texto, fonte_consumivel, algoritmo)
    dados, info, passos, ultimo, cor = lado["dados"], lado["info"], lado["passos"], lado["ultimo"], lado["cor"]
    reiniciar_se_mudou(("um", titulo, texto, fonte_consumivel, algoritmo), ultimo)
    camadas = dados["camadas"]

    with st.sidebar:
        st.header("Visualização")
        rotulos_camada = {ACOMPANHAR: None}
        rotulos_camada.update({f"{nome_da_camada(k)} · {len(nos)} estados": k for k, nos in camadas.items()})
        vista = st.selectbox("Camada em destaque", list(rotulos_camada))
        ver_armadilhas = st.checkbox("Destacar estados-armadilha", value=True)
        velocidade = st.slider("Velocidade (passos por segundo)", 1, 20, 4)

    atual = passos[st.session_state.passo]
    camada = atual["chaves"] if rotulos_camada[vista] is None else rotulos_camada[vista]
    celulas_camada = {ler_rotulo(no)[0] for no in camadas[camada]}
    celulas_armadilha = {ler_rotulo(no)[0] for no in camadas[camada] if no in dados["armadilhas"]} \
        if ver_armadilhas else set()

    st.title(f"Labirinto interativo · {titulo}")
    mostrar_status(NOME_ALG[algoritmo], info, sum(len(nos) for nos in camadas.values()))

    tabuleiro, painel = st.columns([3, 1])
    with painel:
        if ultimo:
            controles_de_passo(ultimo)
        l, c = atual["pos"]
        st.metric("Posição (linha, coluna)", f"({l}, {c})")
        st.metric("Chaves", ", ".join(atual["chaves"]) or "nenhuma")
        st.metric("Bônus consumidos", ", ".join(map(str, sorted(atual["bonus"]))) or "nenhum")
        st.metric("Custo acumulado", atual["total"], delta=atual["custo"] if st.session_state.passo else None,
                  delta_color="inverse")
        if atual["rotulo"] in dados["armadilhas"]:
            st.error("Este estado é uma armadilha: daqui não dá mais para chegar em G.")

    with tabuleiro:
        mostrar_figura(desenhar_tabuleiro(dados["grade"], passos, st.session_state.passo, camada, cor,
                                          celulas_camada, celulas_armadilha))

    st.subheader("Comparação dos algoritmos")
    st.dataframe(tabela_de_comparacao(dados), hide_index=True)
    m = dados["metricas"]
    e1, e2, e3, e4, e5 = st.columns(5)
    e1.metric("Estados (sem o ALVO)", m["ordem"])
    e2.metric("Arcos (sem os do ALVO)", m["tamanho"])
    e3.metric("Densidade", f"{m['densidade']:.4f}")
    e4.metric("Camadas", len(camadas))
    e5.metric("Estados-armadilha", len(dados["armadilhas"]))
    st.caption("Para ver dois percursos ao mesmo tempo, escolha **Comparação lado a lado** em *Modo*, "
               "na barra lateral.")
    return velocidade


# [IA] Claude Code (Claude Opus 5.5) – modo de comparação lado a lado (bônus): dois percursos sincronizados, sobreposição, curva de custo e passo a passo; revisado por Caio
def aplicar_exemplo(titulos):
    escolhido = st.session_state.cmp_exemplo
    for nome, a, b in EXEMPLOS:
        if nome != escolhido:
            continue
        mapas = {}
        for codigo in (a[0], b[0]):
            mapas[codigo] = next((t for t in titulos if t.startswith(codigo + " ")), None)
        if None in mapas.values():
            return
        st.session_state.cmp_diferentes = a[0] != b[0]
        for lado, (codigo, alg, fonte) in (("a", a), ("b", b)):
            st.session_state[f"cmp_mapa_{lado}"] = mapas[codigo]
            st.session_state[f"cmp_alg_{lado}"] = alg
            st.session_state[f"cmp_fonte_{lado}"] = fonte


def descrever_lado(lado):
    fonte = " · fonte consumível" if lado["fonte"] else ""
    return f"{NOME_ALG[lado['algoritmo']]} em {lado['titulo']}{fonte}"


def no_passo(lado, k):
    """Estado do lado no passo global k: quem já chegou fica parado no último estado."""
    return lado["passos"][min(k, lado["ultimo"])]


def primeira_divergencia(a, b):
    for k, (pa, pb) in enumerate(zip(a["passos"], b["passos"])):
        if pa["rotulo"] != pb["rotulo"]:
            return k
    return None if len(a["passos"]) == len(b["passos"]) else min(len(a["passos"]), len(b["passos"]))


def veredito(a, b):
    """Uma frase com a diferença entre os dois percursos."""
    if not a["ok"] and not b["ok"]:
        return "info", (f"Nenhum dos dois lados tem percurso: A terminou em **{a['info']['status']}** e "
                        f"B em **{b['info']['status']}**.")
    if a["ok"] != b["ok"]:
        bom, ruim, nb, nr = (a, b, "A", "B") if a["ok"] else (b, a, "B", "A")
        return "warning", (f"Só o lado **{nb}** chega em G ({bom['ultimo']} passos, custo "
                           f"{bom['passos'][-1]['total']}). O lado **{nr}** terminou em "
                           f"**{ruim['info']['status']}**.")
    pa, pb = a["ultimo"], b["ultimo"]
    ca, cb = a["passos"][-1]["total"], b["passos"][-1]["total"]
    if [p["rotulo"] for p in a["passos"]] == [p["rotulo"] for p in b["passos"]]:
        return "success", f"Os dois lados fazem **exatamente o mesmo percurso**: {pa} passos, custo {ca}."
    partes = []
    if pa != pb:
        menos, mais = ("A", "B") if pa < pb else ("B", "A")
        n = abs(pa - pb)
        partes.append(f"**{menos}** chega com **{n} passo{'s' if n > 1 else ''} a menos** ({min(pa, pb)} × {max(pa, pb)})")
    else:
        partes.append(f"os dois levam **{pa} passos**, por caminhos diferentes")
    if ca != cb:
        barato = "A" if ca < cb else "B"
        partes.append(f"**{barato}** sai **{abs(ca - cb)} mais barato** (custo {min(ca, cb)} × {max(ca, cb)})")
    else:
        partes.append(f"com o **mesmo custo** ({ca})")
    k = primeira_divergencia(a, b)
    if k is not None:
        partes.append(f"os percursos se separam no passo {k}")
    frase = "; ".join(partes)
    return "success", frase[0].upper() + frase[1:] + "."


def desenhar_sobreposicao(grade, a, b, k):
    """Os dois percursos sobre a mesma grade: A em azul, B em laranja; o trecho já andado fica forte."""
    altura, largura = len(grade), len(grade[0])
    lado = min(0.55, 14 / largura)
    fig, ax = plt.subplots(figsize=(max(5.0, largura * lado), max(3.0, altura * lado)))
    ax.imshow([[to_rgba(COR_TERRENO.get(casa, COR_CHAO)) for casa in linha] for linha in grade],
              interpolation="nearest", zorder=1)
    for l, linha in enumerate(grade):
        for c, casa in enumerate(linha):
            if casa in SIMBOLOS_VISIVEIS:
                ax.text(c, l, casa, ha="center", va="center", fontsize=max(5, 20 * lado),
                        fontweight="bold" if casa.isupper() else "normal", color=COR_TEXTO, alpha=0.6, zorder=3)

    desloc = {"A": -0.13, "B": 0.13}
    so_a = {p["pos"] for p in a["passos"]} - {p["pos"] for p in b["passos"]} if b["ok"] else set()
    so_b = {p["pos"] for p in b["passos"]} - {p["pos"] for p in a["passos"]} if a["ok"] else set()
    for nome, lado_info in (("A", a), ("B", b)):
        if not lado_info["ok"]:
            continue
        d, cor = desloc[nome], COR_LADO[nome]
        xs = [p["pos"][1] + d for p in lado_info["passos"]]
        ys = [p["pos"][0] + d for p in lado_info["passos"]]
        i = min(k, lado_info["ultimo"])
        ax.plot(xs, ys, color=cor, lw=2, alpha=0.25, zorder=4, solid_capstyle="round")
        ax.plot(xs[:i + 1], ys[:i + 1], color=cor, lw=3, zorder=5, solid_capstyle="round",
                ls="-" if nome == "A" else (0, (4, 1.5)))
        ax.plot(xs[i], ys[i], "o", ms=max(6, 24 * lado), color=cor, mec=COR_TEXTO, mew=1.4, zorder=6)
    for celulas, nome in ((so_a, "A"), (so_b, "B")):
        if celulas:
            ls, cs = zip(*celulas)
            ax.scatter(cs, ls, marker="s", s=(26 * lado) ** 2, facecolor="none", edgecolor=COR_LADO[nome],
                       linewidths=1.2, zorder=2)

    ax.set_title(f"Os dois percursos na mesma grade · passo {k}", fontsize=11, color=COR_TEXTO, loc="left")
    ax.set_xlabel("coluna", color=COR_TEXTO_2)
    ax.set_ylabel("linha", color=COR_TEXTO_2)
    ax.set_xlim(-0.5, largura - 0.5)
    ax.set_ylim(altura - 0.5, -0.5)
    passo_tick = 1 if largura <= 20 else 5
    ax.set_xticks(range(0, largura, passo_tick))
    ax.set_yticks(range(0, altura, passo_tick))
    ax.tick_params(labelsize=8, colors=COR_TEXTO_2, length=0)
    ax.set_aspect("equal")
    for borda in ax.spines.values():
        borda.set_visible(False)
    legenda = [
        Line2D([0], [0], color=COR_LADO["A"], lw=3, label=f"A · {descrever_lado(a)}"),
        Line2D([0], [0], color=COR_LADO["B"], lw=3, ls=(0, (4, 1.5)), label=f"B · {descrever_lado(b)}"),
        Line2D([0], [0], color=COR_TEXTO_2, lw=2, alpha=0.3, label="trecho que ainda falta"),
        Line2D([0], [0], marker="s", ls="", mfc="none", mec=COR_TEXTO_2, ms=8,
               label="casa que só um dos percursos usa (cor do lado)"),
        Patch(facecolor=COR_TERRENO[","], label="lama (custo 3)"),
        Patch(facecolor=COR_TERRENO["~"], label="água (custo 5)"),
    ]
    ax.legend(handles=legenda, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False,
              fontsize=8, labelcolor=COR_TEXTO)
    return fig


def desenhar_custos(a, b, k):
    """Custo acumulado por passo dos dois lados, com o passo atual marcado."""
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    ax.axhline(0, color=COR_TEXTO_2, lw=0.8)
    for nome, lado in (("A", a), ("B", b)):
        if not lado["ok"]:
            continue
        totais = [p["total"] for p in lado["passos"]]
        ax.step(range(len(totais)), totais, where="post", color=COR_LADO[nome], lw=2,
                ls="-" if nome == "A" else (0, (4, 1.5)),
                label=f"{nome} · {NOME_ALG[lado['algoritmo']]}: {lado['ultimo']} passos, custo {totais[-1]}")
        i = min(k, lado["ultimo"])
        ax.plot(i, totais[i], "o", ms=8, color=COR_LADO[nome], mec="white", mew=1.5, zorder=5)
    ax.axvline(k, color=COR_TEXTO_2, lw=1, ls=":", label=f"passo atual ({k})")
    ax.set_title("Custo acumulado a cada passo", fontsize=11, color=COR_TEXTO, loc="left")
    ax.set_xlabel("passo", color=COR_TEXTO_2)
    ax.set_ylabel("custo acumulado", color=COR_TEXTO_2)
    ax.tick_params(labelsize=8, colors=COR_TEXTO_2)
    ax.grid(color="#e4e3df", lw=0.6)
    ax.set_axisbelow(True)
    for borda in ("top", "right"):
        ax.spines[borda].set_visible(False)
    ax.legend(loc="upper left", frameon=False, fontsize=8, labelcolor=COR_TEXTO)
    return fig


def tabela_passo_a_passo(a, b):
    linhas = []
    for k in range(max(a["ultimo"], b["ultimo"]) + 1):
        pa = a["passos"][k] if a["ok"] and k <= a["ultimo"] else None
        pb = b["passos"][k] if b["ok"] and k <= b["ultimo"] else None
        linhas.append({
            "passo": k,
            "estado A": pa["rotulo"] if pa else "—",
            "custo A": pa["total"] if pa else None,
            "estado B": pb["rotulo"] if pb else "—",
            "custo B": pb["total"] if pb else None,
            "mesmo estado": "sim" if pa and pb and pa["rotulo"] == pb["rotulo"] else "não",
        })
    return pd.DataFrame(linhas).astype({"custo A": "Int64", "custo B": "Int64"})


def painel_do_lado(nome, lado, k, outro, ver_armadilhas):
    cor_lado = COR_LADO[nome]
    st.markdown(f"<h3 style='margin-bottom:0'><span style='color:{cor_lado}'>■</span> Lado {nome}</h3>",
                unsafe_allow_html=True)
    st.caption(descrever_lado(lado))
    dados = lado["dados"]
    mostrar_status(f"{NOME_ALG[lado['algoritmo']]} (lado {nome})", lado["info"],
                   sum(len(nos) for nos in dados["camadas"].values()))
    i = min(k, lado["ultimo"])
    atual = lado["passos"][i]

    m1, m2, m3, m4 = st.columns(4)
    if lado["ok"]:
        total_outro = outro["passos"][-1]["total"] if outro["ok"] else None
        m1.metric("Passos até G", lado["ultimo"],
                  delta=lado["ultimo"] - outro["ultimo"] if outro["ok"] and nome == "B" else None,
                  delta_color="inverse", help="No lado B, a diferença em relação ao lado A.")
        m2.metric("Custo final", lado["passos"][-1]["total"],
                  delta=lado["passos"][-1]["total"] - total_outro if total_outro is not None and nome == "B"
                  else None, delta_color="inverse", help="No lado B, a diferença em relação ao lado A.")
    else:
        m1.metric("Passos até G", "—")
        m2.metric("Custo final", "—")
    m3.metric("Custo agora", atual["total"])
    m4.metric("Chaves agora", ", ".join(atual["chaves"]) or "nenhuma")

    camada = atual["chaves"]
    nos_camada = dados["camadas"].get(camada, [])
    celulas_camada = {ler_rotulo(no)[0] for no in nos_camada}
    celulas_armadilha = {ler_rotulo(no)[0] for no in nos_camada if no in dados["armadilhas"]} \
        if ver_armadilhas else set()
    mostrar_figura(desenhar_tabuleiro(dados["grade"], lado["passos"], i, camada, lado["cor"],
                                      celulas_camada, celulas_armadilha), dpi=100)
    if lado["ok"] and k >= lado["ultimo"] and k > 0:
        st.success(f"Lado {nome} chegou em G no passo {lado['ultimo']}.")
    if atual["rotulo"] in dados["armadilhas"]:
        st.error("Este estado é uma armadilha: daqui não dá mais para chegar em G.")


def modo_lado_a_lado(textos, inicial):
    titulos = list(textos)
    padrao = titulos[min(inicial, len(titulos) - 1)]
    st.session_state.setdefault("cmp_exemplo", SEM_EXEMPLO)
    st.session_state.setdefault("cmp_diferentes", False)
    for lado, alg in (("a", "BFS"), ("b", "DIJKSTRA")):
        st.session_state.setdefault(f"cmp_mapa_{lado}", padrao)
        st.session_state.setdefault(f"cmp_alg_{lado}", alg)
        st.session_state.setdefault(f"cmp_fonte_{lado}", False)
        if st.session_state[f"cmp_mapa_{lado}"] not in titulos:  # o mapa enviado foi removido
            st.session_state[f"cmp_mapa_{lado}"] = padrao

    with st.sidebar:
        st.header("Exemplos prontos")
        st.selectbox("Comparações que valem a pena ver", (SEM_EXEMPLO,) + tuple(e[0] for e in EXEMPLOS),
                     key="cmp_exemplo", on_change=aplicar_exemplo, args=(titulos,))
        st.header("Lado A")
        st.selectbox("Mapa", titulos, key="cmp_mapa_a")
        st.radio("Algoritmo do lado A", ALGORITMOS, key="cmp_alg_a", format_func=NOME_ALG.get, horizontal=True)
        st.checkbox("Fonte consumível no lado A", key="cmp_fonte_a")
        st.header("Lado B")
        diferentes = st.checkbox("Usar outro mapa no lado B", key="cmp_diferentes")
        if diferentes:
            st.selectbox("Mapa do lado B", titulos, key="cmp_mapa_b")
        st.radio("Algoritmo do lado B", ALGORITMOS, key="cmp_alg_b", format_func=NOME_ALG.get, horizontal=True)
        st.checkbox("Fonte consumível no lado B", key="cmp_fonte_b")
        st.header("Visualização")
        ver_armadilhas = st.checkbox("Destacar estados-armadilha", value=True)
        velocidade = st.slider("Velocidade (passos por segundo)", 1, 20, 4)

    ta = st.session_state.cmp_mapa_a
    tb = st.session_state.cmp_mapa_b if diferentes else ta
    a = preparar(ta, *textos[ta], st.session_state.cmp_fonte_a, st.session_state.cmp_alg_a)
    b = preparar(tb, *textos[tb], st.session_state.cmp_fonte_b, st.session_state.cmp_alg_b)
    ultimo = max(a["ultimo"], b["ultimo"])
    reiniciar_se_mudou(("lado", ta, textos[ta][1], a["fonte"], a["algoritmo"],
                        tb, textos[tb][1], b["fonte"], b["algoritmo"]), ultimo)
    k = st.session_state.passo

    st.title("Labirinto interativo · comparação lado a lado")
    st.caption(f"**A:** {descrever_lado(a)}  ·  **B:** {descrever_lado(b)}. Os dois andam juntos: o passo é o "
               f"mesmo dos dois lados, e quem chega primeiro espera parado em G.")
    tipo, frase = veredito(a, b)
    getattr(st, tipo)(frase)

    if ultimo:
        controle, resumo = st.columns([2, 3])
        with controle:
            controles_de_passo(ultimo, "▶ Reproduzir os dois")
        with resumo:
            r1, r2, r3 = st.columns(3)
            pa, pb = no_passo(a, k), no_passo(b, k)
            r1.metric("Passo", f"{k} de {ultimo}")
            r2.metric("Custo agora (A × B)", f"{pa['total']} × {pb['total']}",
                      help="Custo acumulado de cada lado até o passo atual.")
            r3.metric("Mesma casa agora?", "sim" if pa["pos"] == pb["pos"] else "não",
                      help="Compara só a posição; as chaves e os bônus podem ser diferentes.")

    col_a, col_b = st.columns(2)
    with col_a:
        painel_do_lado("A", a, k, b, ver_armadilhas)
    with col_b:
        painel_do_lado("B", b, k, a, ver_armadilhas)

    st.subheader("Os dois percursos juntos")
    if a["dados"]["grade"] == b["dados"]["grade"]:
        sobre, curva = st.columns([3, 2])
        with sobre:
            mostrar_figura(desenhar_sobreposicao(a["dados"]["grade"], a, b, k))
        with curva:
            mostrar_figura(desenhar_custos(a, b, k))
            k_div = primeira_divergencia(a, b) if a["ok"] and b["ok"] else None
            if k_div is not None:
                st.caption(f"Até o passo {k_div - 1} os dois percursos passam pelos mesmos estados; "
                           f"a partir do passo {k_div}, cada um segue o seu caminho.")
    else:
        st.caption("Os lados usam mapas diferentes, então não há sobreposição na grade; "
                   "a curva de custo continua comparável.")
        mostrar_figura(desenhar_custos(a, b, k))

    with st.expander("Passo a passo dos dois percursos (tabela)"):
        st.dataframe(tabela_passo_a_passo(a, b), hide_index=True, height=320)
        st.caption("Rótulos no formato do enunciado: (linha,coluna)|chaves|{bônus consumidos}.")

    with st.expander("Grafo de estados dos dois lados"):
        linhas = []
        for nome, lado in (("A", a), ("B", b)):
            m = lado["dados"]["metricas"]
            linhas.append({"lado": nome, "configuração": descrever_lado(lado), "estados": m["ordem"],
                           "arcos": m["tamanho"], "densidade": round(m["densidade"], 4),
                           "camadas": len(lado["dados"]["camadas"]),
                           "estados-armadilha": len(lado["dados"]["armadilhas"]), "status": lado["info"]["status"]})
        st.dataframe(pd.DataFrame(linhas), hide_index=True)
    return velocidade


def main():
    st.set_page_config(page_title="Labirinto interativo", page_icon="🧩", layout="wide")
    args = ler_argumentos()
    opcoes, inicial = mapas_disponiveis(args.mapa)

    with st.sidebar:
        modo = st.radio("Modo", MODOS, horizontal=True)
        enviado = st.file_uploader("Enviar um mapa (.txt), como o mapa surpresa", type="txt")
    textos = ler_mapas(opcoes, enviado)
    if not textos:
        st.error("Nenhum mapa encontrado em data/mapas/ nem em data/mapas_grupo/.")
        st.stop()
    if enviado is not None:
        inicial = 0  # o mapa enviado entra no topo da lista

    if modo == MODOS[0]:
        velocidade = modo_um_algoritmo(textos, inicial)
    else:
        velocidade = modo_lado_a_lado(textos, inicial)

    if st.session_state.tocando:
        time.sleep(1 / velocidade)
        st.rerun()


if __name__ == "__main__":
    main()
