// [IA] Claude Code (Claude Opus 5.5) – painel de métricas do grafo de estados e tabela dos três algoritmos no mesmo mapa
import { motion } from "motion/react";
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
    { nome: "densidade", valor: dados.metricas.densidade, casas: 4, ajuda: "|E| / (|V|·(|V|−1))" },
    { nome: "camadas", valor: camadas, ajuda: "conjuntos de chaves diferentes" },
    { nome: "casas livres", valor: livres, ajuda: "o grafo de posições teria esse número de nós" },
    { nome: "armadilhas", valor: armadilhas, ajuda: "estados que nunca chegam ao G" },
  ];

  return (
    <section className="metricas" aria-label="Métricas do grafo de estados">
      <div className="contadores">
        {itens.map((m, i) => (
          <motion.div key={m.nome} className="contador-cartao" title={m.ajuda}
            initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
            <NumeroAnimado valor={m.valor} casas={m.casas} className="contador-valor" />
            <span className="contador-nome">{m.nome}</span>
          </motion.div>
        ))}
      </div>

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
                  <td className="numero">{r.passos ?? "-"}</td>
                  <td className="numero">{r.custo ?? "-"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
