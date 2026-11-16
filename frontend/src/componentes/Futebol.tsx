// peças de futebol desenhadas em SVG: bola, cartão, bandeirinha de escanteio e linhas do campo
import type { CSSProperties } from "react";

const PENTAGONO = (cx: number, cy: number, r: number, giro = -90) =>
  Array.from({ length: 5 }, (_, k) => {
    const a = ((giro + 72 * k) * Math.PI) / 180;
    return `${(cx + Math.cos(a) * r).toFixed(3)},${(cy + Math.sin(a) * r).toFixed(3)}`;
  }).join(" ");

// Bola dentro de um <svg> qualquer, centrada em (0, 0) com raio r
export function Bola({ r, contorno = "#0d2a1c", giro = 0, espessura, aro }: { r: number; contorno?: string; giro?: number; espessura?: number; aro?: number }) {
  const s = r / 50;
  const linha = espessura ?? 3.2;
  return (
    <g transform={`scale(${s}) rotate(${giro})`}>
      <defs>
        <clipPath id="recorte-bola"><circle r={48} /></clipPath>
      </defs>
      <circle r={48} fill="#fff" />
      <g clipPath="url(#recorte-bola)" fill="#14201a" stroke="#14201a" strokeWidth={linha} strokeLinejoin="round">
        <polygon points={PENTAGONO(0, 0, 15)} />
        {Array.from({ length: 5 }, (_, k) => {
          const a = ((-90 + 72 * k) * Math.PI) / 180;
          const [x1, y1, x2, y2] = [Math.cos(a) * 15, Math.sin(a) * 15, Math.cos(a) * 31, Math.sin(a) * 31];
          const b = ((-90 + 36 + 72 * k) * Math.PI) / 180;
          return (
            <g key={k}>
              <line x1={x1} y1={y1} x2={x2} y2={y2} />
              <polygon points={PENTAGONO(Math.cos(a) * 46, Math.sin(a) * 46, 15, -90 + 72 * k + 180)} />
              <line x1={x2} y1={y2} x2={Math.cos(b) * 52} y2={Math.sin(b) * 52} />
              <line x1={Math.cos(a + (72 * Math.PI) / 180) * 31} y1={Math.sin(a + (72 * Math.PI) / 180) * 31} x2={Math.cos(b) * 52} y2={Math.sin(b) * 52} />
            </g>
          );
        })}
      </g>
      <circle r={48} fill="none" stroke={contorno} strokeWidth={aro ?? linha + 1} />
    </g>
  );
}

export function IconeBola({ tamanho = 20, className, style }: { tamanho?: number; className?: string; style?: CSSProperties }) {
  return (
    <svg viewBox="-52 -52 104 104" width={tamanho} height={tamanho} className={className} style={style} aria-hidden>
      <Bola r={50} />
    </svg>
  );
}

export type CorDoCartao = "amarelo" | "vermelho" | "verde" | "azul";

export function Cartao({ cor, className }: { cor: CorDoCartao; className?: string }) {
  return <span className={`cartao-arbitro cartao-${cor} ${className ?? ""}`} aria-hidden />;
}

export function Bandeirinha({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 32" className={className} aria-hidden>
      <path d="M5 30V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <path d="M6 4h13l-3 5 3 5H6z" fill="var(--amarelo)" />
      <path d="M1 30a10 10 0 0 1 10 0" fill="none" stroke="currentColor" strokeWidth="1.6" opacity="0.5" />
    </svg>
  );
}

export function Carregando({ texto }: { texto: string }) {
  return (
    <div className="carregando">
      <span className="bola-rolando"><IconeBola tamanho={30} /></span>
      {texto}
    </div>
  );
}

// escudo genérico de clube (iniciais numa forma de escudo, cor fixa por nome) e a "jogada": um caminho desenhado como troca de passes num campo
const CORES_DE_CLUBE = ["#2a78d6", "#eb6834", "#1baf7a", "#e87ba4", "#6250d6", "#008300", "#c99700", "#1d7f8c", "#b3261e", "#0d2a1c"];

export function corDoClube(nome: string) {
  let h = 0;
  for (const ch of nome.replace(/\s*\(.*\)$/, "")) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return CORES_DE_CLUBE[h % CORES_DE_CLUBE.length];
}

