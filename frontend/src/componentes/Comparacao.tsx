// [IA] Claude Code (Claude Opus 5.5) – comparação lado a lado (bônus): dois percursos na mesma linha do tempo, sobrepostos ou lado a lado, com a curva de custo
import { Columns2, GitCompareArrows, Layers2 } from "lucide-react";
import { motion } from "motion/react";
import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { ALGORITMOS, NOME_DO_ALGORITMO, NOME_DO_STATUS, passosDoResultado, resumoDaComparacao } from "../modelo";
import type { Algoritmo, DadosDoMapa, ResumoDoMapa } from "../tipos";
import { usarReproducao } from "../usarReproducao";
import { Controles } from "./Controles";
import { GraficoCusto } from "./GraficoCusto";
import { Tabuleiro } from "./Tabuleiro";

interface Lado {
  mapa: string;
  algoritmo: Algoritmo;
  fonte: boolean;
}

const COR = { A: "#2563eb", B: "#ea580c" };

const EXEMPLOS: { titulo: string; a: [string, Algoritmo, boolean]; b: [string, Algoritmo, boolean] }[] = [
  { titulo: "m01 · menos passos × menor custo", a: ["m01", "BFS", false], b: ["m01", "DIJKSTRA", false] },
  { titulo: "m03 · três chaves", a: ["m03", "BFS", false], b: ["m03", "DIJKSTRA", false] },
  { titulo: "m05 · o desvio pelos bônus", a: ["m05", "BFS", false], b: ["m05", "BELLMAN_FORD", false] },
  { titulo: "m05 · peso negativo", a: ["m05", "DIJKSTRA", false], b: ["m05", "BELLMAN_FORD", false] },
  { titulo: "m06 · fonte infinita × consumível", a: ["m06", "BELLMAN_FORD", false], b: ["m06", "BELLMAN_FORD", true] },
  { titulo: "m02 × m07 · com e sem solução", a: ["m02", "BFS", false], b: ["m07", "BFS", false] },
  { titulo: "m08 · mapa grande", a: ["m08", "BFS", false], b: ["m08", "DIJKSTRA", false] },
];

function descrever(lado: Lado, mapas: ResumoDoMapa[]) {
  const mapa = mapas.find((m) => m.id === lado.mapa)?.titulo.split(" · ")[0] ?? lado.mapa;
  return `${NOME_DO_ALGORITMO[lado.algoritmo]}${lado.fonte ? " (fonte consumível)" : ""} no ${mapa}`;
}

function ConfiguracaoDoLado({ nome, lado, setLado, mapas, dados }: {
  nome: "A" | "B"; lado: Lado; setLado: (l: Lado) => void; mapas: ResumoDoMapa[]; dados: DadosDoMapa | null;
}) {
  const r = dados?.algoritmos[lado.algoritmo];
  return (
    <div className="lado-config" style={{ "--cor": COR[nome] } as CSSProperties}>
      <span className="lado-nome">lado {nome}</span>
      <select value={lado.mapa} onChange={(ev) => setLado({ ...lado, mapa: ev.target.value })} aria-label={`Mapa do lado ${nome}`}>
        {mapas.map((m) => <option key={m.id} value={m.id}>{m.titulo}</option>)}
      </select>
      <div className="segmentado pequeno" role="radiogroup" aria-label={`Algoritmo do lado ${nome}`}>
        {ALGORITMOS.map((a) => (
          <button key={a} type="button" role="radio" aria-checked={lado.algoritmo === a}
            className={lado.algoritmo === a ? "ativo" : ""} onClick={() => setLado({ ...lado, algoritmo: a })}>
            {lado.algoritmo === a && <motion.span layoutId={`alg-lado-${nome}`} className="segmentado-fundo" />}
            <span>{NOME_DO_ALGORITMO[a]}</span>
          </button>
        ))}
      </div>
      <label className="interruptor pequeno">
        <input type="checkbox" checked={lado.fonte} onChange={(ev) => setLado({ ...lado, fonte: ev.target.checked })} />
        <span className="interruptor-trilho" aria-hidden />
        <span>fonte consumível</span>
      </label>
      {r && (
        <span className={`etiqueta status-${r.status.toLowerCase()}`}>
          {NOME_DO_STATUS[r.status]}{r.status === "OK" ? ` · ${r.passos} passos · custo ${r.custo}` : ""}
        </span>
      )}
    </div>
  );
}

