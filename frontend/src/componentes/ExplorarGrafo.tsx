// [IA] Claude Code (Claude Opus 5.5) – grafo interativo da Visão geral da Parte 2 (pedido da professora no acompanhamento): escolher o grafo, a origem, o destino e o algoritmo e ver o caminho desenhado sobre a rede
import { Play } from "lucide-react";
import { motion } from "motion/react";
import { useEffect, useMemo, useRef, useState, type CSSProperties, type KeyboardEvent, type ReactNode } from "react";
import { calcularRota, carregarGrafoDaParte2 } from "../api";
import type { AlgoritmoDaParte2, ClubeDoGrafo, GrafoDaParte2, NoDaRota, ResumoDoGrafoDaParte2, RotaDaParte2, TrechoDaRota } from "../tipos";
import { Carregando, EscudoDoClube, MiniEscudo } from "./Futebol";

const ALGORITMOS: AlgoritmoDaParte2[] = ["BFS", "DFS", "DIJKSTRA", "BELLMAN_FORD"];
const O_QUE_ACHA: Record<AlgoritmoDaParte2, string> = {
  BFS: "procura um caminho com a menor quantidade de arcos",
  DFS: "explora os caminhos em profundidade até encontrar o destino",
  DIJKSTRA: "procura o menor custo usando pesos ajustados",
  BELLMAN_FORD: "procura o menor custo mesmo com pesos negativos, desde que não exista ciclo negativo relevante",
};
const NOME_DO_GRAFO: Record<GrafoDaParte2, string> = { clubes: "Clubes", temporal: "Clubes por temporada" };
const STATUS: Record<RotaDaParte2["status"], string> = { OK: "caminho encontrado", SEM_CAMINHO: "sem caminho", CICLO_NEGATIVO: "ciclo negativo" };
const temporadaCurta = (s: number) => `${String(s % 100).padStart(2, "0")}/${String((s + 1) % 100).padStart(2, "0")}`;
const semAcento = (t: string) => t.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase();

function EscolhaDeClube({ rotulo, clubes, valor, aoEscolher }: {
  rotulo: string; clubes: ClubeDoGrafo[]; valor: number; aoEscolher: (id: number) => void;
}) {
  const atual = clubes.find((c) => c.id === valor);
  const [texto, setTexto] = useState("");
  const [aberto, setAberto] = useState(false);
  const [marcado, setMarcado] = useState(0);
  const opcoes = useMemo(() => {
    const busca = semAcento(texto.trim());
    return (busca ? clubes.filter((c) => semAcento(c.nome).includes(busca)) : clubes).slice(0, 8);
  }, [clubes, texto]);

  const escolher = (c: ClubeDoGrafo) => { aoEscolher(c.id); setAberto(false); setTexto(""); };
  const teclar = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "ArrowDown") { e.preventDefault(); setAberto(true); setMarcado((m) => Math.min(m + 1, opcoes.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setMarcado((m) => Math.max(m - 1, 0)); }
    else if (e.key === "Enter" && aberto && opcoes[marcado]) { e.preventDefault(); escolher(opcoes[marcado]); }
    else if (e.key === "Escape") { setAberto(false); setTexto(""); }
  };

  return (
    <label className="escolha-clube">
      <span className="rotulo-pequeno">{rotulo}</span>
      <span className="escolha-clube-campo">
        {atual && !aberto && <MiniEscudo nome={atual.nome} />}
        <input value={aberto ? texto : atual?.nome ?? ""} placeholder="digite o nome do clube"
          role="combobox" aria-expanded={aberto} aria-autocomplete="list"
          onFocus={() => { setAberto(true); setTexto(""); setMarcado(0); }}
          onBlur={() => setTimeout(() => { setAberto(false); setTexto(""); }, 150)}
          onChange={(e) => { setTexto(e.target.value); setMarcado(0); }} onKeyDown={teclar} />
      </span>
      {aberto && (
        <ul className="escolha-clube-lista" role="listbox">
          {opcoes.length === 0 && <li className="vazio">nenhum clube com esse nome</li>}
          {opcoes.map((c, i) => (
            <li key={c.id} role="option" aria-selected={i === marcado}>
              <button type="button" className={i === marcado ? "marcado" : ""} onMouseDown={(e) => e.preventDefault()}
                onMouseEnter={() => setMarcado(i)} onClick={() => escolher(c)}>
                <MiniEscudo nome={c.nome} /> <span>{c.nome}</span> <small>{c.grau} arcos</small>
              </button>
            </li>
          ))}
        </ul>
      )}
    </label>
  );
}

