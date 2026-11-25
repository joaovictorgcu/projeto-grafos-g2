# [IA] ChatGPT – sugestões de casos de teste

import pandas as pd
from src.graphs.dataset import aplicar_recorte, marcar_emprestimos, montar_arcos, temporada


def test_remover_pseudo_clubes():
    df = pd.DataFrame({
        "player_id": [1, 2, 3],
        "transfer_date": pd.to_datetime(["2024-07-01", "2024-07-02", "2024-07-03"]),
        "transfer_season": ["24/25", "24/25", "24/25"],
        "from_club_id": [10, 515, 20],
        "to_club_id": [20, 10, 123],
        "transfer_fee": [10_000_000, 0, 5_000_000],
        "market_value_in_eur": [8_000_000, 0, 4_000_000],
    })

    usadas, _ = aplicar_recorte(df)

    assert usadas["from_club_id"].tolist() == [10]
    assert usadas["to_club_id"].tolist() == [20]


def test_remover_self_loops():
    df = pd.DataFrame({
        "player_id": [1, 2],
        "transfer_date": pd.to_datetime(["2024-07-01", "2024-07-02"]),
        "transfer_season": ["24/25", "24/25"],
        "from_club_id": [10, 30],
        "to_club_id": [10, 40],
        "transfer_fee": [5_000_000, 8_000_000],
        "market_value_in_eur": [4_000_000, 6_000_000],
    })

    usadas, _ = aplicar_recorte(df)

    assert usadas["from_club_id"].tolist() == [30]
    assert usadas["to_club_id"].tolist() == [40]


def test_marcar_emprestimos():
    df = pd.DataFrame({
        "player_id": [1, 1, 2],
        "transfer_date": pd.to_datetime(["2023-07-01", "2024-06-30", "2024-07-01"]),
        "transfer_season": ["23/24", "23/24", "24/25"],
        "from_club_id": [10, 20, 10],
        "to_club_id": [20, 10, 30],
        "transfer_fee": [0, 0, 0],
        "market_value_in_eur": [5_000_000, 5_000_000, 3_000_000],
    })

    marcacao = marcar_emprestimos(df)

    assert marcacao.tolist() == [True, True, False]


def test_montar_arcos():
    usadas = pd.DataFrame({
        "from_club_id": [10, 10, 20],
        "to_club_id": [20, 20, 30],
        "peso": [2_000_000, 3_000_000, 1_000_000],
    })

    arcos = montar_arcos(usadas)
    arco_10_20 = arcos[(arcos["origem"] == 10) & (arcos["destino"] == 20)].iloc[0]

    assert arco_10_20["peso"] == 5_000_000
    assert arco_10_20["transferencias"] == 2


def test_temporada():
    assert temporada("15/16") == 2015
    assert temporada("99/00") == 1999