export function Comparacao({ mapas, mapaInicial, obterDados }: {
  mapas: ResumoDoMapa[]; mapaInicial: string; obterDados: (id: string, fonte: boolean) => Promise<DadosDoMapa>;
}) {
  const [a, setA] = useState<Lado>({ mapa: mapaInicial, algoritmo: "BFS", fonte: false });
  const [b, setB] = useState<Lado>({ mapa: mapaInicial, algoritmo: "DIJKSTRA", fonte: false });
  const [dadosA, setDadosA] = useState<DadosDoMapa | null>(null);
  const [dadosB, setDadosB] = useState<DadosDoMapa | null>(null);
  const [visual, setVisual] = useState<"sobrepor" | "lado">("sobrepor");

  useEffect(() => {
    let vivo = true;
    obterDados(a.mapa, a.fonte).then((d) => vivo && setDadosA(d)).catch(() => vivo && setDadosA(null));
    return () => { vivo = false; };
  }, [a.mapa, a.fonte, obterDados]);
  useEffect(() => {
    let vivo = true;
    obterDados(b.mapa, b.fonte).then((d) => vivo && setDadosB(d)).catch(() => vivo && setDadosB(null));
    return () => { vivo = false; };
  }, [b.mapa, b.fonte, obterDados]);

  const prontos = dadosA && dadosB && dadosA.id === a.mapa && dadosB.id === b.mapa
    && dadosA.fonte_consumivel === a.fonte && dadosB.fonte_consumivel === b.fonte;
  const resA = prontos ? dadosA.algoritmos[a.algoritmo] : null;
  const resB = prontos ? dadosB.algoritmos[b.algoritmo] : null;
  const passosA = useMemo(() => (prontos && resA ? passosDoResultado(dadosA, resA) : []), [prontos, dadosA, resA]);
  const passosB = useMemo(() => (prontos && resB ? passosDoResultado(dadosB, resB) : []), [prontos, dadosB, resB]);
  const ultimo = Math.max(0, passosA.length - 1, passosB.length - 1);
  const reproducao = usarReproducao(ultimo, JSON.stringify([a, b]));
  const duracao = Math.min(0.35, 0.85 / reproducao.velocidade);
  const mesmoMapa = a.mapa === b.mapa;
  const sobrepor = visual === "sobrepor" && mesmoMapa && prontos;

  function aplicarExemplo(e: (typeof EXEMPLOS)[number]) {
    const achar = (codigo: string) => mapas.find((m) => m.id.startsWith(`${codigo}_`))?.id ?? mapaInicial;
    setA({ mapa: achar(e.a[0]), algoritmo: e.a[1], fonte: e.a[2] });
    setB({ mapa: achar(e.b[0]), algoritmo: e.b[1], fonte: e.b[2] });
    setVisual(e.a[0] === e.b[0] ? "sobrepor" : "lado");
  }

  return (
    <div className="comparacao">
      <div className="exemplos">
        <span className="rotulo-pequeno"><GitCompareArrows size={14} aria-hidden /> exemplos prontos</span>
        <div className="chips">
          {EXEMPLOS.map((e) => <button key={e.titulo} type="button" className="chip" onClick={() => aplicarExemplo(e)}>{e.titulo}</button>)}
        </div>
      </div>

      <div className="lados">
        <ConfiguracaoDoLado nome="A" lado={a} setLado={setA} mapas={mapas} dados={prontos ? dadosA : null} />
        <ConfiguracaoDoLado nome="B" lado={b} setLado={setB} mapas={mapas} dados={prontos ? dadosB : null} />
      </div>

      <div className="segmentado" role="radiogroup" aria-label="Como mostrar">
        {([["sobrepor", "Sobrepor", Layers2], ["lado", "Lado a lado", Columns2]] as const).map(([valor, nome, Icone]) => (
          <button key={valor} type="button" role="radio" aria-checked={visual === valor} disabled={valor === "sobrepor" && !mesmoMapa}
            className={visual === valor ? "ativo" : ""} onClick={() => setVisual(valor)}>
            {visual === valor && <motion.span layoutId="visual-ativo" className="segmentado-fundo" />}
            <Icone size={16} aria-hidden />
            <span>{nome}{valor === "sobrepor" && !mesmoMapa ? " (só no mesmo mapa)" : ""}</span>
          </button>
        ))}
      </div>

      {!prontos || !resA || !resB ? (
        <div className="carregando">Calculando os dois lados…</div>
      ) : (
        <>
          {sobrepor ? (
            <div className="quadro">
              <Tabuleiro dados={dadosA} resultado={resA} passos={passosA} passo={Math.min(reproducao.passo, passosA.length - 1)}
                duracao={duracao} camadaFixa={null} mostrarArmadilhas={false} corDoJogador={COR.A}
                fantasma={resB.status === "OK" ? { passos: passosB, passo: reproducao.passo, cor: COR.B } : undefined} />
            </div>
          ) : (
            <div className="dois-quadros">
              {([["A", dadosA, resA, passosA], ["B", dadosB, resB, passosB]] as const).map(([nome, d, r, p]) => (
                <div key={nome} className="quadro" style={{ "--cor": COR[nome] } as CSSProperties}>
                  <span className="quadro-rotulo">lado {nome}</span>
                  <Tabuleiro dados={d} resultado={r} passos={p} passo={Math.min(reproducao.passo, p.length - 1)} duracao={duracao}
                    camadaFixa={null} mostrarArmadilhas={r.status === "SEM_SOLUCAO"} corDoJogador={COR[nome]} compacto />
                </div>
              ))}
            </div>
          )}

          <Controles reproducao={reproducao} ultimo={ultimo} cor={COR.A} />

          <div className="comparacao-baixo">
            <div className="cartao">
              <span className="rotulo-pequeno">custo acumulado por passo</span>
              <GraficoCusto passo={reproducao.passo} altura={190} series={[
                { nome: "A", cor: COR.A, custos: resA.custos ?? [] },
                { nome: "B", cor: COR.B, custos: resB.custos ?? [] },
              ]} />
              <div className="legenda-linhas">
                <span><i className="ponto" style={{ background: COR.A }} />A · {descrever(a, mapas)}</span>
                <span><i className="ponto" style={{ background: COR.B }} />B · {descrever(b, mapas)}</span>
              </div>
            </div>
            <motion.div key={JSON.stringify([a, b])} className="cartao resumo-comparacao" initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}>
              <span className="rotulo-pequeno">o que muda</span>
              <p>{resumoDaComparacao({ nome: "A", resultado: resA }, { nome: "B", resultado: resB })}</p>
              <table className="tabela-algoritmos">
                <thead><tr><th scope="col">lado</th><th scope="col">passos</th><th scope="col">custo</th></tr></thead>
                <tbody>
                  <tr><th scope="row" style={{ color: COR.A }}>A</th><td className="numero">{resA.passos ?? "—"}</td><td className="numero">{resA.custo ?? "—"}</td></tr>
                  <tr><th scope="row" style={{ color: COR.B }}>B</th><td className="numero">{resB.passos ?? "—"}</td><td className="numero">{resB.custo ?? "—"}</td></tr>
                </tbody>
              </table>
            </motion.div>
          </div>
        </>
      )}
    </div>
  );
}
