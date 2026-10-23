"""Exploração do dataset da Parte 2 (estrutura, faltantes, distribuições, relações e outliers)."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .graphs.dataset import (DATA_CORTE, Dataset, carregar_dataset, ler_clubes, ler_jogadores,
                             temporada)

FAIXAS_IDADE = [0, 21, 24, 27, 30, 33, 50]
SEM_LIGA = "fora das ligas cobertas"


def enriquecer(d: Dataset, pasta) -> pd.DataFrame:
    jogadores = ler_jogadores(pasta)
    clubes = ler_clubes(pasta).rename(columns={"club_id": "to_club_id", "domestic_competition_id": "liga"})
    t = (d.usadas.merge(jogadores, on="player_id", how="left")
                 .merge(clubes, on="to_club_id", how="left"))
    t["idade"] = (t["transfer_date"] - t["date_of_birth"]).dt.days / 365.25
    t["faixa_idade"] = pd.cut(t["idade"], FAIXAS_IDADE, labels=["até 21", "22-24", "25-27", "28-30", "31-33", "34+"])
    t["gratuita"] = t["transfer_fee"] == 0
    t["negativo"] = t["peso"] < 0
    t["tem_empresario"] = t["agent_name"].notna().map({True: "com empresário", False: "sem empresário"})
    t["liga"] = t["liga"].fillna(SEM_LIGA)
    t["razao"] = t["transfer_fee"] / t["market_value_in_eur"]
    return t


def spearman(a: pd.Series, b: pd.Series) -> float:
    m = a.notna() & b.notna()
    return float(a[m].rank().corr(b[m].rank()))


def iqr(serie: pd.Series) -> dict:
    q1, q3 = serie.quantile([0.25, 0.75])
    amplitude = q3 - q1
    baixo, alto = q1 - 1.5 * amplitude, q3 + 1.5 * amplitude
    fora = (serie < baixo) | (serie > alto)
    return {"q1": float(q1), "q3": float(q3), "limite_inferior": float(baixo), "limite_superior": float(alto),
            "outliers": int(fora.sum()), "outliers_pct": round(100 * float(fora.mean()), 2)}


def estrutural(d: Dataset) -> dict:
    b = d.brutas
    return {
        "linhas_brutas": len(b),
        "colunas": {c: str(t) for c, t in b.dtypes.items()},
        "inconsistencias": {
            "valor_pago_negativo": int((b["transfer_fee"] < 0).sum()),
            "valor_mercado_zero_ou_negativo": int((b["market_value_in_eur"] <= 0).sum()),
            "linhas_duplicadas": int(b.duplicated().sum()),
            "data_invalida": int(b["transfer_date"].isna().sum()),
            "datas_depois_do_corte": int((b["transfer_date"] > DATA_CORTE).sum()),
            "data_maxima": str(b["transfer_date"].max().date()),
            "self_loops": int((b["from_club_id"] == b["to_club_id"]).sum()),
        },
        "funil": [{"etapa": n, "linhas": k} for n, k in d.funil],
    }


def faltantes(d: Dataset, t: pd.DataFrame) -> dict:
    b = d.brutas.copy()
    b["temporada"] = b["transfer_season"].map(temporada)
    por_temporada = (b.groupby("temporada")[["transfer_fee", "market_value_in_eur"]]
                      .apply(lambda x: x.isna().mean() * 100).round(2))
    fee_falta = b["transfer_fee"].isna()
    return {
        "brutas_pct": {
            "transfer_fee": round(100 * float(fee_falta.mean()), 2),
            "market_value_in_eur": round(100 * float(b["market_value_in_eur"].isna().mean()), 2),
            "os_dois": round(100 * float((fee_falta & b["market_value_in_eur"].isna()).mean()), 2),
        },
        "por_temporada_pct": por_temporada.reset_index().to_dict(orient="records"),
        "valor_de_mercado_mediano": {
            "quando_fee_falta": float(b.loc[fee_falta, "market_value_in_eur"].median()),
            "quando_fee_existe": float(b.loc[~fee_falta, "market_value_in_eur"].median()),
        },
        "usadas_pct": {c: round(100 * float(t[c].isna().mean()), 2)
                       for c in ["idade", "position", "foot", "height_in_cm", "agent_name",
                                 "country_of_citizenship"]}
                      | {"liga": round(100 * float((t["liga"] == SEM_LIGA).mean()), 2)},
    }


def distribucional(d: Dataset, t: pd.DataFrame) -> dict:
    a = d.arcos
    saida = a.groupby("origem").size()
    entrada = a.groupby("destino").size()
    nos = sorted(set(a["origem"]) | set(a["destino"]))
    saida, entrada = saida.reindex(nos, fill_value=0), entrada.reindex(nos, fill_value=0)

    def resumo(s):
        q = s.quantile([0.5, 0.9, 0.99])
        return {"min": float(s.min()), "mediana": float(q[0.5]), "p90": float(q[0.9]), "p99": float(q[0.99]),
                "max": float(s.max()), "media": float(s.mean())}

    return {
        "peso_transferencia": resumo(t["peso"]),
        "peso_arco": resumo(a["peso"]),
        "valor_pago": resumo(t["transfer_fee"]),
        "valor_mercado": resumo(t["market_value_in_eur"]),
        "grau_saida": resumo(saida),
        "grau_entrada": resumo(entrada),
        "transferencias_gratuitas_pct": round(100 * float(t["gratuita"].mean()), 2),
        "transferencias_negativas_pct": round(100 * float(t["negativo"].mean()), 2),
        "pagas_abaixo_do_mercado_pct": round(100 * float(t.loc[~t["gratuita"], "negativo"].mean()), 2),
        "massa_negativa_das_gratuitas_pct": round(
            100 * float(t.loc[t["negativo"] & t["gratuita"], "peso"].sum() / t.loc[t["negativo"], "peso"].sum()), 2),
        "maiores_graus_saida": [{"clube": d.nome(c), "grau": int(g)} for c, g in
                                saida.sort_values(ascending=False, kind="stable").head(10).items()],
        "maiores_graus_entrada": [{"clube": d.nome(c), "grau": int(g)} for c, g in
                                  entrada.sort_values(ascending=False, kind="stable").head(10).items()],
    }


def por_grupo(t: pd.DataFrame, coluna: str, minimo: int = 0) -> list:
    g = (t.groupby(coluna, observed=True)
          .agg(transferencias=("peso", "size"), negativas_pct=("negativo", "mean"),
               gratuitas_pct=("gratuita", "mean"), peso_mediano=("peso", "median"),
               valor_mercado_mediano=("market_value_in_eur", "median"))
          .reset_index())
    g = g[g["transferencias"] >= minimo]
    g[["negativas_pct", "gratuitas_pct"]] = (g[["negativas_pct", "gratuitas_pct"]] * 100).round(2)
    return g.to_dict(orient="records")


def relacional(t: pd.DataFrame) -> dict:
    pagas = t[~t["gratuita"]]
    numericos = ["idade", "height_in_cm", "market_value_in_eur", "temporada"]
    return {
        "spearman_peso": {c: round(spearman(t["peso"], t[c]), 3) for c in numericos},
        "spearman_razao_pagas": {c: round(spearman(pagas["razao"], pagas[c]), 3) for c in numericos},
        "spearman_gratuita": {c: round(spearman(t["gratuita"].astype(int), t[c]), 3) for c in numericos},
        "por_faixa_idade": por_grupo(t, "faixa_idade"),
        "por_posicao": por_grupo(t, "position"),
        "por_pe": por_grupo(t, "foot"),
        "por_empresario": por_grupo(t, "tem_empresario"),
        "por_liga_destino": por_grupo(t, "liga", minimo=300),
    }


def outliers(t: pd.DataFrame) -> dict:
    pagas = t[~t["gratuita"]]
    log_razao = np.log10(pagas["razao"])
    extremos = t.reindex(t["peso"].abs().sort_values(ascending=False).index).head(10)
    return {
        "peso_iqr": iqr(t["peso"]),
        "log10_razao_pagas_iqr": iqr(log_razao),
        "maiores_em_modulo": [
            {"jogador": r.player_name, "de": r.from_club_name, "para": r.to_club_name,
             "temporada": r.transfer_season, "valor_pago": float(r.transfer_fee),
             "valor_mercado": float(r.market_value_in_eur), "peso": int(r.peso)}
            for r in extremos.itertuples()
        ],
    }


def resumo_eda(d: Dataset, pasta) -> tuple:
    t = enriquecer(d, pasta)
    resumo = {
        "estrutural": estrutural(d),
        "faltantes": faltantes(d, t),
        "distribucional": distribucional(d, t),
        "relacional": relacional(t),
        "outliers": outliers(t),
    }
    return resumo, t


def main(argv=None):
    p = argparse.ArgumentParser(description="Análise exploratória do dataset da Parte 2.")
    p.add_argument("--dataset", default="data/dataset_parte2")
    p.add_argument("--out", default="out/parte2")
    args = p.parse_args(argv)
    d = carregar_dataset(args.dataset)
    resumo, _ = resumo_eda(d, args.dataset)
    saida = Path(args.out)
    saida.mkdir(parents=True, exist_ok=True)
    caminho = saida / "eda_resumo.json"
    caminho.write_text(json.dumps(resumo, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(caminho)


if __name__ == "__main__":
    main()
