// peças em pixel art isométrica, no clima dos hotéis virtuais dos anos 2000: campo em losangos, bonecos de blocos e cabeças para a escalação
import type { CSSProperties } from "react";

const PELES = ["#f1c7a0", "#d9a477", "#a8714a", "#7a4e2d", "#e8b98f"];
const CABELOS = ["#2b1a10", "#5a3518", "#0f0f0f", "#a8652b", "#3b2414"];

export interface Jogador {
  camisa: string;
  pele?: number;
  cabelo?: number;
  calcao?: string;
}

// boneco de pé, 10 × 22 pixels, com a base (pés) em (0, 0)
export function Boneco({ camisa, pele = 0, cabelo = 0, calcao = "#0d2a1c", virado = false }: Jogador & { virado?: boolean }) {
  const p = PELES[pele % PELES.length];
  const c = CABELOS[cabelo % CABELOS.length];
  const px: [number, number, number, number, string][] = [
    [2, 0, 6, 2, c], [1, 1, 1, 3, c],
    [2, 2, 6, 5, p], [7, 3, 1, 1, "#14201a"], [4, 3, 1, 1, "#14201a"], [5, 5, 2, 1, "#c97a5a"],
    [3, 7, 4, 1, p],
    [1, 8, 8, 6, camisa], [0, 9, 1, 4, camisa], [9, 9, 1, 4, camisa], [0, 13, 1, 1, p], [9, 13, 1, 1, p],
    [3, 9, 4, 1, "rgba(255,255,255,0.35)"],
    [2, 14, 6, 3, calcao],
    [2, 17, 2, 3, p], [6, 17, 2, 3, p],
    [2, 18, 2, 1, "#fff"], [6, 18, 2, 1, "#fff"],
    [1, 20, 3, 2, "#14201a"], [6, 20, 3, 2, "#14201a"],
  ];
  return (
    <g transform={`translate(${virado ? 5 : -5} -22) scale(${virado ? -1 : 1} 1)`} shapeRendering="crispEdges">
      {px.map(([x, y, w, h, cor], i) => <rect key={i} x={x} y={y} width={w} height={h} fill={cor} />)}
    </g>
  );
}

// cabeça e ombros, 12 × 12 pixels, para a escalação
export function Rosto({ camisa, pele = 0, cabelo = 0, tamanho = 44 }: Jogador & { tamanho?: number }) {
  const p = PELES[pele % PELES.length];
  const c = CABELOS[cabelo % CABELOS.length];
  return (
    <svg viewBox="0 0 12 12" width={tamanho} height={tamanho} shapeRendering="crispEdges" className="rosto-pixel" aria-hidden>
      <rect x={3} y={0} width={6} height={2} fill={c} />
      <rect x={2} y={1} width={1} height={3} fill={c} />
      <rect x={3} y={2} width={6} height={5} fill={p} />
      <rect x={4} y={3} width={1} height={1} fill="#14201a" />
      <rect x={7} y={3} width={1} height={1} fill="#14201a" />
      <rect x={5} y={5} width={2} height={1} fill="#c97a5a" />
      <rect x={4} y={7} width={4} height={1} fill={p} />
      <rect x={1} y={8} width={10} height={4} fill={camisa} />
      <rect x={4} y={8} width={4} height={1} fill="rgba(255,255,255,0.4)" />
    </svg>
  );
}

const TW = 32;
const TH = 16;

function ponto(i: number, j: number, ox: number, oy: number): [number, number] {
  return [(i - j) * (TW / 2) + ox, (i + j) * (TH / 2) + oy];
}

