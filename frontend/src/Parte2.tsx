// [IA] Claude Code (Claude Opus 5.5) – Parte 2: números do grafo, caminhos e ciclos dos algoritmos, desempenho e as figuras com as notas do grupo
import { ChevronDown, X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import { carregarParte2 } from "./api";
import { NumeroAnimado } from "./componentes/NumeroAnimado";
import { Topo, type Aba } from "./componentes/Topo";
import type { DadosDaParte2, Figura, ParDoDijkstra } from "./tipos";

type Secao = "geral" | "caminhos" | "desempenho" | "figuras";

const ABAS: Aba<Secao>[] = [
  { id: "geral", nome: "Visão geral" },
  { id: "caminhos", nome: "Caminhos e ciclos" },
  { id: "desempenho", nome: "Desempenho" },
  { id: "figuras", nome: "Figuras" },
];

const NOME = { BFS: "BFS", DFS: "DFS", DIJKSTRA: "Dijkstra", BELLMAN_FORD: "Bellman-Ford" } as Record<string, string>;
const COR = { BFS: "#2563eb", DFS: "#7c3aed", DIJKSTRA: "#059669", BELLMAN_FORD: "#ea580c" } as Record<string, string>;

const formatoEuro = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "EUR", notation: "compact", maximumFractionDigits: 1 });
const euro = (v: number) => formatoEuro.format(v);
const TIPO_DE_ARCO: Record<string, string> = { arvore: "árvore", retorno: "retorno", avanco: "avanço", cruzamento: "cruzamento" };
const numero = (v: number, casas = 0) => v.toLocaleString("pt-BR", { maximumFractionDigits: casas, minimumFractionDigits: casas });

function Rota({ clubes, ciclo }: { clubes: string[]; ciclo?: boolean }) {
  return (
    <ol className={ciclo ? "rota ciclo" : "rota"}>
      {clubes.map((clube, i) => (
        <motion.li key={`${clube}-${i}`} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.06 * i }}>
          <span className="rota-clube">{clube}</span>
        </motion.li>
      ))}
    </ol>
  );
}

function Transferencias({ lista }: { lista: Record<string, string[]> }) {
  const [aberto, setAberto] = useState(false);
  return (
    <div className="transferencias">
      <button type="button" className="chip" onClick={() => setAberto((a) => !a)} aria-expanded={aberto}>
        <ChevronDown size={14} aria-hidden style={{ transform: aberto ? "rotate(180deg)" : undefined, transition: "transform .2s" }} />
        {aberto ? "esconder as transferências" : "ver as transferências de cada arco"}
      </button>
      <AnimatePresence>
        {aberto && (
          <motion.dl initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}>
            {Object.entries(lista).map(([arco, jogadores]) => (
              <div key={arco}>
                <dt>{arco.replace("->", "→")}</dt>
                {jogadores.map((j) => <dd key={j}>{j}</dd>)}
              </div>
            ))}
          </motion.dl>
        )}
      </AnimatePresence>
    </div>
  );
}

