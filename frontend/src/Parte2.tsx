// Parte 2: números do grafo, caminhos e ciclos dos algoritmos, desempenho e as visualizações de AVD com as notas do grupo
// [IA] Claude Code (Claude Opus 5.5) – Parte 2 mais enxuta: sem funil, sem lista de ciclos de ida e volta, sem transferências por arco e sem as figuras A1 a A4, que repetiam as abas Caminhos e Desempenho
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";
import { carregarParte2 } from "./api";
import { Galeria, tituloDoArquivo, type GrupoDaGaleria } from "./componentes/Galeria";
import { Cartao, Carregando, Jogada, MiniEscudo } from "./componentes/Futebol";
import { NumeroAnimado } from "./componentes/NumeroAnimado";
import { NotaCorrida } from "./componentes/TextoDaNota";
import { Topo, type Aba } from "./componentes/Topo";
import type { DadosDaParte2, Figura, ParDoDijkstra } from "./tipos";

type Secao = "geral" | "caminhos" | "desempenho" | "figuras";

const ABAS: Aba<Secao>[] = [
  { id: "geral", nome: "Visão geral" },
  { id: "caminhos", nome: "Caminhos e ciclos" },
  { id: "desempenho", nome: "Desempenho" },
  { id: "figuras", nome: "Visualizações de AVD" },
];

const NOME = { BFS: "BFS", DFS: "DFS", DIJKSTRA: "Dijkstra", BELLMAN_FORD: "Bellman-Ford" } as Record<string, string>;
// mesma ordem e cores das figuras do src/viz_parte2.py
const COR = { BFS: "#2a78d6", DFS: "#eb6834", DIJKSTRA: "#1baf7a", BELLMAN_FORD: "#9a5fd8" } as Record<string, string>;

const formatoEuro = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "EUR", notation: "compact", maximumFractionDigits: 1 });
const euro = (v: number) => formatoEuro.format(v);
const TIPO_DE_ARCO: Record<string, string> = { arvore: "árvore", retorno: "retorno", avanco: "avanço", cruzamento: "cruzamento" };
const numero = (v: number, casas = 0) => v.toLocaleString("pt-BR", { maximumFractionDigits: casas, minimumFractionDigits: casas });

function Rota({ clubes, ciclo }: { clubes: string[]; ciclo?: boolean }) {
  if (clubes.length <= 5) return <Jogada clubes={clubes} ciclo={ciclo} />;
  return (
    <ol className={ciclo ? "rota ciclo" : "rota"}>
      {clubes.map((clube, i) => (
        <motion.li key={`${clube}-${i}`} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.04 * i }}>
          <span className="rota-clube"><MiniEscudo nome={clube} />{clube}</span>
        </motion.li>
      ))}
    </ol>
  );
}

function VisaoGeral({ dados }: { dados: DadosDaParte2 }) {
  const d = dados.relatorio.dataset;
  const ciclos2 = dados.relatorio.ciclos_de_comprimento_2;
  const placar = [
    { nome: "clubes", detalhe: "nós", valor: d.V },
    { nome: "pares de clubes", detalhe: "arcos", valor: d.E },
    { nome: "arcos com peso negativo", detalhe: "%", valor: d.arcos_peso_negativo_pct, casas: 2 },
    { nome: "ciclos negativos", detalhe: "de 2 arcos", valor: ciclos2.total },
  ];
  return (
    <div className="parte2-grade">
      <section className="placar" aria-label="Números do grafo">
        {placar.map((c) => (
          <div key={c.nome} className="placar-item">
            <NumeroAnimado valor={c.valor} casas={c.casas} className="placar-valor" />
            <span className="placar-nome">{c.nome} <small>{c.detalhe}</small></span>
          </div>
        ))}
      </section>

      <section className="cartao">
        <h3 className="cartao-titulo">Ficha do grafo</h3>
        <dl className="ficha">
          <div><dt>Nó</dt><dd>clube</dd></div>
          <div><dt>Arco</dt><dd>clube que vendeu → clube que comprou</dd></div>
          <div><dt>Peso</dt><dd>valor pago − valor de mercado, somado nas transferências do par</dd></div>
          <div><dt>Pesos</dt><dd className="numero-linha"><span>{euro(d.peso_min)} <small>mín</small></span> <span>{euro(d.peso_mediana)} <small>mediana</small></span> <span>{euro(d.peso_max)} <small>máx</small></span></dd></div>
          <div><dt>Por temporada</dt><dd className="numero-linha">{numero(d.temporal.V)} nós, {numero(d.temporal.E)} arcos</dd></div>
        </dl>
        <span className="detalhe">Fonte: {d.fonte}</span>
      </section>
    </div>
  );
}

