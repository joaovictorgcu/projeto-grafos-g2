# [IA] Claude Code (Claude Opus 5) – esqueleto do script de ficha, a partir dos filtros
# documentados nos slides do checkpoint. Números a conferir pelo grupo.
"""Ficha do dataset da Parte 2: confere o snapshot e recalcula os números da proposta.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

# --------------------------------------------------------------------------- #
# CONFERIR ANTES DE RODAR: nomes das colunas no snapshot que vocês baixaram.
# Se algum estiver diferente, o script para e lista as colunas que encontrou.
# --------------------------------------------------------------------------- #
COL = {
    "jogador":        "player_id",
    "data":           "transfer_date",
    "temporada":      "transfer_season",
    "origem_id":      "from_club_id",
    "destino_id":     "to_club_id",
    "origem_nome":    "from_club_name",
    "destino_nome":   "to_club_name",
    "valor_pago":     "transfer_fee",
    "valor_mercado":  "market_value_in_eur",
}
COL_JOGADORES = {
    "jogador":        "player_id",
    "nascimento":     "date_of_birth",
    "posicao":        "position",
    "pe":             "foot",
    "altura":         "height_in_cm",
    "nacionalidade":  "country_of_citizenship",
    "empresario":     "agent_name",
}
COL_CLUBES = {
    "clube":          "club_id",
    "liga":           "domestic_competition_id",
}

# Recorte, como está nos slides do checkpoint.
DATA_CORTE = "2026-07-06"   # depois disso, só retornos de empréstimo agendados
PSEUDO_CLUBES = ["Without Club", "Unknown", "Retired", "Career break", "Ban", "Own Youth"]

# Preencher com a URL de onde o snapshot foi baixado, para o --baixar funcionar.
URL_SNAPSHOT = ""


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def exigir_colunas(df: pd.DataFrame, mapa: dict, arquivo: str) -> None:
    faltando = [v for v in mapa.values() if v not in df.columns]
    if faltando:
        sys.exit(
            f"\n{arquivo}: não achei a(s) coluna(s) {faltando}.\n"
            f"Colunas que existem no arquivo:\n  {sorted(df.columns)}\n"
            f"Ajuste o dicionário COL no topo de scripts/ficha_transfermarkt.py."
        )


def carregar(pasta: Path) -> tuple[pd.DataFrame, pd.DataFrame | None, pd.DataFrame | None]:
    arq = pasta / "transfers.csv"
    if not arq.exists():
        sys.exit(f"não achei {arq}. Baixe o snapshot para essa pasta antes de rodar.")
    transferencias = pd.read_csv(arq, low_memory=False)
    exigir_colunas(transferencias, COL, "transfers.csv")

    jogadores = clubes = None
    if (pasta / "players.csv").exists():
        jogadores = pd.read_csv(pasta / "players.csv", low_memory=False)
        exigir_colunas(jogadores, COL_JOGADORES, "players.csv")
    if (pasta / "clubs.csv").exists():
        clubes = pd.read_csv(pasta / "clubs.csv", low_memory=False)
        exigir_colunas(clubes, COL_CLUBES, "clubs.csv")
    return transferencias, jogadores, clubes


def aplicar_recorte(t: pd.DataFrame) -> tuple[pd.DataFrame, list[tuple[str, int]]]:
    """Os cinco filtros do recorte, na ordem dos slides. Devolve também o funil."""
    funil = [("transferências no arquivo bruto", len(t))]

    # 1. data de corte
    t = t.copy()
    t[COL["data"]] = pd.to_datetime(t[COL["data"]], errors="coerce")
    t = t[t[COL["data"]] <= pd.Timestamp(DATA_CORTE)]
    funil.append((f"até {DATA_CORTE}", len(t)))

    # 2. valor pago e valor de mercado conhecidos (sem eles não existe peso)
    t = t.dropna(subset=[COL["valor_pago"], COL["valor_mercado"]])
    funil.append(("com valor pago e valor de mercado", len(t)))

    # 3. sem os pseudo-clubes
    for lado in ("origem_nome", "destino_nome"):
        t = t[~t[COL[lado]].isin(PSEUDO_CLUBES)]
    funil.append(("sem pseudo-clubes", len(t)))

    # 4. sem self-loops
    t = t[t[COL["origem_id"]] != t[COL["destino_id"]]]
    funil.append(("sem self-loops", len(t)))

    # 5. empréstimos: fee = 0 em ida e volta consecutiva do mesmo jogador (heurística)
    t = t.sort_values([COL["jogador"], COL["data"]])
    g = t.groupby(COL["jogador"], sort=False)
    volta_para_origem = g[COL["destino_id"]].shift(-1).eq(t[COL["origem_id"]]) & \
                        g[COL["origem_id"]].shift(-1).eq(t[COL["destino_id"]])
    veio_de_volta = g[COL["destino_id"]].shift(1).eq(t[COL["origem_id"]]) & \
                    g[COL["origem_id"]].shift(1).eq(t[COL["destino_id"]])
    sem_valor = t[COL["valor_pago"]].fillna(0).eq(0)
    emprestimo = sem_valor & (volta_para_origem | veio_de_volta)
    t = t[~emprestimo]
    funil.append(("sem empréstimos", len(t)))

    return t, funil


def montar_arcos(t: pd.DataFrame) -> pd.DataFrame:
    """Um arco por par ordenado, com os pesos somados."""
    t = t.assign(peso=t[COL["valor_pago"]] - t[COL["valor_mercado"]])
    arcos = (t.groupby([COL["origem_id"], COL["destino_id"]], as_index=False)
               .agg(peso=("peso", "sum"), transferencias=(COL["jogador"], "size")))
    return arcos.rename(columns={COL["origem_id"]: "origem", COL["destino_id"]: "destino"})


def pares_com_ciclo_negativo(arcos: pd.DataFrame) -> int:
    """Pares (u,v) com os dois sentidos presentes e soma negativa — ciclos de comprimento 2.

    É o único tipo de ciclo que dá para contar sem algoritmo de grafo: basta casar cada arco
    com o seu inverso. Ciclos mais longos são trabalho do Bellman-Ford do grupo.
    """
    volta = arcos.rename(columns={"origem": "destino", "destino": "origem",
                                  "peso": "peso_volta"})[["origem", "destino", "peso_volta"]]
    par = arcos.merge(volta, on=["origem", "destino"])
    par = par[par["origem"] < par["destino"]]           # conta cada par uma vez só
    return int((par["peso"] + par["peso_volta"] < 0).sum())


def faltantes(brutas: pd.DataFrame, jogadores, clubes) -> dict:
    """% de ausência sobre as linhas BRUTAS, como está na proposta."""
    n = len(brutas)
    pct = lambda s: round(100 * s.isna().mean(), 2)
    out = {
        "valor_pago": pct(brutas[COL["valor_pago"]]),
        "valor_mercado": pct(brutas[COL["valor_mercado"]]),
    }
    if jogadores is not None:
        j = brutas.merge(jogadores, left_on=COL["jogador"],
                         right_on=COL_JOGADORES["jogador"], how="left")
        for rotulo, chave in (("idade", "nascimento"), ("posicao", "posicao"),
                              ("pe", "pe"), ("altura", "altura"),
                              ("nacionalidade", "nacionalidade"), ("empresario", "empresario")):
            out[rotulo] = pct(j[COL_JOGADORES[chave]])
    if clubes is not None:
        c = brutas.merge(clubes, left_on=COL["destino_id"],
                         right_on=COL_CLUBES["clube"], how="left")
        out["liga_do_destino"] = pct(c[COL_CLUBES["liga"]])
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Ficha do dataset da Parte 2.")
    ap.add_argument("--dados", default="data/dataset_parte2", type=Path)
    ap.add_argument("--saida", default="out/parte2/ficha_dataset.json", type=Path)
    ap.add_argument("--gravar-hashes", action="store_true",
                    help="grava os SHA-256 atuais como referência do snapshot")
    args = ap.parse_args()

    brutas, jogadores, clubes = carregar(args.dados)

    # --- hashes do snapshot ---
    hashes = {p.name: sha256(p) for p in sorted(args.dados.glob("*.csv"))}
    ref = args.dados / "hashes.json"
    if args.gravar_hashes:
        ref.write_text(json.dumps(hashes, indent=2), encoding="utf-8")
        print(f"hashes gravados em {ref}")
    elif ref.exists():
        esperado = json.loads(ref.read_text(encoding="utf-8"))
        divergentes = [k for k, v in esperado.items() if hashes.get(k) != v]
        if divergentes:
            print(f"ATENÇÃO: o snapshot mudou em {divergentes}. Os números da proposta "
                  f"foram calculados sobre outra versão.\n")
        else:
            print("snapshot confere com hashes.json\n")

    # --- recorte e grafo ---
    usadas, funil = aplicar_recorte(brutas)
    arcos = montar_arcos(usadas)
    nos = pd.unique(arcos[["origem", "destino"]].values.ravel())
    v, e = len(nos), len(arcos)
    densidade = e / (v * (v - 1)) if v > 1 else 0.0
    neg = arcos["peso"] < 0

    ficha = {
        "funil": [{"etapa": nome, "linhas": n} for nome, n in funil],
        "V": v,
        "E": e,
        "transferencias_usadas": len(usadas),
        "densidade": round(densidade, 6),
        "densidade_pct": round(100 * densidade, 2),
        "grau_medio": round(e / v, 2) if v else 0,
        "arcos_peso_negativo": int(neg.sum()),
        "arcos_peso_negativo_pct": round(100 * neg.mean(), 2),
        "peso_min_eur": float(arcos["peso"].min()),
        "peso_mediana_eur": float(arcos["peso"].median()),
        "peso_max_eur": float(arcos["peso"].max()),
        "pares_ciclo_negativo_2": pares_com_ciclo_negativo(arcos),
        "faltantes_pct_sobre_brutas": faltantes(brutas, jogadores, clubes),
        "sha256": hashes,
    }

    # --- saída ---
    print("FUNIL DO RECORTE")
    for nome, n in funil:
        print(f"  {n:>9,}  {nome}")
    print(f"\nGRAFO\n  |V| = {v:,} clubes\n  |E| = {e:,} arcos")
    print(f"  densidade = {ficha['densidade_pct']}%   grau médio = {ficha['grau_medio']}")
    print(f"  arcos com peso negativo: {ficha['arcos_peso_negativo']:,} "
          f"({ficha['arcos_peso_negativo_pct']}%)")
    print(f"  peso mín/mediana/máx (EUR): {ficha['peso_min_eur']:,.0f} / "
          f"{ficha['peso_mediana_eur']:,.0f} / {ficha['peso_max_eur']:,.0f}")
    print(f"  pares com ciclo negativo de comprimento 2: {ficha['pares_ciclo_negativo_2']:,}")
    print("\nFALTANTES (% sobre as brutas)")
    for k, pc in ficha["faltantes_pct_sobre_brutas"].items():
        print(f"  {pc:>6.2f}%  {k}")

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(ficha, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nficha gravada em {args.saida}")


if __name__ == "__main__":
    main()
