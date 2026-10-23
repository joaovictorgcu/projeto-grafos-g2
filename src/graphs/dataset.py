"""Leitura do snapshot do Transfermarkt e montagem dos grafos da Parte 2."""
import hashlib
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .graph import Grafo

URL_SNAPSHOT = "https://pub-e682421888d945d684bcae8890b0ec20.r2.dev/data/"
ARQUIVOS = {  # snapshot com dados até 06/07/2026, publicado em 05/09/2026
    "transfers.csv.gz": "90326983daf7e6ac7aabdfe62b90936d9bf1dd2171e53dec75c3751eb1620a83",
    "players.csv.gz": "d22e407981d5b51a79bf8ff59835729f3526f7dc3495a6d8ed2f852ed2e86403",
    "clubs.csv.gz": "aa57ab56e87faffaea1e8697439a32caf10116d8f2f2dfb3a57193c0bb1d641b",
}

COLUNAS_TRANSFERENCIAS = [
    "player_id", "transfer_date", "transfer_season", "from_club_id", "to_club_id",
    "from_club_name", "to_club_name", "transfer_fee", "market_value_in_eur",
]
COLUNAS_JOGADORES = [
    "player_id", "date_of_birth", "position", "sub_position", "foot", "height_in_cm",
    "country_of_citizenship", "agent_name",
]
COLUNAS_CLUBES = ["club_id", "domestic_competition_id"]

# ids que não são clubes
PSEUDO_CLUBES = {515: "Without Club", 75: "Unknown", 123: "Retired",
                 2113: "Career break", 2077: "Ban", 12604: "Own Youth"}
DATA_CORTE = pd.Timestamp("2026-07-06")


class DatasetInvalido(ValueError):
    pass


def sha256(caminho) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def baixar(pasta) -> dict:
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    conferido = {}
    for nome, esperado in ARQUIVOS.items():
        caminho = pasta / nome
        if not caminho.exists():
            # sem User-Agent o R2 responde 403
            req = urllib.request.Request(URL_SNAPSHOT + nome, headers={"User-Agent": "projeto-grafos-g2"})
            with urllib.request.urlopen(req) as resp:
                caminho.write_bytes(resp.read())
        conferido[nome] = sha256(caminho) == esperado
    return conferido


def _arquivo(pasta: Path, nome: str) -> Path:
    for candidato in (pasta / f"{nome}.csv.gz", pasta / f"{nome}.csv"):
        if candidato.exists():
            return candidato
    raise DatasetInvalido(
        f"não achei {nome}.csv.gz nem {nome}.csv em {pasta}. "
        f"Baixe o snapshot com: python scripts/ficha_transfermarkt.py --baixar"
    )


def _ler(pasta, nome: str, colunas: list) -> pd.DataFrame:
    caminho = _arquivo(Path(pasta), nome)
    df = pd.read_csv(caminho, low_memory=False)
    faltando = [c for c in colunas if c not in df.columns]
    if faltando:
        raise DatasetInvalido(f"{caminho.name}: faltam as colunas {faltando}.")
    return df


def ler_transferencias(pasta) -> pd.DataFrame:
    t = _ler(pasta, "transfers", COLUNAS_TRANSFERENCIAS)
    t["transfer_date"] = pd.to_datetime(t["transfer_date"], errors="coerce")
    return t


def ler_jogadores(pasta) -> pd.DataFrame:
    j = _ler(pasta, "players", COLUNAS_JOGADORES)[COLUNAS_JOGADORES].copy()
    j["position"] = j["position"].replace("Missing", pd.NA)
    j["date_of_birth"] = pd.to_datetime(j["date_of_birth"], errors="coerce")
    return j


def ler_clubes(pasta) -> pd.DataFrame:
    return _ler(pasta, "clubs", COLUNAS_CLUBES)[COLUNAS_CLUBES].copy()


def temporada(texto) -> int:
    yy = int(str(texto)[:2])
    return 1900 + yy if yy > 50 else 2000 + yy


def marcar_emprestimos(t: pd.DataFrame) -> pd.Series:
    o = t.sort_values(["player_id", "transfer_date"], kind="stable")
    g = o.groupby("player_id")
    ida = (g["from_club_id"].shift(-1) == o["to_club_id"]) & (g["to_club_id"].shift(-1) == o["from_club_id"])
    volta = (g["from_club_id"].shift(1) == o["to_club_id"]) & (g["to_club_id"].shift(1) == o["from_club_id"])
    return ((ida | volta) & (o["transfer_fee"] == 0)).reindex(t.index)