export function iniciais(nome: string) {
  const palavras = nome.replace(/\s*\(.*\)$/, "").replace(/[.\-]/g, " ").split(/\s+/).filter(Boolean);
  if (palavras.length === 1) return palavras[0].slice(0, 3).toUpperCase();
  return palavras.slice(0, 3).map((p) => p[0]).join("").toUpperCase();
}

const FORMA_DO_ESCUDO = "M0 -13 L11 -9 L11 1 C11 8 5 12 0 14 C-5 12 -11 8 -11 1 L-11 -9 Z";

export function EscudoDoClube({ nome, tamanho = 1 }: { nome: string; tamanho?: number }) {
  const sigla = iniciais(nome);
  return (
    <g transform={`scale(${tamanho})`}>
      <path d={FORMA_DO_ESCUDO} fill={corDoClube(nome)} stroke="#fff" strokeWidth={1.6} />
      <path d="M-11 -3 H11" stroke="rgba(255,255,255,0.35)" strokeWidth={1.2} />
      <text y={4.5} textAnchor="middle" className="escudo-sigla" style={{ fontSize: sigla.length > 2 ? 7.5 : 9 }}>{sigla}</text>
    </g>
  );
}

export function MiniEscudo({ nome }: { nome: string }) {
  return (
    <svg viewBox="-13 -15 26 30" className="mini-escudo" aria-hidden>
      <EscudoDoClube nome={nome} />
    </svg>
  );
}

export function Jogada({ clubes, ciclo }: { clubes: string[]; ciclo?: boolean }) {
  const [W, H] = [420, 150];
  const n = clubes.length;
  const pontos = clubes.map((_, i) => ({
    x: 52 + (i * (W - 104)) / Math.max(1, n - 1),
    y: n <= 2 ? H / 2 : i % 2 === 0 ? 58 : 98,
  }));
  const cor = ciclo ? "var(--ciclo)" : "var(--amarelo)";
  const marcador = ciclo ? "url(#seta-ciclo)" : "url(#seta-passe)";
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="jogada" role="img" aria-label={clubes.join(" para ")}>
      <defs>
        <marker id="seta-passe" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M0 0 L10 5 L0 10 z" fill="var(--amarelo)" />
        </marker>
        <marker id="seta-ciclo" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M0 0 L10 5 L0 10 z" fill="var(--ciclo)" />
        </marker>
      </defs>
      {Array.from({ length: 8 }, (_, i) => (
        <rect key={i} x={(i * W) / 8} y={0} width={W / 8} height={H} fill={i % 2 ? "#18633a" : "#1a6b3c"} />
      ))}
      <g className="jogada-linhas">
        <rect x={8} y={8} width={W - 16} height={H - 16} />
        <line x1={W / 2} y1={8} x2={W / 2} y2={H - 8} />
        <circle cx={W / 2} cy={H / 2} r={24} />
        <rect x={8} y={H / 2 - 34} width={30} height={68} />
        <rect x={W - 38} y={H / 2 - 34} width={30} height={68} />
      </g>
      {pontos.slice(1).map((p, i) => {
        const a = pontos[i];
        const [dx, dy] = [p.x - a.x, p.y - a.y];
        const dist = Math.hypot(dx, dy);
        const [ux, uy] = [dx / dist, dy / dist];
        const [x1, y1, x2, y2] = [a.x + ux * 20, a.y + uy * 20, p.x - ux * 22, p.y - uy * 22];
        const meio = { x: (x1 + x2) / 2 - uy * 14, y: (y1 + y2) / 2 + ux * 14 };
        return (
          <path key={i} d={`M ${x1} ${y1} Q ${meio.x} ${meio.y} ${x2} ${y2}`} fill="none" stroke={cor} strokeWidth={2.4}
            strokeDasharray="6 5" markerEnd={marcador} className="jogada-passe" style={{ animationDelay: `${i * 0.25}s` }} />
        );
      })}
      {pontos.map((p, i) => (
        <g key={i} transform={`translate(${p.x} ${p.y})`}>
          <EscudoDoClube nome={clubes[i]} tamanho={1.35} />
          <text y={i % 2 === 0 || n <= 2 ? -24 : 36} textAnchor="middle" className="jogada-nome">{clubes[i]}</text>
        </g>
      ))}
    </svg>
  );
}
