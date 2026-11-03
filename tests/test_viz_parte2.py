"""Formatação e resumos usados nos gráficos da Parte 2 (não precisa do snapshot)."""
import pytest

from src.viz_parte2 import br, eur, milhoes, pct, pct_eixo, resumo_camadas, tempo_ms

MENOS = "−"


def test_br_usa_ponto_de_milhar_virgula_decimal_e_menos_tipografico():
    assert br(4739) == "4.739"
    assert br(22009.862) == "22.010"
    assert br(-1234.5, 1) == f"{MENOS}1.234,5"
    assert br(-0.963, 2) == f"{MENOS}0,96"


def test_pct():
    assert pct(0.7809) == "78%"
    assert pct(0.36636, 1) == "36,6%"
    assert pct_eixo(1) == "100%"
    assert pct_eixo(0.001) == "0,1%"


def test_milhoes_mostra_uma_casa_decimal_so_quando_ela_existe():
    # −3,5 mi e −4 mi são transferências diferentes e não podem aparecer iguais
    assert milhoes(-3_500_000) == f"{MENOS}3,5 mi"
    assert milhoes(-4_000_000) == f"{MENOS}4 mi"
    assert milhoes(-33_800_000) == f"{MENOS}33,8 mi"
    assert milhoes(-34_000_000) == f"{MENOS}34 mi"
    assert milhoes(180_000_000) == "180 mi"
    assert milhoes(-335_460_000) == f"{MENOS}335,5 mi"


def test_eur_para_eixos():
    assert eur(0) == "0"
    assert eur(1_000) == "1 mil"
    assert eur(-100_000) == f"{MENOS}100 mil"
    assert eur(1_000_000) == "1 mi"
    assert eur(-100_000_000) == f"{MENOS}100 mi"


def test_tempo_ms():
    assert tempo_ms(2.416) == "2,4 ms"
    assert tempo_ms(22009.862) == "22.010 ms (≈ 22 s)"


def test_resumo_camadas_com_as_camadas_do_benfica():
    camadas = [1, 87, 742, 1183, 743, 281, 106, 34, 17, 6, 2, 1]
    meio, ate5 = resumo_camadas(camadas)
    assert sum(camadas) == 3203
    assert meio == pytest.approx((742 + 1183 + 743) / 3203)
    assert ate5 == pytest.approx((1 + 87 + 742 + 1183 + 743 + 281) / 3203)
    assert 0.77 < meio < 0.84 and ate5 > 0.9
