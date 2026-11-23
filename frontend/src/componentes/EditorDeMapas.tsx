// [IA] Claude Code (Claude Opus 5.5) – editor de mapas: desenhar a grade clicando, conferir S e G, baixar o .txt e testar no labirinto
import { Download, Eraser, Frame, Play } from "lucide-react";
import { useEffect, useMemo, useRef, useState, type PointerEvent } from "react";
import { CORES_CHAVE } from "../modelo";
import type { ResumoDoMapa } from "../tipos";

const PALETA: { titulo: string; simbolos: [string, string][] }[] = [
  { titulo: "terreno", simbolos: [[".", "chão (+1)"], ["#", "parede"], [",", "lama (+3)"], ["~", "água (+5)"]] },
  { titulo: "início e saída", simbolos: [["S", "início"], ["G", "saída"]] },
  { titulo: "itens", simbolos: [["+", "bônus (−4 na 1ª vez)"], ["*", "fonte (−2)"]] },
  { titulo: "chaves", simbolos: [["a", "chave a"], ["b", "chave b"], ["c", "chave c"], ["d", "chave d"]] },
  { titulo: "portas", simbolos: [["A", "porta A"], ["B", "porta B"], ["C", "porta C"], ["D", "porta D"]] },
  { titulo: "esteiras", simbolos: [[">", "esteira →"], ["<", "esteira ←"], ["^", "esteira ↑"], ["v", "esteira ↓"]] },
];

const SETA: Record<string, string> = { ">": "→", "<": "←", "^": "↑", v: "↓" };
const MIN = 3;
const MAX_LINHAS = 31;
const MAX_COLUNAS = 71;

function gradeInicial(linhas = 9, colunas = 15) {
  return Array.from({ length: linhas }, (_, l) => Array.from({ length: colunas }, (_, c) => {
    if (l === 0 || c === 0 || l === linhas - 1 || c === colunas - 1) return "#";
    if (l === 1 && c === 1) return "S";
    if (l === linhas - 2 && c === colunas - 2) return "G";
    return ".";
  }));
}

function Celula({ simbolo, l, c }: { simbolo: string; l: number; c: number }) {
  const fundo = simbolo === "#" ? "var(--parede)" : simbolo === "," ? "#ecd3b3" : simbolo === "~" ? "#cfe3f7" : "#fff";
  const chave = simbolo.toLowerCase();
  return (
    <g transform={`translate(${c} ${l})`}>
      <rect width={1} height={1} fill={fundo} stroke="rgba(13,42,28,0.12)" strokeWidth={0.02} />
      {simbolo === "S" && <circle cx={0.5} cy={0.5} r={0.26} fill="var(--parede)" />}
      {simbolo === "G" && <circle cx={0.5} cy={0.5} r={0.26} fill="none" stroke="var(--parede)" strokeWidth={0.1} />}
      {simbolo === "+" && <rect x={0.3} y={0.3} width={0.4} height={0.4} fill="#1baf7a" transform="rotate(45 0.5 0.5)" />}
      {simbolo === "*" && <text x={0.5} y={0.72} textAnchor="middle" className="editor-glifo" fill="#1d7f8c">★</text>}
      {/^[a-d]$/.test(simbolo) && (
        <>
          <circle cx={0.38} cy={0.5} r={0.17} fill="none" stroke={CORES_CHAVE[chave]} strokeWidth={0.09} />
          <path d="M0.55 0.5 H0.85 M0.75 0.5 V0.64" stroke={CORES_CHAVE[chave]} strokeWidth={0.09} />
        </>
      )}
      {/^[A-D]$/.test(simbolo) && (
        <>
          <rect x={0.08} y={0.08} width={0.84} height={0.84} fill={CORES_CHAVE[chave]} />
          <text x={0.5} y={0.68} textAnchor="middle" className="editor-glifo" fill="#fff">{simbolo}</text>
        </>
      )}
      {SETA[simbolo] && <text x={0.5} y={0.7} textAnchor="middle" className="editor-glifo" fill="#43524a">{SETA[simbolo]}</text>}
    </g>
  );
}