interface Parada { id: number; nome: string; temporadas: string[]; reticencias?: number }

// junta as temporadas seguidas do mesmo clube (arcos de espera do grafo por temporada) numa parada só
function paradasDoCaminho(caminho: NoDaRota[], ciclo: boolean): Parada[] {
  const nos = ciclo ? caminho.slice(0, -1) : caminho;
  const paradas: Parada[] = [];
  for (const no of nos) {
    const ultima = paradas[paradas.length - 1];
    if (ultima && ultima.id === no.id) { if (no.temporada) ultima.temporadas.push(no.temporada); }
    else paradas.push({ id: no.id, nome: no.nome, temporadas: no.temporada ? [no.temporada] : [] });
  }
  return paradas;
}

const MAXIMO_NO_DESENHO = 10;

function DesenhoDaRota({ resumo, caminho, trechos, ciclo, cor, euro }: {
  resumo: ResumoDoGrafoDaParte2; caminho: NoDaRota[] | null; trechos: TrechoDaRota[]; ciclo: boolean; cor: string; euro: (v: number) => string;
}) {
  const [W, H] = [960, 430];
  const todas = caminho ? paradasDoCaminho(caminho, ciclo) : [];
  const pesos = trechos.filter((t) => !t.espera).map((t) => t.peso);
  // caminho muito longo (a DFS chega a centenas de arcos): desenha o começo e o fim, e a lista completa fica embaixo
  const escondidas = Math.max(0, todas.length - MAXIMO_NO_DESENHO);
  const paradas: Parada[] = escondidas
    ? [...todas.slice(0, 4), { id: -1, nome: "", temporadas: [], reticencias: todas.length - 8 }, ...todas.slice(-4)]
    : todas;
  const n = paradas.length;
  // cada parada tem a sua posição (um clube que aparece duas vezes no caminho aparece duas vezes no desenho)
  const xDaParada = (i: number) => (n <= 1 ? W / 2 : 130 + (i * (W - 260)) / (n - 1));
  const yDaParada = () => H / 2 - 10;
  const naParada = paradas.map((_, i) => ({ x: xDaParada(i), y: yDaParada() }));
  const pos = new Map<number, { x: number; y: number }>();
  paradas.forEach((p, i) => { if (!pos.has(p.id)) pos.set(p.id, naParada[i]); });
  const noAnel = resumo.contexto.nos.filter((c) => !pos.has(c.id));
  noAnel.forEach((c, i) => {
    const a = -Math.PI / 2 + (2 * Math.PI * i) / noAnel.length;
    pos.set(c.id, { x: W / 2 + (W / 2 - 46) * Math.cos(a), y: H / 2 + (H / 2 - 34) * Math.sin(a) });
  });
  const arcosDoContexto = resumo.contexto.arcos.filter(([u, v]) => pos.has(u) && pos.has(v));

  const saltos = paradas.slice(0, -1).map((p, i) => ({ de: p, para: paradas[i + 1], a: naParada[i], b: naParada[i + 1], i }));
  if (ciclo && n > 1) saltos.push({ de: paradas[n - 1], para: paradas[0], a: naParada[n - 1], b: naParada[0], i: n - 1 });
  const pesoDoSalto = (i: number) => {
    if (!escondidas) return pesos[i];
    if (i < 3) return pesos[i];
    if (i >= n - 4) return pesos[pesos.length - (n - 1 - i)];
    return undefined;
  };
  const curva = (a: { x: number; y: number }, b: { x: number; y: number }, volta: boolean) => {
    const [mx, my] = [(a.x + b.x) / 2, (a.y + b.y) / 2];
    const [dx, dy] = [b.x - a.x, b.y - a.y];
    const d = Math.hypot(dx, dy) || 1;
    const dobra = volta ? -130 : -24; // as setas do caminho curvam para cima; a que fecha o ciclo volta por baixo
    const [cx, cy] = [mx - (dy / d) * dobra, my + (dx / d) * dobra];
    const r = 22; // termina na borda do círculo do clube
    const [ex, ey] = [b.x - ((b.x - cx) / Math.hypot(b.x - cx, b.y - cy)) * r, b.y - ((b.y - cy) / Math.hypot(b.x - cx, b.y - cy)) * r];
    const fora = volta ? 0.5 * dobra - 16 : 0.5 * dobra - 12; // o valor fica do lado de fora da curva
    return { d: `M${a.x} ${a.y} Q${cx} ${cy} ${ex} ${ey}`, rotulo: { x: mx - (dy / d) * fora, y: my + (dx / d) * fora + 4 } };
  };

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="explorar-desenho" role="img"
      aria-label={paradas.length ? `Caminho: ${todas.map((p) => p.nome).join(", ")}` : "Os clubes com mais transferências"}>
      <defs>
        <marker id="seta-explorar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M0 0 L10 5 L0 10 z" fill={cor} />
        </marker>
      </defs>
      <g className="explorar-contexto">
        {arcosDoContexto.map(([u, v]) => {
          const [a, b] = [pos.get(u)!, pos.get(v)!];
          return <line key={`${u}-${v}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} />;
        })}
      </g>
      {noAnel.map((c) => {
        const p = pos.get(c.id)!;
        const embaixo = p.y > H / 2;
        return (
          <g key={c.id} transform={`translate(${p.x} ${p.y})`} className="explorar-no-contexto">
            <circle r={13} />
            <EscudoDoClube nome={c.nome} tamanho={0.62} />
            <text y={embaixo ? 27 : -19} textAnchor="middle">{c.nome}</text>
          </g>
        );
      })}
      <g key={paradas.map((p) => p.id).join("-")}>
        {saltos.map(({ de, para, a, b, i }) => {
          const volta = ciclo && i === n - 1;
          const { d, rotulo } = curva(a, b, volta);
          const peso = de.reticencias || para.reticencias ? undefined : pesoDoSalto(i);
          return (
            <g key={i}>
              <motion.path d={d} className="explorar-seta" stroke={cor} markerEnd="url(#seta-explorar)"
                strokeDasharray={de.reticencias || para.reticencias ? "5 6" : undefined}
                initial={{ pathLength: 0, opacity: 0 }} animate={{ pathLength: 1, opacity: 1 }}
                transition={{ duration: 0.35, delay: 0.12 * i }} />
              {peso !== undefined && (
                <motion.text x={rotulo.x} y={rotulo.y} textAnchor="middle" className={peso < 0 ? "explorar-peso negativo" : "explorar-peso"}
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.12 * i + 0.25 }}>{euro(peso)}</motion.text>
              )}
            </g>
          );
        })}
        {paradas.map((p, i) => {
          const { x, y } = naParada[i];
          if (p.reticencias) {
            return (
              <g key="reticencias" transform={`translate(${x} ${y})`} className="explorar-reticencias">
                <circle r={20} />
                <text y={5} textAnchor="middle">…</text>
                <text y={38 + (i % 2 === 0 ? 0 : 30)} textAnchor="middle" className="explorar-temporada">+{p.reticencias} clubes</text>
              </g>
            );
          }
          const papel = ciclo ? (i === 0 ? "início do ciclo" : "") : i === 0 ? "origem" : i === n - 1 ? "destino" : "";
          const temporadas = p.temporadas.length > 1 ? `${p.temporadas[0]} a ${p.temporadas[p.temporadas.length - 1]}` : p.temporadas[0];
          const linha = i % 2 === 0 ? 0 : 30; // nomes em duas linhas alternadas para não encostarem
          return (
            <g key={`${p.id}-${i}`} transform={`translate(${x} ${y})`}>
            <motion.g className="explorar-parada"
              initial={{ opacity: 0, scale: 0.6 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.12 * i }}>
              <circle r={21} stroke={cor} />
              <EscudoDoClube nome={p.nome} tamanho={1.05} />
              {papel && <text y={-30} textAnchor="middle" className="explorar-papel">{papel}</text>}
              {linha > 0 && <line y1={22} y2={24 + linha} className="explorar-guia" />}
              <text y={38 + linha} textAnchor="middle" className="explorar-nome">{p.nome}</text>
              {temporadas && <text y={51 + linha} textAnchor="middle" className="explorar-temporada">{temporadas}</text>}
            </motion.g>
            </g>
          );
        })}
      </g>
    </svg>
  );
}

export function ExplorarGrafo({ cores, nomes, euro, detalhes }: {
  cores: Record<string, string>; nomes: Record<string, string>; euro: (v: number) => string;
  detalhes: (caminho: NoDaRota[], trechos: TrechoDaRota[], ciclo: boolean) => ReactNode;
}) {
  const [resumo, setResumo] = useState<ResumoDoGrafoDaParte2 | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [grafo, setGrafo] = useState<GrafoDaParte2>("clubes");
  const [alg, setAlg] = useState<AlgoritmoDaParte2>("BFS");
  const [origem, setOrigem] = useState(0);
  const [destino, setDestino] = useState(0);
  const [temporada, setTemporada] = useState(0);
  const [rota, setRota] = useState<RotaDaParte2 | null>(null);
  const [calculando, setCalculando] = useState(false);
  const pedido = useRef(0);

  const porId = useMemo(() => new Map((resumo?.clubes ?? []).map((c) => [c.id, c])), [resumo]);
  const temporadas = porId.get(origem)?.temporadas ?? [];

  const calcular = (g = grafo, a = alg, o = origem, d = destino, t = temporada) => {
    const meu = ++pedido.current;
    setCalculando(true);
    setErro(null);
    calcularRota(g, a, o, d, t)
      .then((r) => { if (meu === pedido.current) setRota(r); })
      .catch((e: Error) => { if (meu === pedido.current) { setErro(e.message); setRota(null); } })
      .finally(() => { if (meu === pedido.current) setCalculando(false); });
  };

  useEffect(() => {
    carregarGrafoDaParte2().then((r) => {
      setResumo(r);
      const p = r.padrao.clubes;
      setOrigem(p.origem); setDestino(p.destino); setTemporada(r.padrao.temporal.temporada);
      calcular("clubes", "BFS", p.origem, p.destino);
    }).catch((e: Error) => setErro(e.message));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // na troca de clube de origem, fica na temporada mais próxima que esse clube tem no grafo
  useEffect(() => {
    if (temporadas.length && !temporadas.includes(temporada)) {
      setTemporada(temporadas.reduce((m, s) => (Math.abs(s - temporada) < Math.abs(m - temporada) ? s : m), temporadas[0]));
    }
  }, [origem, temporadas, temporada]);

  const trocarGrafo = (g: GrafoDaParte2) => {
    setGrafo(g);
    if (g === "temporal" && resumo && origem === resumo.padrao.clubes.origem && destino === resumo.padrao.clubes.destino) {
      const p = resumo.padrao.temporal; // o exemplo do relatório: Benfica 15/16 até o Bournemouth
      setOrigem(p.origem); setDestino(p.destino); setTemporada(p.temporada);
    }
  };

  if (!resumo) {
    return (
      <section className="cartao explorar">
        <h3 className="cartao-titulo">Explorar o grafo</h3>
        {erro ? <p className="detalhe">{erro}</p> : <Carregando texto="Carregando o dataset da Parte 2 (uns 10 a 15 segundos na primeira vez)…" />}
      </section>
    );
  }

  const cor = cores[alg];
  const bfLento = grafo === "clubes" && alg === "BELLMAN_FORD";
  const ciclo = rota?.status === "CICLO_NEGATIVO";
  const caminho = ciclo ? rota?.ciclo?.caminho ?? null : rota?.caminho ?? null;
  const trechos = (ciclo ? rota?.ciclo?.trechos : rota?.trechos) ?? [];
  const custo = ciclo ? rota?.ciclo?.custo : rota?.custo;
  const mesmaConsulta = rota && rota.grafo === grafo && rota.algoritmo === alg;

  return (
    <section className="cartao explorar" style={{ "--cor": cor } as CSSProperties}>
      <div className="cartao-cabeca">
        <h3 className="cartao-titulo">Explorar o grafo</h3>
        <span className="detalhe">escolha o grafo, a origem, o destino e o algoritmo</span>
      </div>

      <div className="explorar-controles">
        <div className="explorar-grupo">
          <span className="rotulo-pequeno">grafo</span>
          <div className="chips" style={{ "--cor": "var(--destaque)" } as CSSProperties}>
            {(["clubes", "temporal"] as GrafoDaParte2[]).map((g) => (
              <button key={g} type="button" className={g === grafo ? "chip ativo" : "chip"} onClick={() => trocarGrafo(g)}>{NOME_DO_GRAFO[g]}</button>
            ))}
          </div>
        </div>
        <EscolhaDeClube rotulo="origem" clubes={resumo.clubes} valor={origem} aoEscolher={setOrigem} />
        {grafo === "temporal" && (
          <label className="explorar-grupo">
            <span className="rotulo-pequeno">sai na temporada</span>
            <select value={temporada} onChange={(e) => setTemporada(Number(e.target.value))}>
              {temporadas.map((s) => <option key={s} value={s}>{temporadaCurta(s)}</option>)}
            </select>
          </label>
        )}
        <EscolhaDeClube rotulo="destino" clubes={resumo.clubes} valor={destino} aoEscolher={setDestino} />
        <div className="explorar-grupo">
          <span className="rotulo-pequeno">algoritmo</span>
          <div className="chips">
            {ALGORITMOS.map((a) => (
              <button key={a} type="button" className={a === alg ? "chip ativo" : "chip"} style={{ "--cor": cores[a] } as CSSProperties}
                onClick={() => setAlg(a)} title={O_QUE_ACHA[a]}>{nomes[a]}</button>
            ))}
          </div>
        </div>
        <button type="button" className="botao-envio explorar-rodar" onClick={() => calcular()} disabled={calculando}>
          <Play size={16} aria-hidden /> {calculando ? "calculando…" : "rodar"}
        </button>
      </div>
      <p className="detalhe explorar-dica">
        <b>{nomes[alg]}:</b> {O_QUE_ACHA[alg]}.
        {grafo === "temporal" &&
          " No grafo por temporada, a chegada pode acontecer em qualquer temporada. BFS e DFS seguem suas próprias ordens de busca, enquanto Dijkstra e Bellman-Ford consideram os custos das conexões."}
        {grafo === "temporal" && alg === "DIJKSTRA" &&
          " Neste grafo, o Dijkstra utiliza a repesagem de Johnson para trabalhar com pesos não negativos."}
        {bfLento &&
          " O grafo de clubes possui ciclos negativos. O Bellman-Ford realiza as passadas necessárias para verificar os custos, o que pode tornar a execução mais demorada."}
      </p>

      {erro && <p className="explorar-erro">{erro}</p>}

      <div className={calculando ? "explorar-quadro calculando" : "explorar-quadro"}>
        <DesenhoDaRota resumo={resumo} caminho={caminho} trechos={trechos} ciclo={ciclo} cor={mesmaConsulta ? cor : cores[rota?.algoritmo ?? alg]} euro={euro} />
        {calculando && <div className="explorar-carregando"><Carregando texto={bfLento ? "Bellman-Ford rodando no grafo de clubes…" : "calculando…"} /></div>}
      </div>
      <span className="detalhe">
        Os {resumo.contexto.nos.length} clubes com mais conexões
        aparecem em cinza, mostrando o contexto da rede.
        As setas coloridas representam o resultado do algoritmo,
        e os números indicam o peso de cada conexão
        (valor pago menos valor de mercado).
      </span>

      {rota && (
        <div className="explorar-resultado">
          <span className={`etiqueta status-${rota.status === "OK" ? "ok" : rota.status === "CICLO_NEGATIVO" ? "ciclo_negativo" : "sem_solucao"}`}>
            {nomes[rota.algoritmo]} · {NOME_DO_GRAFO[rota.grafo]} · {STATUS[rota.status]}
          </span>
          <dl className="explorar-numeros">
            {custo !== undefined && <div><dt>{ciclo ? "custo de uma volta" : "custo do caminho"}</dt><dd className={custo < 0 ? "negativo" : ""}>{euro(custo)}</dd></div>}
            {(ciclo ? rota.ciclo?.arcos : rota.arcos) !== undefined && <div><dt>arcos</dt><dd>{ciclo ? rota.ciclo?.arcos : rota.arcos}</dd></div>}
            {rota.grafo === "temporal" && rota.transferencias_no_caminho !== undefined && <div><dt>transferências</dt><dd>{rota.transferencias_no_caminho}</dd></div>}
            <div><dt>nós alcançados</dt><dd>{rota.alcancados.toLocaleString("pt-BR")}</dd></div>
            <div><dt>tempo</dt><dd>{rota.segundos.toLocaleString("pt-BR")} s{rota.guardado && <small> (já calculado antes, veio da memória)</small>}</dd></div>
          </dl>
          {rota.status === "SEM_CAMINHO" && (
            <p className="detalhe">
              Não foi encontrado um caminho que ligue o clube de origem ao destino neste grafo.
            </p>
          )}
          {ciclo && (
            <p className="detalhe">
              O Bellman-Ford encontrou um ciclo negativo que pode ser alcançado a partir da origem. Como repetir esse ciclo pode diminuir o custo continuamente, o algoritmo apresenta o ciclo encontrado em vez de um caminho de menor custo.
            </p>
          )}
          {rota.custo_deslocado !== undefined && (
            <p className="detalhe">
              Para conseguir executar o Dijkstra, os pesos foram ajustados em +{euro(resumo.deslocamento)} por arco, evitando valores negativos. O custo apresentado no resultado continua sendo o valor original, sem esse ajuste.
            </p>
          )}
          {caminho && detalhes(caminho, trechos, ciclo)}
        </div>
      )}
    </section>
  );
}
