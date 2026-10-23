"""Ficha do dataset da Parte 2: baixa o snapshot, confere o SHA-256 e recalcula os números da proposta.

    python scripts/ficha_transfermarkt.py --baixar
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.graphs.dataset import ARQUIVOS, baixar, carregar_dataset, sha256  # noqa: E402
from src.parte2 import pares_ciclo_2  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Ficha do dataset da Parte 2.")
    ap.add_argument("--dados", default="data/dataset_parte2", type=Path)
    ap.add_argument("--saida", default="out/parte2/ficha_dataset.json", type=Path)
    ap.add_argument("--baixar", action="store_true", help="baixa o que faltar do snapshot")
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if args.baixar:
        for nome, ok in baixar(args.dados).items():
            print(f"{nome:20s} {'SHA-256 ok' if ok else 'SHA-256 DIFERENTE do snapshot da proposta'}")
        print()

    d = carregar_dataset(args.dados)
    a = d.arcos
    v = len(set(a["origem"]) | set(a["destino"]))
    e = len(a)
    ficha = {
        "funil": [{"etapa": n, "linhas": k} for n, k in d.funil],
        "V": v,
        "E": e,
        "transferencias_usadas": len(d.usadas),
        "densidade": round(e / (v * (v - 1)), 6),
        "grau_medio": round(e / v, 2),
        "arcos_peso_negativo_pct": round(100 * float((a["peso"] < 0).mean()), 2),
        "peso_min_eur": int(a["peso"].min()),
        "peso_mediana_eur": float(a["peso"].median()),
        "peso_max_eur": int(a["peso"].max()),
        "pares_ciclo_negativo_2": pares_ciclo_2(d)["total"],
        "sha256": {nome: sha256(args.dados / nome) for nome in ARQUIVOS if (args.dados / nome).exists()},
    }

    print("FUNIL DO RECORTE")
    for nome, n in d.funil:
        print(f"  {n:>9,}  {nome}")
    print(f"\nGRAFO\n  |V| = {v:,} clubes\n  |E| = {e:,} arcos")
    print(f"  arcos com peso negativo: {ficha['arcos_peso_negativo_pct']}%")
    print(f"  peso mín/mediana/máx (EUR): {ficha['peso_min_eur']:,} / {ficha['peso_mediana_eur']:,.0f} / "
          f"{ficha['peso_max_eur']:,}")
    print(f"  pares com ciclo negativo de comprimento 2: {ficha['pares_ciclo_negativo_2']:,}")

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(ficha, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nficha gravada em {args.saida}")


if __name__ == "__main__":
    main()
