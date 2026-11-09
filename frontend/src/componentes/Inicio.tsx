// [IA] Claude Code (Claude Opus 5.5) – tela inicial: escolha entre a Parte 1 (labirinto) e a Parte 2 (rede de transferências)
import { ArrowRight } from "lucide-react";
import { motion } from "motion/react";

const LABIRINTO = [
  "###########",
  "#S..#.....#",
  "#.#.#.###.#",
  "#.#...#...#",
  "#.#####.#.#",
  "#.....#.#G#",
  "###########",
];

const NOS: [number, number][] = [[20, 30], [62, 18], [104, 34], [38, 70], [84, 66], [128, 76], [56, 108], [112, 112], [150, 40]];
const ARCOS: [number, number][] = [[0, 1], [1, 2], [0, 3], [3, 4], [4, 2], [4, 5], [3, 6], [6, 7], [7, 5], [2, 8], [5, 8], [1, 4]];

function DesenhoLabirinto() {
  return (
    <svg viewBox="0 0 11 7" className="desenho" aria-hidden>
      {LABIRINTO.flatMap((linha, l) => [...linha].map((casa, c) => (
        <rect key={`${l}-${c}`} x={c} y={l} width={1.02} height={1.02} fill={casa === "#" ? "#1c1c1a" : "#fff"} />
      )))}
      <motion.polyline points="1.5,1.5 3.5,1.5 3.5,3.5 5.5,3.5 5.5,1.5 9.5,1.5 9.5,5.5" fill="none" stroke="#ff5a00" strokeWidth={0.28}
        strokeLinecap="round" strokeLinejoin="round" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
        transition={{ duration: 2.6, ease: "easeInOut", repeat: Infinity, repeatDelay: 1.2 }} />
      <circle cx={1.5} cy={1.5} r={0.28} fill="#1c1c1a" />
      <circle cx={9.5} cy={5.5} r={0.26} fill="#fff" stroke="#1c1c1a" strokeWidth={0.09} />
    </svg>
  );
}

function DesenhoRede() {
  return (
    <svg viewBox="0 0 170 130" className="desenho" aria-hidden>
      {ARCOS.map(([a, b], i) => (
        <motion.line key={i} x1={NOS[a][0]} y1={NOS[a][1]} x2={NOS[b][0]} y2={NOS[b][1]} stroke={i % 3 === 0 ? "#ff5a00" : "#c9bba8"}
          strokeWidth={i % 3 === 0 ? 2.4 : 1.6} initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
          transition={{ duration: 0.9, delay: 0.12 * i, repeat: Infinity, repeatType: "reverse", repeatDelay: 2.4 }} />
      ))}
      {NOS.map(([x, y], i) => (
        <motion.circle key={i} cx={x} cy={y} r={i === 4 ? 9 : 6} fill={i === 4 ? "#1c1c1a" : "#fff"} stroke="#1c1c1a" strokeWidth={2}
          initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.06 * i, type: "spring", stiffness: 300, damping: 18 }}
          style={{ transformBox: "fill-box", transformOrigin: "center" }} />
      ))}
    </svg>
  );
}

export function Inicio({ aoEscolher }: { aoEscolher: (parte: "parte1" | "parte2") => void }) {
  const cartoes = [
    {
      id: "parte1" as const, rotulo: "Parte 1", titulo: "Labirinto com chaves",
      texto: "O labirinto vira um grafo de estados: posição, chaves e bônus usados. BFS, DFS, Dijkstra e Bellman-Ford rodando nos mapas do enunciado, do grupo e no mapa surpresa.",
      Desenho: DesenhoLabirinto,
    },
    {
      id: "parte2" as const, rotulo: "Parte 2", titulo: "Rede de transferências",
      texto: "Clubes do Transfermarkt ligados pelas transferências de jogadores, com peso igual ao valor pago menos o valor de mercado. Caminhos, ciclos negativos, desempenho e as visualizações de AVD.",
      Desenho: DesenhoRede,
    },
  ];
  return (
    <main className="inicio">
      <motion.div className="inicio-cabecalho" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <span className="rotulo-pequeno">Projeto final de Teoria dos Grafos e AVD · CESAR School · 2026.2</span>
        <h1>Grupo 2</h1>
        <p>Escolha a parte do projeto que você quer abrir.</p>
      </motion.div>
      <div className="inicio-cartoes">
        {cartoes.map(({ id, rotulo, titulo, texto, Desenho }, i) => (
          <motion.button key={id} type="button" className="inicio-cartao" onClick={() => aoEscolher(id)}
            initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 + i * 0.12 }}
            whileHover={{ y: -6 }} whileTap={{ scale: 0.98 }}>
            <div className="inicio-desenho"><Desenho /></div>
            <span className="rotulo-pequeno">{rotulo}</span>
            <h2>{titulo}</h2>
            <p>{texto}</p>
            <span className="inicio-abrir">Abrir <ArrowRight size={18} aria-hidden /></span>
          </motion.button>
        ))}
      </div>
    </main>
  );
}
