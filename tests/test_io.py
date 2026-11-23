# [IA] Claude Code (Claude Opus 5.5) – casos de teste da leitura e da validação dos mapas
from pathlib import Path

import pytest

from src.graphs.io import MapaInvalido, interpretar_mapa, ler_mapa

MAPAS = Path(__file__).resolve().parent.parent / "data" / "mapas"


def test_nao_retangular():
    with pytest.raises(MapaInvalido, match="não é retangular: a linha 2 tem 4 casas"):
        interpretar_mapa("#####\n#S.G#\n####\n")


def test_dois_inicios():
    with pytest.raises(MapaInvalido, match=r"2 inícios S, em \(1,1\), \(1,2\)"):
        interpretar_mapa("#####\n#SSG#\n#####\n")


def test_nenhuma_saida():
    with pytest.raises(MapaInvalido, match="não tem saída G"):
        interpretar_mapa("#####\n#S..#\n#####\n")


def test_simbolo_desconhecido():
    with pytest.raises(MapaInvalido, match=r"símbolo desconhecido 'x' na posição \(1,2\)"):
        interpretar_mapa("#####\n#SxG#\n#####\n")


def test_nenhum_inicio():
    with pytest.raises(MapaInvalido, match="não tem início S"):
        interpretar_mapa("#####\n#..G#\n#####\n")


def test_mapa_vazio():
    with pytest.raises(MapaInvalido, match="vazio"):
        interpretar_mapa("; só comentário\n\n")


def test_linha_vazia_no_meio():
    with pytest.raises(MapaInvalido, match="linha 1 está vazia"):
        interpretar_mapa("#####\n\n#S.G#\n#####\n")


def test_espaco_no_fim_da_linha():
    with pytest.raises(MapaInvalido, match="não é retangular"):
        interpretar_mapa("#####\n#S.G# \n#####\n")


def test_erro_cita_o_nome_do_mapa():
    with pytest.raises(MapaInvalido, match="^surpresa: "):
        interpretar_mapa("#####\n#S..#\n#####\n", nome="surpresa")


def test_mapa_invalido_e_value_error():
    assert issubclass(MapaInvalido, ValueError)


def test_comentarios_ignorados():
    m = interpretar_mapa("; topo\n#####\n; meio\n#S.G#\n#####\n")
    assert (m.altura, m.largura) == (3, 5)


def test_bom_do_windows():
    m = interpretar_mapa("﻿#####\n#S.G#\n#####\n")
    assert m.casa(0, 0) == "#" and m.largura == 5


def test_varias_saidas_sao_validas():
    m = interpretar_mapa("######\n#G.SG#\n######\n")
    assert m.saidas == [(1, 1), (1, 4)]


def test_todas_as_esteiras_sao_validas():
    m = interpretar_mapa("########\n#S><^vG#\n########\n")
    assert m.esteiras == {(1, 2): ">", (1, 3): "<", (1, 4): "^", (1, 5): "v"}


@pytest.mark.parametrize("arquivo", sorted(MAPAS.glob("*.txt")), ids=lambda p: p.stem)
def test_mapas_fornecidos_sao_validos(arquivo):
    m = ler_mapa(arquivo)
    assert len(m.inicios) == 1 and m.saidas


def test_bonus_em_ordem_de_leitura():
    m = ler_mapa(MAPAS / "m05_bonus.txt")
    assert m.bonus == {(3, 2): 0, (3, 10): 1, (5, 4): 2}


def test_duas_portas_com_a_mesma_letra():
    m = ler_mapa(MAPAS / "m07_impossivel.txt")
    assert m.portas == {"A": [(1, 6), (3, 7)]}
