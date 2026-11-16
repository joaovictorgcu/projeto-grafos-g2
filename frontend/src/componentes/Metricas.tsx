// painel de métricas do grafo de estados e tabela dos três algoritmos no mesmo mapa
import type { CSSProperties } from "react";
import { ALGORITMOS, NOME_DO_ALGORITMO, NOME_DO_STATUS, camadasDoMapa } from "../modelo";
import type { Algoritmo, DadosDoMapa } from "../tipos";
import { NumeroAnimado } from "./NumeroAnimado";

export function Metricas({ dados, algoritmo, aoEscolher }: {
  dados: DadosDoMapa; algoritmo: Algoritmo; aoEscolher: (a: Algoritmo) => void;
}) {
  const armadilhas = dados.estados.filter((e) => e.armadilha).length;
  const camadas = camadasDoMapa(dados).length;
  const livres = dados.grade.reduce((t, linha) => t + [...linha].filter((c) => c !== "#").length, 0);
  const itens = [
    { nome: "estados", valor: dados.metricas.ordem, ajuda: "nós do grafo, sem o ALVO" },
    { nome: "arcos", valor: dados.metricas.tamanho, ajuda: "movimentos possíveis, sem os arcos até o ALVO" },
    { nome: "densidade", valor: dados.metricas.densidade, casas: 4, ajuda: "|E| / (|V| × (|V| − 1))" },
    { nome: "camadas", valor: camadas, ajuda: "conjuntos de chaves diferentes" },
    { nome: "casas livres", valor: livres, ajuda: "o grafo de posições teria esse número de nós" },
    { nome: "armadilhas", valor: armadilhas, ajuda: "estados que nunca chegam ao G" },
  ];

  const maiorPassos = Math.max(1, ...ALGORITMOS.map((a) => dados.algoritmos[a].passos ?? 0));
  const maiorCusto = Math.max(1, ...ALGORITMOS.map((a) => dados.algoritmos[a].custo ?? 0));

  return (
    <section className="metricas" aria-label="Métricas do grafo de estados">
      <dl className="estatisticas">
        {itens.map((m) => (
          <div key={m.nome} title={m.ajuda}>
            <dt>{m.nome}</dt>
            <dd><NumeroAnimado valor={m.valor} casas={m.casas} /></dd>
          </div>
        ))}
      </dl>

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