function VisaoGeral({ dados }: { dados: DadosDaParte2 }) {
  const d = dados.relatorio.dataset;
  const maiorEtapa = Math.max(...d.funil.map((f) => f.linhas));
  const ciclos2 = dados.relatorio.ciclos_de_comprimento_2;
  const cartoes = [
    { nome: "clubes (nós)", valor: d.V },
    { nome: "pares de clubes (arcos)", valor: d.E },
    { nome: "% dos arcos com peso negativo", valor: d.arcos_peso_negativo_pct, casas: 2 },
    { nome: "pares com ciclo negativo de 2 arcos", valor: ciclos2.total },
  ];
  return (
    <div className="parte2-grade">
      <div className="contadores quatro">
        {cartoes.map((c, i) => (
          <motion.div key={c.nome} className="contador-cartao" initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.06 * i }}>
            <NumeroAnimado valor={c.valor} casas={c.casas} className="contador-valor" />
            <span className="contador-nome">{c.nome}</span>
          </motion.div>
        ))}
      </div>

      <section className="cartao">
        <span className="rotulo-pequeno">modelo</span>
        <p className="modelo-texto">
          <b>Nó</b> = clube. <b>Arco</b> = clube que vendeu → clube que comprou. <b>Peso</b> = valor pago menos valor de mercado,
          somado nas transferências do par. Fonte: {d.fonte}.
        </p>
        <div className="pesos">
          <span>menor peso <b>{euro(d.peso_min)}</b></span>
          <span>mediana <b>{euro(d.peso_mediana)}</b></span>
          <span>maior peso <b>{euro(d.peso_max)}</b></span>
          <span>grafo por temporada <b>{numero(d.temporal.V)} nós · {numero(d.temporal.E)} arcos</b></span>
        </div>
      </section>

      <section className="cartao">
        <span className="rotulo-pequeno">do arquivo bruto ao grafo</span>
        <ul className="funil">
          {d.funil.map((f, i) => (
            <li key={f.etapa}>
              <span className="funil-etapa">{f.etapa}</span>
              <div className="funil-barra">
                <motion.span initial={{ width: 0 }} animate={{ width: `${(f.linhas / maiorEtapa) * 100}%` }} transition={{ delay: 0.08 * i, duration: 0.6 }} />
              </div>
              <span className="funil-valor">{numero(f.linhas)}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="cartao">
        <span className="rotulo-pequeno">ciclos negativos de 2 arcos mais fortes (ida e volta)</span>
        <table className="tabela-algoritmos simples">
          <thead><tr><th>clubes</th><th className="numero">ida</th><th className="numero">volta</th><th className="numero">soma</th></tr></thead>
          <tbody>
            {ciclos2.mais_negativos.map((c) => (
              <tr key={c.clubes.join("|")}>
                <th scope="row">{c.clubes.join(" ⇄ ")}</th>
                <td className="numero">{euro(c.ida)}</td>
                <td className="numero">{euro(c.volta)}</td>
                <td className="numero">{euro(c.soma)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

function CartaoDoPar({ par, i }: { par: ParDoDijkstra; i: number }) {
  return (
    <motion.article className="cartao par" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
      <header>
        <h4>{par.origem} → {par.destino}</h4>
        <span className={par.custo_original < 0 ? "valor negativo" : "valor"}>{euro(par.custo_original)}</span>
      </header>
      <Rota clubes={par.caminho} />
      <span className="detalhe">{par.arcos} arcos no Dijkstra · {par.passos_bfs} arcos no menor caminho da BFS</span>
      <Transferencias lista={par.transferencias} />
    </motion.article>
  );
}

function Caminhos({ dados }: { dados: DadosDaParte2 }) {
  const r = dados.relatorio;
  const semCiclo = r.bellman_ford.sem_ciclo_negativo;
  const maiorCamada = Math.max(...r.bfs.flatMap((b) => b.camadas));
  return (
    <div className="parte2-grade">
      <section>
        <h3 className="titulo-secao">Dijkstra: menor custo entre 6 pares</h3>
        <p className="texto-secao">Pesos deslocados com <code>{r.dijkstra.transformacao.formula}</code> (+{euro(r.dijkstra.transformacao.deslocamento_eur)} por arco), porque o Dijkstra não aceita peso negativo. O custo mostrado é o original.</p>
        <div className="pares">
          {r.dijkstra.pares.map((par, i) => <CartaoDoPar key={`${par.origem}-${par.destino}`} par={par} i={i} />)}
        </div>
      </section>

      <section>
        <h3 className="titulo-secao">Bellman-Ford</h3>
        <div className="pares">
          <article className="cartao par">
            <header>
              <h4>Sem ciclo negativo: {semCiclo.fonte} → {semCiclo.menor_custo.destino}</h4>
              <span className="valor negativo">{euro(semCiclo.menor_custo.custo)}</span>
            </header>
            <span className="detalhe">{semCiclo.grafo}: {numero(semCiclo.ordem)} nós, {numero(semCiclo.tamanho)} arcos, {numero(semCiclo.arcos_negativos)} negativos</span>
            <Rota clubes={semCiclo.menor_custo.caminho} />
            <Transferencias lista={semCiclo.menor_custo.transferencias} />
          </article>
          {r.bellman_ford.com_ciclo_negativo.map((c) => (
            <article key={c.grafo} className="cartao par ciclo">
              <header>
                <h4>Ciclo negativo a partir de {c.fonte}</h4>
                <span className="valor negativo">{euro(c.ciclo.custo)}</span>
              </header>
              <span className="detalhe">{c.grafo}: {numero(c.ordem)} nós, {numero(c.tamanho)} arcos</span>
              <Rota clubes={c.ciclo.clubes} ciclo />
              <Transferencias lista={c.ciclo.transferencias} />
            </article>
          ))}
        </div>
      </section>

      <section>
        <h3 className="titulo-secao">BFS e DFS a partir de 3 clubes</h3>
        <div className="pares">
          {r.bfs.map((b, i) => {
            const dfs = r.dfs[i];
            const totalArcos = Object.values(dfs.arcos).reduce((t, v) => t + v, 0);
            return (
              <article key={b.nome} className="cartao par">
                <header>
                  <h4>{b.nome}</h4>
                  <span className="valor">{numero(b.alcancados)} alcançados</span>
                </header>
                <span className="rotulo-pequeno">BFS: clubes por nível</span>
                <div className="niveis" role="img" aria-label={`Níveis da BFS a partir de ${b.nome}: ${b.camadas.join(", ")}`}>
                  {b.camadas.map((n, k) => (
                    <div key={k} className="nivel" title={`nível ${k}: ${n} clubes`}>
                      <motion.span initial={{ height: 0 }} animate={{ height: `${Math.max(3, (n / maiorCamada) * 100)}%` }} transition={{ delay: 0.04 * k }} />
                      <small>{k}</small>
                    </div>
                  ))}
                </div>
                <span className="rotulo-pequeno">DFS: tipos de arco {dfs.tem_ciclo ? "(tem ciclo)" : ""}</span>
                <div className="barra-arcos">
                  {Object.entries(dfs.arcos).map(([tipo, n]) => (
                    <span key={tipo} className={`arco-${tipo}`} style={{ width: `${(n / totalArcos) * 100}%` }} title={`${TIPO_DE_ARCO[tipo] ?? tipo}: ${numero(n)}`} />
                  ))}
                </div>
                <div className="legenda-arcos">
                  {Object.entries(dfs.arcos).map(([tipo, n]) => <span key={tipo}><i className={`arco-${tipo}`} />{TIPO_DE_ARCO[tipo] ?? tipo} {numero(n)}</span>)}
                </div>
              </article>
            );
          })}
        </div>
      </section>
    </div>
  );
}

function Desempenho({ dados }: { dados: DadosDaParte2 }) {
  const r = dados.relatorio;
  const algoritmos = ["BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD"];
  const [foco, setFoco] = useState<{ alg: string; pct: number } | null>(null);
  const completo = r.desempenho.filter((d) => d.tamanho_pct === 100);
  return (
    <div className="parte2-grade">
      <p className="texto-secao">Tempo medido (média de {r.parametros.repeticoes} execuções) e a curva da complexidade teórica, os dois divididos pelo valor no grafo completo. Escala log no eixo vertical.</p>
      <div className="escalas">
        {algoritmos.map((alg) => {
          const pontos = r.escalabilidade.filter((e) => e.algoritmo === alg).sort((a, b) => a.tamanho_pct - b.tamanho_pct);
          const valores = pontos.flatMap((p) => [p.tempo_relativo, p.teoria_relativa]).filter((v) => v > 0);
          const minimo = Math.log10(Math.min(...valores));
          const x = (pct: number) => 30 + (pct / 100) * 550;
          const y = (v: number) => 16 + (1 - (Math.log10(v) - minimo) / (0 - minimo || 1)) * 190;
          const linha = (chave: "tempo_relativo" | "teoria_relativa") => pontos.map((p, i) => `${i ? "L" : "M"} ${x(p.tamanho_pct)} ${y(p[chave])}`).join(" ");
          return (
            <section key={alg} className="cartao">
              <header className="escala-topo">
                <h4 style={{ color: COR[alg] }}>{NOME[alg]}</h4>
                <code>{pontos[0]?.complexidade}</code>
              </header>
              <svg viewBox="0 0 620 240" className="grafico-escala" role="img" aria-label={`${NOME[alg]}: tempo medido contra a teoria`}>
                {[10, 25, 50, 75, 100].map((pct) => (
                  <g key={pct}>
                    <line x1={x(pct)} x2={x(pct)} y1={16} y2={206} className="grade-grafico" />
                    <text x={x(pct)} y={230} className="eixo-grafico" textAnchor="middle">{pct}%</text>
                  </g>
                ))}
                <motion.path d={linha("teoria_relativa")} fill="none" stroke="#85796b" strokeWidth={2} strokeDasharray="5 5"
                  initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 1 }} />
                <motion.path d={linha("tempo_relativo")} fill="none" stroke={COR[alg]} strokeWidth={3}
                  initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 1, delay: 0.2 }} />
                {pontos.map((p) => (
                  <circle key={p.tamanho_pct} cx={x(p.tamanho_pct)} cy={y(p.tempo_relativo)} r={foco?.alg === alg && foco.pct === p.tamanho_pct ? 7 : 5}
                    fill={COR[alg]} stroke="#fff" strokeWidth={2} onMouseEnter={() => setFoco({ alg, pct: p.tamanho_pct })}
                    onMouseLeave={() => setFoco(null)} tabIndex={0} onFocus={() => setFoco({ alg, pct: p.tamanho_pct })} onBlur={() => setFoco(null)}>
                    <title>{`${p.tamanho_pct}% do grafo · ${numero(p.V)} nós, ${numero(p.E)} arcos · ${numero(p.media_s * 1000, 2)} ms`}</title>
                  </circle>
                ))}
              </svg>
              <div className="legenda-linhas horizontal">
                <span><i className="ponto" style={{ background: COR[alg] }} />medido</span>
                <span><i className="tracejado" />teoria</span>
                {foco?.alg === alg && (() => {
                  const p = pontos.find((q) => q.tamanho_pct === foco.pct)!;
                  return <span className="foco">{p.tamanho_pct}%: {numero(p.media_s * 1000, 2)} ms</span>;
                })()}
              </div>
            </section>
          );
        })}
      </div>

      <section className="cartao">
        <span className="rotulo-pequeno">grafo completo ({numero(completo[0]?.V ?? 0)} nós, {numero(completo[0]?.E ?? 0)} arcos)</span>
        <table className="tabela-algoritmos simples">
          <thead><tr><th>algoritmo</th><th>tarefa</th><th className="numero">média</th><th className="numero">desvio</th><th className="numero">memória</th></tr></thead>
          <tbody>
            {completo.map((d) => (
              <tr key={d.algoritmo}>
                <th scope="row" style={{ color: COR[d.algoritmo] }}>{NOME[d.algoritmo]}</th>
                <td>{d.tarefa}</td>
                <td className="numero">{numero(d.media_s * 1000, 2)} ms</td>
                <td className="numero">{numero(d.desvio_s * 1000, 2)} ms</td>
                <td className="numero">{d.memoria_pico_kb === null ? "não medida" : `${numero(d.memoria_pico_kb, 0)} KB`}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

function Figuras({ figuras }: { figuras: Figura[] }) {
  const [aberta, setAberta] = useState<Figura | null>(null);
  useEffect(() => {
    function tecla(ev: KeyboardEvent) {
      if (ev.key === "Escape") setAberta(null);
    }
    window.addEventListener("keydown", tecla);
    return () => window.removeEventListener("keydown", tecla);
  }, []);
  return (
    <>
      <div className="figuras">
        {figuras.map((f, i) => (
          <motion.button key={f.arquivo} type="button" className="figura" onClick={() => setAberta(f)}
            initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.04 * i }} whileHover={{ y: -4 }}>
            <img src={`/parte2/${f.arquivo}`} alt={`${f.codigo}: ${f.arquivo}`} loading="lazy" />
            <span className="figura-rotulo"><b>{f.codigo}</b> {f.tipo}</span>
          </motion.button>
        ))}
      </div>
      <AnimatePresence>
        {aberta && (
          <motion.div className="visor" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setAberta(null)}
            role="dialog" aria-modal="true" aria-label={`Figura ${aberta.codigo}`}>
            <motion.div className="visor-conteudo" initial={{ scale: 0.95, y: 10 }} animate={{ scale: 1, y: 0 }} onClick={(ev) => ev.stopPropagation()}>
              <button type="button" className="botao-icone visor-fechar" onClick={() => setAberta(null)} aria-label="Fechar"><X size={18} /></button>
              <img src={`/parte2/${aberta.arquivo}`} alt={`${aberta.codigo}: ${aberta.arquivo}`} />
              <div className="visor-texto">
                <span className="rotulo-pequeno">{aberta.codigo} · {aberta.tipo} · {aberta.arquivo}</span>
                {aberta.nota && <p>{aberta.nota}</p>}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

export function Parte2({ aoInicio }: { aoInicio: () => void }) {
  const [secao, setSecao] = useState<Secao>(() => {
    const pedida = new URLSearchParams(window.location.search).get("secao") as Secao;
    return ABAS.some((aba) => aba.id === pedida) ? pedida : "geral";
  });
  const [dados, setDados] = useState<DadosDaParte2 | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    carregarParte2().then(setDados).catch((e: Error) => setErro(e.message));
  }, []);

  useEffect(() => {
    window.history.replaceState(null, "", `?parte=2&secao=${secao}`);
  }, [secao]);

  return (
    <div className="app">
      <div className="fundo-animado" aria-hidden />
      <Topo parte="Parte 2 · Rede de transferências" abas={ABAS} ativa={secao} aoTrocar={setSecao} aoInicio={aoInicio} />
      <main className="corpo sem-lateral">
        <div className="conteudo">
          <AnimatePresence mode="wait">
            <motion.div key={secao} className="vista" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.25 }}>
              <div className="titulo-vista">
                <div>
                  <h2>{ABAS.find((a) => a.id === secao)!.nome}</h2>
                  <span>Transfermarkt: clubes ligados pelas transferências de jogadores</span>
                </div>
              </div>
              {erro ? <div className="carregando">{erro}</div>
                : !dados ? <div className="carregando"><span className="girando" />Carregando os resultados da Parte 2…</div>
                  : secao === "geral" ? <VisaoGeral dados={dados} />
                    : secao === "caminhos" ? <Caminhos dados={dados} />
                      : secao === "desempenho" ? <Desempenho dados={dados} />
                        : <Figuras figuras={dados.figuras} />}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
