// [IA] Claude Code (Claude Opus 5.5) – Parte 2: números do grafo, caminhos e ciclos dos algoritmos, desempenho e as visualizações de AVD com as notas do grupo
// [IA] Claude Code (Claude Opus 5.5) – Parte 2 mais enxuta: sem funil, sem lista de ciclos de ida e volta, sem transferências por arco e sem as figuras A1 a A4, que repetiam as abas Caminhos e Desempenho
import { ChevronDown } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState, type ReactNode } from "react";
import { carregarParte2 } from "./api";
import { Galeria, tituloDoArquivo, type GrupoDaGaleria } from "./componentes/Galeria";
import { Cartao, Carregando, Jogada, MiniEscudo, corDoClube } from "./componentes/Futebol";
import { Boneco } from "./componentes/Pixel";
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

function Recolhivel({ titulo, valor, classe = "", children }: { titulo: ReactNode; valor: number; classe?: string; children: ReactNode }) {
  const [aberto, setAberto] = useState(false);
  return (
    <article className={`cartao par recolhivel ${classe}${aberto ? " aberto" : ""}`}>
      <h4 className="par-titulo">
        <button type="button" className="par-cabeca" onClick={() => setAberto((a) => !a)} aria-expanded={aberto}>
          <span className="par-nome">{titulo}</span>
          <span className={valor < 0 ? "valor negativo" : "valor"}>{euro(valor)}</span>
          <ChevronDown size={18} aria-hidden className="par-seta" />
        </button>
      </h4>
      <AnimatePresence initial={false}>
        {aberto && (
          <motion.div className="par-corpo" initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.25 }}>
            <div>{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </article>
  );
}

function FichaDoJogador({ nome, temporada, arco, peso }: { nome: string; temporada: string; arco: string; peso: number | null }) {
  const [de, para] = arco.split(" -> ");
  return (
    <motion.div className="ficha-jogador" initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }}>
      <svg viewBox="-14 -42 28 46" className="ficha-boneco" aria-hidden>
        <g className="ficha-corpo"><Boneco camisa={corDoClube(para)} /></g>
        <g className="ficha-bola">
          <circle cx={5} cy={-2} r={2.4} fill="#fff" stroke="#14201a" strokeWidth={0.6} />
          <circle cx={5} cy={-2} r={0.9} fill="#14201a" />
        </g>
      </svg>
      <div className="ficha-texto">
        <strong>{nome}</strong>
        <span><MiniEscudo nome={de} /> {de} → <MiniEscudo nome={para} /> {para}</span>
        <span>transferência na temporada {temporada}</span>
        {peso !== null && (
          <span><b className={peso < 0 ? "valor negativo" : "valor"}>{euro(peso)}</b> <small>pago − valor de mercado</small></span>
        )}
      </div>
    </motion.div>
  );
}

function TabelaDeTransferencias({ lista }: { lista: Record<string, string[]> }) {
  const [aberto, setAberto] = useState<string | null>(null);
  const linhas = Object.entries(lista).flatMap(([arco, jogadores]) => jogadores.map((texto, i) => {
    const partes = /^(.*) \((\d\d\/\d\d)\): (-?[\d.]+)$/.exec(texto);
    return {
      arco, i, total: jogadores.length, chave: `${arco}#${i}`,
      nome: partes ? partes[1] : texto,
      temporada: partes ? partes[2] : "",
      peso: partes ? Number(partes[3].replace(/\./g, "")) : null,
    };
  }));
  return (
    <table className="tabela-algoritmos simples transferencias">
      <thead><tr><th>seta</th><th>jogador</th><th>temporada</th><th className="numero">pago − valor de mercado</th></tr></thead>
      <tbody>
        {linhas.map((l) => [
          <tr key={l.chave}>
            {l.i === 0 && (
              <th scope="rowgroup" rowSpan={l.total + (aberto?.startsWith(`${l.arco}#`) ? 1 : 0)}>{l.arco.replace(" -> ", " → ")}</th>
            )}
            <td>
              <button type="button" className="nome-jogador" aria-expanded={aberto === l.chave}
                onClick={() => setAberto((a) => (a === l.chave ? null : l.chave))}>{l.nome}</button>
            </td>
            <td>{l.temporada}</td>
            <td className={l.peso !== null && l.peso < 0 ? "numero negativo" : "numero"}>{l.peso === null ? "" : euro(l.peso)}</td>
          </tr>,
          aberto === l.chave && (
            <tr key={`${l.chave}-ficha`} className="linha-ficha">
              <td colSpan={3}><FichaDoJogador nome={l.nome} temporada={l.temporada} arco={l.arco} peso={l.peso} /></td>
            </tr>
          ),
        ])}
      </tbody>
    </table>
  );
}

function CartaoDoPar({ par }: { par: ParDoDijkstra }) {
  return (
    <Recolhivel titulo={`${par.origem} → ${par.destino}`} valor={par.custo_original}>
      <Rota clubes={par.caminho} />
      <span className="detalhe">{par.arcos} arcos no Dijkstra, {par.passos_bfs} arcos no menor caminho da BFS</span>
      <TabelaDeTransferencias lista={par.transferencias} />
    </Recolhivel>
  );
}