def aplicar_recorte(t: pd.DataFrame):
    emprestimo = marcar_emprestimos(t)
    funil = [("transferências no arquivo bruto", len(t))]
    m = t["transfer_date"] <= DATA_CORTE
    funil.append((f"até {DATA_CORTE.date()}", int(m.sum())))
    m &= t["transfer_fee"].notna() & t["market_value_in_eur"].notna()
    funil.append(("com valor pago e valor de mercado", int(m.sum())))
    m &= ~t["from_club_id"].isin(PSEUDO_CLUBES) & ~t["to_club_id"].isin(PSEUDO_CLUBES)
    funil.append(("sem pseudo-clubes", int(m.sum())))
    m &= t["from_club_id"] != t["to_club_id"]
    funil.append(("sem self-loops", int(m.sum())))
    m &= ~emprestimo
    funil.append(("sem empréstimos", int(m.sum())))

    usadas = t[m].copy()
    usadas["peso"] = (usadas["transfer_fee"] - usadas["market_value_in_eur"]).round().astype("int64")
    usadas["temporada"] = usadas["transfer_season"].map(temporada)
    return usadas, funil


def montar_arcos(usadas: pd.DataFrame) -> pd.DataFrame:
    arcos = (usadas.groupby(["from_club_id", "to_club_id"], as_index=False)
                   .agg(peso=("peso", "sum"), transferencias=("peso", "size")))
    return arcos.rename(columns={"from_club_id": "origem", "to_club_id": "destino"})


def nomes_dos_clubes(t: pd.DataFrame) -> dict:
    nomes = pd.concat([
        t[["from_club_id", "from_club_name"]].set_axis(["id", "nome"], axis=1),
        t[["to_club_id", "to_club_name"]].set_axis(["id", "nome"], axis=1),
    ]).dropna()
    return nomes.groupby("id")["nome"].agg(lambda s: s.mode().iat[0]).to_dict()


def grafo_de_clubes(arcos: pd.DataFrame, deslocamento: int = 0) -> Grafo:
    g = Grafo()
    for u, v, p in zip(arcos["origem"].tolist(), arcos["destino"].tolist(), arcos["peso"].tolist()):
        g.adicionar_arco(u, v, p + deslocamento)
    return g


def arcos_temporais(usadas: pd.DataFrame) -> pd.DataFrame:
    transf = (usadas.groupby(["from_club_id", "temporada", "to_club_id"], as_index=False)["peso"].sum())
    transf = pd.DataFrame({
        "origem": list(zip(transf["from_club_id"], transf["temporada"])),
        "destino": list(zip(transf["to_club_id"], transf["temporada"] + 1)),
        "peso": transf["peso"],
        "tipo": "transferencia",
    })
    nos = sorted(set(transf["origem"]) | set(transf["destino"]))
    espera = [((c, s), (c2, s2)) for (c, s), (c2, s2) in zip(nos, nos[1:]) if c == c2]
    espera = pd.DataFrame({
        "origem": [a for a, _ in espera],
        "destino": [b for _, b in espera],
        "peso": 0,
        "tipo": "espera",
    })
    return pd.concat([transf, espera], ignore_index=True)


def grafo_temporal(usadas: pd.DataFrame) -> Grafo:
    a = arcos_temporais(usadas)
    g = Grafo()
    for u, v, p in zip(a["origem"].tolist(), a["destino"].tolist(), a["peso"].tolist()):
        g.adicionar_arco(u, v, int(p))
    return g


@dataclass
class Dataset:
    brutas: pd.DataFrame
    usadas: pd.DataFrame
    arcos: pd.DataFrame
    funil: list
    nomes: dict

    def nome(self, clube) -> str:
        if isinstance(clube, tuple):  # nó do grafo temporal
            c, s = clube
            return f"{self.nomes.get(c, c)} ({s % 100:02d}/{(s + 1) % 100:02d})"
        return self.nomes.get(clube, str(clube))

    def grafo(self, deslocamento: int = 0) -> Grafo:
        return grafo_de_clubes(self.arcos, deslocamento)


def carregar_dataset(pasta) -> Dataset:
    brutas = ler_transferencias(pasta)
    usadas, funil = aplicar_recorte(brutas)
    return Dataset(brutas, usadas, montar_arcos(usadas), funil, nomes_dos_clubes(brutas))
