// [IA] Claude Code (Claude Opus 5.5) – tabela dos algoritmos no mesmo mapa
import type { CSSProperties } from "react";
import { ALGORITMOS, NOME_DO_ALGORITMO, NOME_DO_STATUS } from "../modelo";
import type { Algoritmo, DadosDoMapa } from "../tipos";

export function Metricas({ dados, algoritmo, aoEscolher }: {
  dados: DadosDoMapa; algoritmo: Algoritmo; aoEscolher: (a: Algoritmo) => void;
}) {
  const maiorPassos = Math.max(1, ...ALGORITMOS.map((a) => dados.algoritmos[a].passos ?? 0));
  const maiorCusto = Math.max(1, ...ALGORITMOS.map((a) => dados.algoritmos[a].custo ?? 0));

  return (
    <section className="metricas so-tabela" aria-label="Os algoritmos neste mapa">
      <div className="tabela-bloco">
        <span className="rotulo-pequeno">os três algoritmos neste mapa</span>
        <table className="tabela-algoritmos">
          <thead>
            <tr><th scope="col">algoritmo</th><th scope="col">resultado</th><th scope="col">passos</th><th scope="col">custo</th></tr>
          </thead>
          <tbody>
            {ALGORITMOS.map((a) => {
              const r = dados.algoritmos[a];
              return (
                <tr key={a} className={a === algoritmo ? "linha-ativa" : ""} onClick={() => aoEscolher(a)}>
                  <th scope="row">{NOME_DO_ALGORITMO[a]}</th>
                  <td><span className={`etiqueta status-${r.status.toLowerCase()}`}>{NOME_DO_STATUS[r.status]}</span></td>
                  <td className="numero com-barra" style={{ "--p": `${((r.passos ?? 0) / maiorPassos) * 100}%` } as CSSProperties}>{r.passos ?? "-"}</td>
                  <td className="numero com-barra" style={{ "--p": `${(Math.max(0, r.custo ?? 0) / maiorCusto) * 100}%` } as CSSProperties}>{r.custo ?? "-"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
