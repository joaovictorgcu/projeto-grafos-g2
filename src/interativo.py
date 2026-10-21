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


def main():
    st.set_page_config(page_title="Labirinto interativo", page_icon="🧩", layout="wide")
    args = ler_argumentos()
    opcoes, inicial = mapas_disponiveis(args.mapa)
    titulos = list(opcoes)

    with st.sidebar:
        st.header("Mapa")
        escolha = st.selectbox("Mapa do projeto", titulos, index=inicial)
        enviado = st.file_uploader("ou envie um mapa (.txt), como o mapa surpresa", type="txt")
        fonte_consumivel = st.checkbox("Fonte consumível (* vale −2 só na 1ª passagem)")
        st.header("Algoritmo")
        algoritmo = st.radio("Algoritmo", ALGORITMOS, label_visibility="collapsed")

    if enviado is not None:
        nome, titulo = Path(enviado.name).stem, f"{Path(enviado.name).stem} · enviado"
        try:
            texto = enviado.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            st.error(f"{enviado.name}: o arquivo não está em UTF-8.")
            st.stop()
    else:
        arquivo = opcoes[escolha]
        if not arquivo.is_file():
            st.error(f"Arquivo não encontrado: {arquivo}")
            st.stop()
        nome, titulo, texto = arquivo.stem, escolha, arquivo.read_text(encoding="utf-8")

    try:
        dados = processar(texto, nome, fonte_consumivel)
    except MapaInvalido as erro:
        st.error(f"**Mapa inválido.** {erro}")
        st.stop()

    info = dados["caminhos"][algoritmo]
    passos = info["passos"]
    ultimo = len(passos) - 1

    chave = (titulo, texto, fonte_consumivel, algoritmo)
    if st.session_state.get("chave") != chave:
        st.session_state.chave = chave
        st.session_state.passo = 0
        st.session_state.tocando = False
    if st.session_state.tocando:
        st.session_state.passo = min(st.session_state.passo + 1, ultimo)
        st.session_state.tocando = st.session_state.passo < ultimo

    camadas = dados["camadas"]
    indice = {k: n for n, k in enumerate(camadas)}

    def cor(chaves):
        return CORES_CAMADA[indice[chaves] % len(CORES_CAMADA)]

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
    mostrar_status(algoritmo, info, sum(len(nos) for nos in camadas.values()))

    tabuleiro, painel = st.columns([3, 1])
    with painel:
        if ultimo:
            st.slider("Passo", 0, ultimo, key="passo")
            b1, b2, b3, b4 = st.columns(4)
            b1.button("⏮", help="início", on_click=ir_para, args=(0,), width="stretch")
            b2.button("◀", help="voltar um passo", on_click=ir_para,
                      args=(max(0, st.session_state.passo - 1),), width="stretch")
            b3.button("▶", help="avançar um passo", on_click=ir_para,
                      args=(min(ultimo, st.session_state.passo + 1),), width="stretch")
            b4.button("⏭", help="fim", on_click=ir_para, args=(ultimo,), width="stretch")
            st.button("⏸ Pausar" if st.session_state.tocando else "▶ Reproduzir", type="primary",
                      on_click=reproduzir_ou_pausar, args=(ultimo,), width="stretch")
        l, c = atual["pos"]
        st.metric("Posição (linha, coluna)", f"({l}, {c})")
        st.metric("Chaves", ", ".join(atual["chaves"]) or "nenhuma")
        st.metric("Bônus consumidos", ", ".join(map(str, sorted(atual["bonus"]))) or "nenhum")
        st.metric("Custo acumulado", atual["total"], delta=atual["custo"] if st.session_state.passo else None,
                  delta_color="inverse")
        if atual["rotulo"] in dados["armadilhas"]:
            st.error("Este estado é uma armadilha: daqui não dá mais para chegar em G.")

    with tabuleiro:
        fig = desenhar_tabuleiro(dados["grade"], passos, st.session_state.passo, camada, cor,
                                 celulas_camada, celulas_armadilha)
        imagem = io.BytesIO()
        fig.savefig(imagem, format="png", dpi=110, bbox_inches="tight")
        plt.close(fig)
        st.image(imagem)

    st.subheader("Comparação dos algoritmos")
    st.dataframe(tabela_de_comparacao(dados), hide_index=True)
    m = dados["metricas"]
    e1, e2, e3, e4, e5 = st.columns(5)
    e1.metric("Estados (sem o ALVO)", m["ordem"])
    e2.metric("Arcos (sem os do ALVO)", m["tamanho"])
    e3.metric("Densidade", f"{m['densidade']:.4f}")
    e4.metric("Camadas", len(camadas))
    e5.metric("Estados-armadilha", len(dados["armadilhas"]))

    if st.session_state.tocando:
        time.sleep(1 / velocidade)
        st.rerun()


if __name__ == "__main__":
    main()