function Caminhos({ dados }: { dados: DadosDaParte2 }) {
  const r = dados.relatorio;
  const semCiclo = r.bellman_ford.sem_ciclo_negativo;
  return (
    <div className="parte2-grade">
      <section>
        <h3 className="titulo-secao">Dijkstra: menor custo entre 6 pares</h3>
        <p className="texto-secao">Pesos deslocados com <code>{r.dijkstra.transformacao.formula}</code> (+{euro(r.dijkstra.transformacao.deslocamento_eur)} por arco), porque o Dijkstra não aceita peso negativo. O custo mostrado é o original.</p>
        <div className="pares-lista">
          {r.dijkstra.pares.map((par) => <CartaoDoPar key={`${par.origem}-${par.destino}`} par={par} />)}
        </div>
      </section>

      <section>
        <h3 className="titulo-secao">Bellman-Ford</h3>
        <div className="pares-lista">
          <Recolhivel titulo={`Sem ciclo negativo: ${semCiclo.fonte} → ${semCiclo.menor_custo.destino}`} valor={semCiclo.menor_custo.custo}>
            <span className="detalhe">{semCiclo.grafo}: {numero(semCiclo.ordem)} nós, {numero(semCiclo.tamanho)} arcos, {numero(semCiclo.arcos_negativos)} negativos</span>
            <Rota clubes={semCiclo.menor_custo.caminho} />
            <TabelaDeTransferencias lista={semCiclo.menor_custo.transferencias} />
          </Recolhivel>
          {r.bellman_ford.com_ciclo_negativo.map((c) => (
            <Recolhivel key={c.grafo} classe="ciclo" titulo={<><Cartao cor="vermelho" /> Ciclo negativo a partir de {c.fonte}</>} valor={c.ciclo.custo}>
              <span className="detalhe">{c.grafo}: {numero(c.ordem)} nós, {numero(c.tamanho)} arcos</span>
              <Rota clubes={c.ciclo.clubes} ciclo />
              <TabelaDeTransferencias lista={c.ciclo.transferencias} />
            </Recolhivel>
          ))}
        </div>
      </section>

      <section>
        <h3 className="titulo-secao">BFS e DFS a partir de 3 clubes</h3>
        <div className="pares">
          {r.bfs.map((b, i) => {
            const dfs = r.dfs[i];
            return (
              <article key={b.nome} className="cartao par">
                <header>
                  <h4>{b.nome}</h4>
                  <span className="valor">{numero(b.alcancados)} alcançados</span>
                </header>
                <span className="rotulo-pequeno">BFS: clubes por nível</span>
                <div className="tabela-rolagem">
                  <table className="tabela-algoritmos simples tabela-compacta">
                    <tbody>
                      <tr><th scope="row">nível</th>{b.camadas.map((_, k) => <td key={k} className="numero">{k}</td>)}</tr>
                      <tr><th scope="row">clubes</th>{b.camadas.map((n, k) => <td key={k} className="numero">{numero(n)}</td>)}</tr>
                    </tbody>
                  </table>
                </div>
                <span className="rotulo-pequeno">DFS: tipos de arco {dfs.tem_ciclo ? "(tem ciclo)" : ""}</span>
                <table className="tabela-algoritmos simples tabela-compacta">
                  <tbody>
                    {Object.entries(dfs.arcos).map(([tipo, n]) => (
                      <tr key={tipo}><th scope="row">{TIPO_DE_ARCO[tipo] ?? tipo}</th><td className="numero">{numero(n)}</td></tr>
                    ))}
                  </tbody>
                </table>
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
  const completo = r.desempenho.filter((d) => d.tamanho_pct === 100);
  return (
    <div className="parte2-grade">
      <section className="cartao">
        <div className="cartao-cabeca">
          <h3 className="cartao-titulo">Escalabilidade</h3>
          <span className="detalhe">tempo médio de {r.parametros.repeticoes} execuções; "medido" e "teoria" são relativos ao grafo completo (100% = 1)</span>
        </div>
        <div className="escalas">
          {algoritmos.map((alg) => {
            const pontos = r.escalabilidade.filter((e) => e.algoritmo === alg).sort((a, b) => a.tamanho_pct - b.tamanho_pct);
            return (
              <figure key={alg} className="escala">
                <figcaption>
                  <b>{NOME[alg]}</b>
                  <span>{pontos[0]?.complexidade}</span>
                </figcaption>
                <table className="tabela-algoritmos simples tabela-compacta">
                  <thead>
                    <tr><th>grafo</th><th className="numero">nós</th><th className="numero">arcos</th><th className="numero">tempo</th>
                      <th className="numero">medido</th><th className="numero">teoria</th></tr>
                  </thead>
                  <tbody>
                    {pontos.map((p) => (
                      <tr key={p.tamanho_pct}>
                        <th scope="row">{p.tamanho_pct}%</th>
                        <td className="numero">{numero(p.V)}</td>
                        <td className="numero">{numero(p.E)}</td>
                        <td className="numero">{numero(p.media_s * 1000, 2)} ms</td>
                        <td className="numero">{numero(p.tempo_relativo, 3)}</td>
                        <td className="numero">{numero(p.teoria_relativa, 3)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
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