function CartaoDoPar({ par }: { par: ParDoDijkstra }) {
  return (
    <article className="cartao par">
      <header>
        <h4>{par.origem} → {par.destino}</h4>
        <span className={par.custo_original < 0 ? "valor negativo" : "valor"}>{euro(par.custo_original)}</span>
      </header>
      <Rota clubes={par.caminho} />
      <span className="detalhe">{par.arcos} arcos no Dijkstra, {par.passos_bfs} arcos no menor caminho da BFS</span>
    </article>
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
          {r.dijkstra.pares.map((par) => <CartaoDoPar key={`${par.origem}-${par.destino}`} par={par} />)}
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
          </article>
          {r.bellman_ford.com_ciclo_negativo.map((c) => (
            <article key={c.grafo} className="cartao par ciclo">
              <header>
                <h4><Cartao cor="vermelho" /> Ciclo negativo a partir de {c.fonte}</h4>
                <span className="valor negativo">{euro(c.ciclo.custo)}</span>
              </header>
              <span className="detalhe">{c.grafo}: {numero(c.ordem)} nós, {numero(c.tamanho)} arcos</span>
              <Rota clubes={c.ciclo.clubes} ciclo />
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
  const valores = r.escalabilidade.flatMap((p) => [p.tempo_relativo, p.teoria_relativa]).filter((v) => v > 0);
  const piso = Math.floor(Math.log10(Math.min(...valores)));
  const decadas = Array.from({ length: -piso + 1 }, (_, i) => 10 ** -i);
  const [L, R, T, B] = [52, 14, 12, 34];
  const [W, H] = [360, 230];
  const x = (pct: number) => L + (pct / 100) * (W - L - R);
  const y = (v: number) => T + (Math.log10(v) / piso) * (H - T - B);
  const rotuloDecada = (v: number) => (v >= 1 ? "1" : v.toLocaleString("pt-BR", { maximumFractionDigits: 4 }));
  return (
    <div className="parte2-grade">
      <section className="cartao">
        <div className="cartao-cabeca">
          <h3 className="cartao-titulo">Escalabilidade</h3>
          <span className="detalhe">tempo medido (média de {r.parametros.repeticoes} execuções) e complexidade teórica, os dois relativos ao grafo completo; eixo vertical em log</span>
        </div>
        <div className="escalas">
          {algoritmos.map((alg) => {
            const pontos = r.escalabilidade.filter((e) => e.algoritmo === alg).sort((a, b) => a.tamanho_pct - b.tamanho_pct);
            const linha = (chave: "tempo_relativo" | "teoria_relativa") => pontos.map((p, i) => `${i ? "L" : "M"} ${x(p.tamanho_pct)} ${y(p[chave])}`).join(" ");
            const emFoco = foco?.alg === alg ? pontos.find((q) => q.tamanho_pct === foco.pct) : undefined;
            return (
              <figure key={alg} className="escala">
                <figcaption>
                  <b style={{ color: COR[alg] }}>{NOME[alg]}</b>
                  <span>{pontos[0]?.complexidade}</span>
                </figcaption>
                <svg viewBox={`0 0 ${W} ${H}`} className="grafico-escala" role="img" aria-label={`${NOME[alg]}: tempo medido contra a teoria`}>
                  {decadas.map((v) => (
                    <g key={v}>
                      <line x1={L} x2={W - R} y1={y(v)} y2={y(v)} className="grade-grafico" />
                      <text x={L - 8} y={y(v) + 4} className="eixo-grafico" textAnchor="end">{rotuloDecada(v)}</text>
                    </g>
                  ))}
                  <line x1={L} x2={W - R} y1={H - B} y2={H - B} className="eixo-base" />
                  {[10, 25, 50, 75, 100].map((pct) => (
                    <text key={pct} x={x(pct)} y={H - B + 18} className="eixo-grafico" textAnchor="middle">{pct}%</text>
                  ))}
                  <path d={linha("teoria_relativa")} fill="none" stroke="var(--texto-3)" strokeWidth={1.6} strokeDasharray="4 4" />
                  <motion.path d={linha("tempo_relativo")} fill="none" stroke={COR[alg]} strokeWidth={2.6}
                    initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 0.8 }} />
                  {pontos.map((p) => (
                    <circle key={p.tamanho_pct} cx={x(p.tamanho_pct)} cy={y(p.tempo_relativo)} r={emFoco === p ? 6 : 4}
                      fill={COR[alg]} stroke="#fff" strokeWidth={1.5} tabIndex={0}
                      onMouseEnter={() => setFoco({ alg, pct: p.tamanho_pct })} onMouseLeave={() => setFoco(null)}
                      onFocus={() => setFoco({ alg, pct: p.tamanho_pct })} onBlur={() => setFoco(null)}>
                      <title>{`${p.tamanho_pct}% do grafo: ${numero(p.V)} nós, ${numero(p.E)} arcos, ${numero(p.media_s * 1000, 2)} ms`}</title>
                    </circle>
                  ))}
                </svg>
                <div className="legenda-escala">
                  <span><i style={{ background: COR[alg] }} />medido</span>
                  <span><i className="tracejado" />teoria</span>
                  <span className="foco">{emFoco ? `${emFoco.tamanho_pct}%: ${numero(emFoco.media_s * 1000, 2)} ms` : ""}</span>
                </div>
              </figure>
            );
          })}
        </div>
      </section>

      <section className="cartao">
        <div className="cartao-cabeca">
          <h3 className="cartao-titulo">Classificação no grafo completo</h3>
          <span className="detalhe">{numero(completo[0]?.V ?? 0)} nós, {numero(completo[0]?.E ?? 0)} arcos</span>
        </div>
        <table className="tabela-algoritmos simples classificacao">
          <thead><tr><th className="numero">#</th><th>algoritmo</th><th>tarefa</th><th className="numero">média</th><th className="numero">desvio</th></tr></thead>
          <tbody>
            {[...completo].sort((a, b) => a.media_s - b.media_s).map((d, i) => (
              <tr key={d.algoritmo}>
                <td className="numero posicao">{i + 1}</td>
                <th scope="row"><i className="ponto" style={{ background: COR[d.algoritmo] }} /> {NOME[d.algoritmo]}</th>
                <td>{d.tarefa}</td>
                <td className="numero">{numero(d.media_s * 1000, 2)} ms</td>
                <td className="numero">{numero(d.desvio_s * 1000, 2)} ms</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

const GRUPOS_DE_FIGURA: [string, string][] = [["E", "Exploratórias"], ["X", "Explanatórias"]];

function Figuras({ figuras }: { figuras: Figura[] }) {
  const grupos: GrupoDaGaleria[] = GRUPOS_DE_FIGURA.map(([letra, nome]) => ({
    nome,
    itens: figuras.filter((f) => f.codigo.startsWith(letra)).map((f) => ({
      id: f.arquivo, codigo: f.codigo, titulo: tituloDoArquivo(f.arquivo), subtitulo: f.tipo || f.arquivo,
      src: `/parte2/${f.arquivo}`, nota: f.nota ? <NotaCorrida texto={f.nota} /> : null,
    })),
  })).filter((g) => g.itens.length);
  return <Galeria grupos={grupos} />;
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
      <Topo parte="Parte 2: rede de transferências" abas={ABAS} ativa={secao} aoTrocar={setSecao} aoInicio={aoInicio} />
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
                : !dados ? <Carregando texto="Carregando os resultados da Parte 2…" />
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
