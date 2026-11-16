// tela inicial: escalação do grupo e escolha entre a Parte 1 (labirinto) e a Parte 2 (rede de transferências)
import { ArrowRight } from "lucide-react";
import { motion } from "motion/react";
import { IconeBola } from "./Futebol";

const LABIRINTO = [
  "###########",
  "#S..#.....#",
  "#.#.#.###.#",
  "#.#...#...#",
  "#.#####.#.#",
  "#.....#.#G#",
  "###########",
];

const ESCALACAO = [
  { numero: "P1", nome: "Gabriel França", funcao: "modelagem e grafo de estados" },
  { numero: "P2", nome: "Luís Eduardo Bérard", funcao: "algoritmos e testes" },
  { numero: "P3", nome: "Guilherme Burle", funcao: "análises da Parte 1" },
  { numero: "P4", nome: "João Victor Uchôa", funcao: "dados e experimentos" },
  { numero: "P5", nome: "Caio Leimig", funcao: "visualização e comunicação" },
];

const NOS: [number, number][] = [[34, 34], [66, 22], [108, 30], [44, 74], [86, 64], [126, 76], [62, 104], [112, 106], [146, 46]];
const ARCOS: [number, number][] = [[0, 1], [1, 2], [0, 3], [3, 4], [4, 2], [4, 5], [3, 6], [6, 7], [7, 5], [2, 8], [5, 8], [1, 4]];

function DesenhoLabirinto() {
  return (
    <svg viewBox="0 0 11 7" className="desenho" aria-hidden preserveAspectRatio="xMidYMid meet">
      {LABIRINTO.flatMap((linha, l) => [...linha].map((casa, c) => (
        <rect key={`${l}-${c}`} x={c} y={l} width={1.02} height={1.02} fill={casa === "#" ? "var(--parede)" : "var(--chao)"} />
      )))}
      <motion.polyline points="1.5,1.5 3.5,1.5 3.5,3.5 5.5,3.5 5.5,1.5 9.5,1.5 9.5,5.5" fill="none" stroke="var(--caminho)" strokeWidth={0.26}
        strokeLinecap="square" strokeLinejoin="miter" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
        transition={{ duration: 2.4, ease: "easeInOut", repeat: Infinity, repeatDelay: 1.6 }} />
      <circle cx={1.5} cy={1.5} r={0.26} fill="var(--parede)" />
      <circle cx={9.5} cy={5.5} r={0.26} fill="var(--amarelo)" stroke="var(--parede)" strokeWidth={0.08} />
    </svg>
  );
}

function DesenhoRede() {
  return (
    <svg viewBox="0 0 180 130" className="desenho desenho-campo" aria-hidden>
      <g className="linhas-campo">
        <rect x="8" y="8" width="164" height="114" />
        <line x1="90" y1="8" x2="90" y2="122" />
        <circle cx="90" cy="65" r="16" />
        <rect x="8" y="38" width="22" height="54" />
        <rect x="150" y="38" width="22" height="54" />
      </g>
      {ARCOS.map(([a, b], i) => (
        <motion.line key={i} x1={NOS[a][0]} y1={NOS[a][1]} x2={NOS[b][0]} y2={NOS[b][1]} stroke={i % 3 === 0 ? "var(--amarelo)" : "rgba(255,255,255,0.55)"}
          strokeWidth={i % 3 === 0 ? 2.2 : 1.3} initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
          transition={{ duration: 0.8, delay: 0.1 * i }} />
      ))}
      {NOS.map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r={i === 4 ? 7 : 4.5} fill={i === 4 ? "var(--amarelo)" : "#fff"} stroke="var(--gramado-escuro)" strokeWidth={1.5} />
      ))}
    </svg>
  );
}

export function Inicio({ aoEscolher }: { aoEscolher: (parte: "parte1" | "parte2") => void }) {
  const cartoes = [
    {
      id: "parte1" as const, rotulo: "Parte 1", titulo: "Labirinto com chaves",
      texto: "O labirinto vira um grafo de estados: posição, chaves e bônus usados. BFS, DFS, Dijkstra e Bellman-Ford nos mapas do enunciado, do grupo e no mapa surpresa.",
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
      <section className="inicio-faixa">
        <svg className="faixa-campo" viewBox="0 0 1000 400" preserveAspectRatio="xMidYMid slice" aria-hidden>
          <line x1="520" y1="0" x2="520" y2="400" />
          <circle cx="520" cy="200" r="92" />
          <rect x="-1" y="70" width="120" height="260" />
          <rect x="-1" y="140" width="44" height="120" />
          <path d="M119 150a70 70 0 0 1 0 100" />
        </svg>
        <motion.div className="faixa-bola" initial={{ x: -420, rotate: -540, opacity: 0 }} animate={{ x: 0, rotate: 0, opacity: 1 }}
          transition={{ duration: 1.4, ease: [0.2, 0.8, 0.2, 1] }}>
          <IconeBola tamanho={38} />
        </motion.div>
        <div className="inicio-cabecalho">
          <span className="rotulo-claro">Teoria dos Grafos + AVD, CESAR School, 2026.2, turma 5A</span>
          <h1>Grupo 2</h1>
          <p>Projeto final: um labirinto com chaves e uma rede de transferências do futebol, os dois resolvidos como grafos.</p>
        </div>
        <ol className="escalacao" aria-label="Integrantes">
          {ESCALACAO.map((j) => (
            <li key={j.numero}>
              <span className="escalacao-numero">{j.numero}</span>
              <span className="escalacao-nome">{j.nome}</span>
              <span className="escalacao-funcao">{j.funcao}</span>
            </li>
          ))}
        </ol>
      </section>
      <div className="inicio-cartoes">
        {cartoes.map(({ id, rotulo, titulo, texto, Desenho }) => (
          <button key={id} type="button" className={`inicio-cartao inicio-${id}`} onClick={() => aoEscolher(id)}>
            <div className="inicio-desenho"><Desenho /></div>
            <div className="inicio-texto">
              <span className="rotulo-pequeno">{rotulo}</span>
              <h2>{titulo}</h2>
              <p>{texto}</p>
              <span className="inicio-abrir">Abrir <ArrowRight size={18} aria-hidden /></span>
            </div>
          </button>
        ))}
      </div>
    </main>
  );
}