export function EditorDeMapas({ mapas, aoTestar, testando }: {
  mapas: ResumoDoMapa[]; aoTestar: (texto: string, nome: string) => void; testando: boolean;
}) {
  const [grade, setGrade] = useState<string[][]>(() => gradeInicial());
  const [pincel, setPincel] = useState("#");
  const [nome, setNome] = useState("meu_mapa");
  const pintando = useRef(false);
  const linhas = grade.length;
  const colunas = grade[0].length;

  useEffect(() => {
    const soltar = () => { pintando.current = false; };
    window.addEventListener("pointerup", soltar);
    return () => window.removeEventListener("pointerup", soltar);
  }, []);

  const texto = useMemo(() => grade.map((linha) => linha.join("")).join("\n") + "\n", [grade]);
  const contagem = useMemo(() => {
    const todos = grade.flat();
    return { S: todos.filter((s) => s === "S").length, G: todos.filter((s) => s === "G").length };
  }, [grade]);
  const avisos = [
    contagem.S !== 1 && `o mapa precisa de exatamente um início S (tem ${contagem.S})`,
    contagem.G < 1 && "o mapa precisa de pelo menos uma saída G",
  ].filter(Boolean) as string[];

  function pintar(l: number, c: number) {
    setGrade((g) => {
      if (g[l][c] === pincel) return g;
      const nova = g.map((linha) => [...linha]);
      if (pincel === "S") nova.forEach((linha, i) => linha.forEach((s, j) => { if (s === "S") nova[i][j] = "."; }));
      nova[l][c] = pincel;
      return nova;
    });
  }

  function celulaDoPonteiro(ev: PointerEvent<SVGSVGElement>) {
    const caixa = ev.currentTarget.getBoundingClientRect();
    const c = Math.floor(((ev.clientX - caixa.left) / caixa.width) * colunas);
    const l = Math.floor(((ev.clientY - caixa.top) / caixa.height) * linhas);
    return l >= 0 && l < linhas && c >= 0 && c < colunas ? [l, c] as const : null;
  }

  function redimensionar(novasLinhas: number, novasColunas: number) {
    const nl = Math.max(MIN, Math.min(MAX_LINHAS, novasLinhas || MIN));
    const nc = Math.max(MIN, Math.min(MAX_COLUNAS, novasColunas || MIN));
    setGrade((g) => Array.from({ length: nl }, (_, l) => Array.from({ length: nc }, (_, c) => g[l]?.[c] ?? ".")));
  }

  function moldura() {
    setGrade((g) => g.map((linha, l) => linha.map((s, c) => (l === 0 || c === 0 || l === g.length - 1 || c === linha.length - 1 ? "#" : s))));
  }

  function carregarBase(id: string) {
    const base = mapas.find((m) => m.id === id);
    if (!base) return;
    setGrade(base.grade.map((linha) => [...linha]));
    setNome(`${id}_editado`);
  }

  function baixar() {
    const url = URL.createObjectURL(new Blob([texto], { type: "text/plain" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = `${nome || "meu_mapa"}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="editor">
      <div className="editor-barra">
        <label>nome <input value={nome} onChange={(ev) => setNome(ev.target.value.replace(/[^\w-]+/g, "_"))} /></label>
        <label>linhas <input type="number" min={MIN} max={MAX_LINHAS} value={linhas} onChange={(ev) => redimensionar(Number(ev.target.value), colunas)} /></label>
        <label>colunas <input type="number" min={MIN} max={MAX_COLUNAS} value={colunas} onChange={(ev) => redimensionar(linhas, Number(ev.target.value))} /></label>
        <label>começar de
          <select value="" onChange={(ev) => carregarBase(ev.target.value)}>
            <option value="">um mapa existente…</option>
            {mapas.map((m) => <option key={m.id} value={m.id}>{m.titulo}</option>)}
          </select>
        </label>
        <button type="button" className="chip" onClick={moldura}><Frame size={14} aria-hidden /> moldura de parede</button>
        <button type="button" className="chip" onClick={() => setGrade(gradeInicial(linhas, colunas))}><Eraser size={14} aria-hidden /> limpar</button>
      </div>

      <div className="editor-corpo">
        <div className="editor-paleta" role="radiogroup" aria-label="Símbolo para desenhar">
          {PALETA.map((grupo) => (
            <div key={grupo.titulo}>
              <span className="rotulo-pequeno">{grupo.titulo}</span>
              <div className="editor-simbolos">
                {grupo.simbolos.map(([s, rotulo]) => (
                  <button key={s} type="button" role="radio" aria-checked={pincel === s} title={rotulo}
                    className={pincel === s ? "editor-simbolo ativo" : "editor-simbolo"} onClick={() => setPincel(s)}>
                    <svg viewBox="0 0 1 1" aria-hidden><Celula simbolo={s} l={0} c={0} /></svg>
                    <span>{rotulo}</span>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="editor-quadro">
          <svg viewBox={`0 0 ${colunas} ${linhas}`} className="editor-grade" role="img" aria-label={`Grade de ${linhas} por ${colunas} casas`}
            onPointerDown={(ev) => { const p = celulaDoPonteiro(ev); if (p) { pintando.current = true; pintar(...p); } }}
            onPointerMove={(ev) => { if (!pintando.current) return; const p = celulaDoPonteiro(ev); if (p) pintar(...p); }}>
            {grade.map((linha, l) => linha.map((s, c) => <Celula key={`${l}-${c}`} simbolo={s} l={l} c={c} />))}
          </svg>
          {avisos.length > 0
            ? <p className="editor-aviso">{avisos.join("; ")}.</p>
            : <p className="editor-ok">Pronto para testar: clique e arraste na grade para desenhar.</p>}
          <div className="editor-acoes">
            <button type="button" className="botao-envio" onClick={() => aoTestar(texto, nome || "meu_mapa")} disabled={testando || avisos.length > 0}>
              <Play size={18} aria-hidden /> {testando ? "Analisando…" : "Testar no labirinto"}
            </button>
            <button type="button" className="chip" onClick={baixar}><Download size={14} aria-hidden /> baixar .txt</button>
          </div>
          <details className="editor-texto">
            <summary>ver o .txt</summary>
            <pre>{texto}</pre>
          </details>
        </div>
      </div>
    </div>
  );
}