// campo isométrico: 12 × 8 losangos, listras de grama, linhas, dois gols, bonecos e a bola
export function CampoIsometrico({ jogadores, className }: { jogadores: (Jogador & { i: number; j: number })[]; className?: string }) {
  const [C, L] = [12, 8];
  const ox = L * (TW / 2) + 8;
  const oy = 30;
  const W = (C + L) * (TW / 2) + 16;
  const H = (C + L) * (TH / 2) + oy + 18;
  const pt = (i: number, j: number) => ponto(i, j, ox, oy).join(",");
  const losangos = [];
  for (let i = 0; i < C; i++) {
    for (let j = 0; j < L; j++) {
      losangos.push(
        <polygon key={`${i}-${j}`} points={`${pt(i, j)} ${pt(i + 1, j)} ${pt(i + 1, j + 1)} ${pt(i, j + 1)}`}
          fill={Math.floor(i / 2) % 2 ? "#2f8a4b" : "#38995a"} stroke="rgba(0,0,0,0.07)" strokeWidth={0.6} />,
      );
    }
  }
  const [cx, cy] = ponto(C / 2, L / 2, ox, oy);
  const borda = ponto(0, L, ox, oy);
  const gol = (i: number) => {
    const [ax, ay] = ponto(i, L / 2 - 1, ox, oy);
    const [bx, by] = ponto(i, L / 2 + 1, ox, oy);
    return (
      <g className="iso-gol">
        <polygon points={`${ax},${ay} ${bx},${by} ${bx},${by - 18} ${ax},${ay - 18}`} fill="rgba(255,255,255,0.18)" />
        <path d={`M${ax} ${ay}V${ay - 18}L${bx} ${by - 18}V${by}`} fill="none" stroke="#fff" strokeWidth={2.4} />
      </g>
    );
  };
  const ordenados = [...jogadores].sort((a, b) => a.i + a.j - (b.i + b.j));
  const [bolaX, bolaY] = ponto(C / 2 + 0.5, L / 2 + 0.5, ox, oy);
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className={className} role="img" aria-label="Campo de futebol em pixel art isométrica">
      <polygon points={`${pt(0, 0)} ${pt(C, 0)} ${pt(C, L)} ${pt(0, L)}`} fill="#1f6a37" transform="translate(0 6)" />
      <polygon points={`${pt(0, 0)} ${pt(C, 0)} ${pt(C, L)} ${pt(0, L)}`} fill="#1f6a37" />
      {losangos}
      <g fill="none" stroke="rgba(255,255,255,0.85)" strokeWidth={1.4}>
        <polygon points={`${pt(0.5, 0.5)} ${pt(C - 0.5, 0.5)} ${pt(C - 0.5, L - 0.5)} ${pt(0.5, L - 0.5)}`} />
        <line x1={ponto(C / 2, 0.5, ox, oy)[0]} y1={ponto(C / 2, 0.5, ox, oy)[1]} x2={ponto(C / 2, L - 0.5, ox, oy)[0]} y2={ponto(C / 2, L - 0.5, ox, oy)[1]} />
        <ellipse cx={cx} cy={cy} rx={1.4 * TW * 0.707} ry={1.4 * TH * 0.707} />
        <polygon points={`${pt(0.5, L / 2 - 2)} ${pt(2.5, L / 2 - 2)} ${pt(2.5, L / 2 + 2)} ${pt(0.5, L / 2 + 2)}`} />
        <polygon points={`${pt(C - 0.5, L / 2 - 2)} ${pt(C - 2.5, L / 2 - 2)} ${pt(C - 2.5, L / 2 + 2)} ${pt(C - 0.5, L / 2 + 2)}`} />
      </g>
      {gol(0.5)}
      {gol(C - 0.5)}
      <polygon points={`${borda[0]},${borda[1]} ${pt(C, L)} ${ponto(C, L, ox, oy)[0]},${ponto(C, L, ox, oy)[1] + 6} ${borda[0]},${borda[1] + 6}`} fill="#164f29" />
      <polygon points={`${pt(C, 0)} ${pt(C, L)} ${ponto(C, L, ox, oy)[0]},${ponto(C, L, ox, oy)[1] + 6} ${ponto(C, 0, ox, oy)[0]},${ponto(C, 0, ox, oy)[1] + 6}`} fill="#123f21" />
      {ordenados.map((jg, k) => {
        const [x, y] = ponto(jg.i + 0.5, jg.j + 0.5, ox, oy);
        return (
          <g key={k} transform={`translate(${x} ${y})`}>
            <ellipse cx={0} cy={0} rx={7} ry={3} fill="rgba(0,0,0,0.25)" />
            <g className="boneco-pula" style={{ animationDelay: `${k * 0.35}s` } as CSSProperties}>
              <g transform="scale(1.6)"><Boneco {...jg} virado={jg.i > C / 2} /></g>
            </g>
          </g>
        );
      })}
      <g transform={`translate(${bolaX} ${bolaY})`}>
        <ellipse cx={0} cy={1} rx={4} ry={2} fill="rgba(0,0,0,0.3)" />
        <g className="bola-pixel" shapeRendering="crispEdges">
          <rect x={-3} y={-7} width={6} height={6} fill="#fff" />
          <rect x={-2} y={-8} width={4} height={1} fill="#fff" />
          <rect x={-2} y={-1} width={4} height={1} fill="#fff" />
          <rect x={-1} y={-5} width={2} height={2} fill="#14201a" />
          <rect x={-3} y={-7} width={1} height={1} fill="#14201a" />
          <rect x={2} y={-3} width={1} height={1} fill="#14201a" />
        </g>
      </g>
    </svg>
  );
}
