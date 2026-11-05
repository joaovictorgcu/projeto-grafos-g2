// [IA] Claude Code (Claude Opus 5.5) – tabuleiro animado em SVG: terreno, chaves, portas, bônus, rastro por camada, jogador, onda de exploração, armadilhas e ciclo negativo
import { AnimatePresence, motion } from "motion/react";
import { memo, useEffect, useId, useMemo, useRef, type ReactNode } from "react";
import {
  CORES_CHAVE,
  camadasDoMapa,
  celulasPorCamada,
  chave,
  corDaCamada,
  ondaDeExploracao,
} from "../modelo";
import type { DadosDoMapa, Modo, Passo, Resultado } from "../tipos";

const ROTACAO_DA_ESTEIRA: Record<string, number> = { ">": 0, v: 90, "<": 180, "^": 270 };

interface Fantasma {
  passos: Passo[];
  passo: number;
  cor: string;
}

interface Props {
  dados: DadosDoMapa;
  resultado: Resultado;
  passos: Passo[];
  passo: number;
  duracao: number;
  modo: Modo;
  camadaFixa: string | null;
  mostrarArmadilhas: boolean;
  repeticaoDaOnda?: number;
  compacto?: boolean;
  corDoJogador?: string;
  fantasma?: Fantasma;
}

function centro(l: number, c: number): [number, number] {
  return [c + 0.5, l + 0.5];
}

function corDaDistancia(fracao: number) {
  const matiz = 195 + fracao * 130;
  return `hsl(${matiz} 90% 62%)`;
}

const Terreno = memo(function Terreno({ grade, prefixo }: { grade: string[]; prefixo: string }) {
  const casas: ReactNode[] = [];
  grade.forEach((linha, l) => {
    [...linha].forEach((casa, c) => {
      const k = `${l}-${c}`;
      if (casa === "#") {
        casas.push(<rect key={k} x={c} y={l} width={1.02} height={1.02} fill={`url(#${prefixo}-parede)`} />);
        return;
      }
      const xadrez = (l + c) % 2 === 0;
      casas.push(
        <rect key={k} x={c + 0.04} y={l + 0.04} width={0.92} height={0.92} rx={0.16}
          className={xadrez ? "chao chao-a" : "chao chao-b"} />,
      );
      if (casa === "~") {
        casas.push(
          <g key={`${k}-agua`}>
            <rect x={c + 0.04} y={l + 0.04} width={0.92} height={0.92} rx={0.16} className="agua" />
            <rect x={c + 0.04} y={l + 0.04} width={0.92} height={0.92} rx={0.16} className="agua-brilho"
              style={{ animationDelay: `${((l * 3 + c) % 7) * -0.35}s` }} />
          </g>,
        );
      } else if (casa === ",") {
        casas.push(
          <g key={`${k}-lama`}>
            <rect x={c + 0.04} y={l + 0.04} width={0.92} height={0.92} rx={0.16} className="lama" />
            <circle cx={c + 0.3} cy={l + 0.35} r={0.07} className="lama-ponto" />
            <circle cx={c + 0.66} cy={l + 0.5} r={0.09} className="lama-ponto" />
            <circle cx={c + 0.4} cy={l + 0.72} r={0.06} className="lama-ponto" />
          </g>,
        );
      } else if (casa in ROTACAO_DA_ESTEIRA) {
        const [x, y] = centro(l, c);
        casas.push(
          <g key={`${k}-esteira`} clipPath={`url(#${prefixo}-casa-${l}-${c})`}>
            <rect x={c + 0.04} y={l + 0.04} width={0.92} height={0.92} rx={0.16} className="esteira" />
            <g transform={`rotate(${ROTACAO_DA_ESTEIRA[casa]} ${x} ${y})`}>
              <g className="esteira-fluxo">
                {[-0.75, -0.25, 0.25, 0.75].map((d) => (
                  <path key={d} d={`M ${x + d - 0.12} ${y - 0.2} L ${x + d + 0.08} ${y} L ${x + d - 0.12} ${y + 0.2}`}
                    className="esteira-seta" />
                ))}
              </g>
            </g>
          </g>,
        );
      } else if (casa === "S") {
        const [x, y] = centro(l, c);
        casas.push(
          <g key={`${k}-inicio`}>
            <circle cx={x} cy={y} r={0.34} className="inicio-anel" />
            <text x={x} y={y + 0.14} className="rotulo-casa inicio-texto">S</text>
          </g>,
        );
      } else if (casa === "G") {
        const [x, y] = centro(l, c);
        casas.push(
          <g key={`${k}-saida`}>
            <circle cx={x} cy={y} r={0.44} className="saida-brilho" />
            <circle cx={x} cy={y} r={0.36} className="saida-anel" />
            <circle cx={x} cy={y} r={0.22} className="saida-miolo" />
            <text x={x} y={y + 0.13} className="rotulo-casa saida-texto">G</text>
          </g>,
        );
      }
    });
  });
  return <g>{casas}</g>;
});

function Chave({ x, y, cor }: { x: number; y: number; cor: string }) {
  return (
    <g className="flutuar">
      <circle cx={x - 0.14} cy={y} r={0.16} fill="none" stroke={cor} strokeWidth={0.09} />
      <path d={`M ${x + 0.02} ${y} H ${x + 0.34} M ${x + 0.24} ${y} V ${y + 0.12} M ${x + 0.34} ${y} V ${y + 0.1}`}
        stroke={cor} strokeWidth={0.09} strokeLinecap="round" fill="none" />
    </g>
  );
}

function Gema({ x, y }: { x: number; y: number }) {
  return (
    <g className="flutuar">
      <path d={`M ${x} ${y - 0.3} L ${x + 0.26} ${y - 0.04} L ${x} ${y + 0.3} L ${x - 0.26} ${y - 0.04} Z`} className="gema" />
      <path d={`M ${x - 0.26} ${y - 0.04} H ${x + 0.26} M ${x} ${y - 0.3} L ${x - 0.09} ${y - 0.04} L ${x} ${y + 0.3}`}
        className="gema-faceta" />
    </g>
  );
}

function Estrela({ x, y, gasta }: { x: number; y: number; gasta: boolean }) {
  const pontas = Array.from({ length: 10 }, (_, i) => {
    const r = i % 2 === 0 ? 0.32 : 0.14;
    const a = (Math.PI / 5) * i - Math.PI / 2;
    return `${x + r * Math.cos(a)},${y + r * Math.sin(a)}`;
  }).join(" ");
  return <polygon points={pontas} className={gasta ? "fonte fonte-gasta" : "fonte"} />;
}

function Porta({ x, y, cor, aberta }: { x: number; y: number; cor: string; aberta: boolean }) {
  return (
    <g>
      <rect x={x - 0.42} y={y - 0.42} width={0.84} height={0.84} rx={0.12} fill="none" stroke={cor} strokeWidth={0.06}
        opacity={0.9} />
      <motion.rect x={x - 0.36} y={y - 0.36} width={0.72} height={0.72} rx={0.08} fill={cor}
        style={{ transformBox: "fill-box", transformOrigin: "top" }}
        initial={false} animate={{ scaleY: aberta ? 0.06 : 1, opacity: aberta ? 0.5 : 0.85 }}
        transition={{ type: "spring", stiffness: 260, damping: 22 }} />
      {!aberta && (
        <g stroke="#0b1020" strokeWidth={0.07} fill="none" strokeLinecap="round">
          <path d={`M ${x - 0.1} ${y - 0.02} V ${y - 0.12} A 0.1 0.1 0 0 1 ${x + 0.1} ${y - 0.12} V ${y - 0.02}`} />
          <rect x={x - 0.15} y={y - 0.03} width={0.3} height={0.22} rx={0.04} fill="#0b1020" />
        </g>
      )}
    </g>
  );
}

function Explosao({ x, y, cor }: { x: number; y: number; cor: string }) {
  return (
    <g>
      {Array.from({ length: 14 }, (_, i) => {
        const a = (Math.PI * 2 * i) / 14;
        return (
          <motion.circle key={i} cx={x} cy={y} r={0.07} fill={cor}
            initial={{ opacity: 1, cx: x, cy: y }}
            animate={{ opacity: 0, cx: x + Math.cos(a) * 1.3, cy: y + Math.sin(a) * 1.3 }}
            transition={{ duration: 0.8, ease: "easeOut" }} />
        );
      })}
      <motion.circle cx={x} cy={y} fill="none" stroke={cor} strokeWidth={0.08}
        initial={{ r: 0.2, opacity: 1 }} animate={{ r: 1.4, opacity: 0 }} transition={{ duration: 0.7, ease: "easeOut" }} />
    </g>
  );
}

function TextoFlutuante({ x, y, texto, cor }: { x: number; y: number; texto: string; cor: string }) {
  return (
    <motion.text x={x} className="texto-flutuante" fill={cor}
      initial={{ y: y - 0.2, opacity: 0 }} animate={{ y: y - 1.1, opacity: [0, 1, 1, 0] }}
      transition={{ duration: 1.1, ease: "easeOut" }}>
      {texto}
    </motion.text>
  );
}

function trechos(passos: Passo[], ate: number, cor: (chaves: string) => string, deslocar: (chaves: string) => number) {
  const lista: { cor: string; pontos: [number, number][] }[] = [];
  for (let n = 1; n <= ate; n++) {
    const de = passos[n - 1].estado;
    const para = passos[n].estado;
    const tom = cor(de.chaves);
    const d = deslocar(de.chaves);
    const fim: [number, number] = [para.c + 0.5 + d, para.l + 0.5 + d];
    const ultimo = lista[lista.length - 1];
    if (ultimo && ultimo.cor === tom) ultimo.pontos.push(fim);
    else lista.push({ cor: tom, pontos: [[de.c + 0.5 + d, de.l + 0.5 + d], fim] });
  }
  return lista;
}

function Rastro({ passos, passo, duracao, cor, prefixo, tracejado, deslocar }: {
  passos: Passo[]; passo: number; duracao: number; cor: (chaves: string) => string; prefixo: string; tracejado?: boolean;
  deslocar: (chaves: string) => number;
}) {
  const completos = trechos(passos, Math.max(0, passo - 1), cor, deslocar);
  const d = passo > 0 ? deslocar(passos[passo - 1].estado.chaves) : 0;
  const ultimo = passo > 0 ? { de: passos[passo - 1].estado, para: passos[passo].estado } : null;
  return (
    <g className={tracejado ? "rastro rastro-fantasma" : "rastro"}>
      {completos.map((t, i) => {
        const d = t.pontos.map(([x, y], j) => `${j ? "L" : "M"} ${x} ${y}`).join(" ");
        return (
          <g key={i}>
            {!tracejado && <path d={d} stroke={t.cor} className="rastro-brilho" filter={`url(#${prefixo}-brilho)`} />}
            <path d={d} stroke={t.cor} className="rastro-linha" />
          </g>
        );
      })}
      {ultimo && (
        <motion.path key={passo}
          d={`M ${ultimo.de.c + 0.5 + d} ${ultimo.de.l + 0.5 + d} L ${ultimo.para.c + 0.5 + d} ${ultimo.para.l + 0.5 + d}`}
          stroke={cor(ultimo.de.chaves)} className="rastro-linha"
          initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: duracao, ease: "easeInOut" }} />
      )}
    </g>
  );
}

function Jogador({ passo, cor, duracao, chaves, fantasma }: {
  passo: Passo; cor: string; duracao: number; chaves: string; fantasma?: boolean;
}) {
  const [x, y] = centro(passo.estado.l, passo.estado.c);
  return (
    <motion.g initial={false} animate={{ x, y }} transition={{ duration: duracao, ease: "easeInOut" }}>
      {!fantasma && <circle r={0.62} fill={cor} className="jogador-aura" />}
      <circle r={fantasma ? 0.26 : 0.32} fill={cor} stroke="#f8fafc" strokeWidth={0.07}
        strokeDasharray={fantasma ? "0.12 0.08" : undefined} className="jogador-corpo" />
      {!fantasma && chaves && (
        <g className="orbita">
          {[...chaves].map((k, i) => {
            const a = (Math.PI * 2 * i) / chaves.length;
            return <circle key={k} cx={Math.cos(a) * 0.52} cy={Math.sin(a) * 0.52} r={0.1} fill={CORES_CHAVE[k]}
              stroke="#0b1020" strokeWidth={0.03} />;
          })}
        </g>
      )}
    </motion.g>
  );
}

export function Tabuleiro(props: Props) {
  const { dados, resultado, passos, passo, duracao, modo, camadaFixa, mostrarArmadilhas, compacto, fantasma } = props;
  const prefixo = "t" + useId().replace(/[^a-zA-Z0-9]/g, "");
  const grade = dados.grade;
  const altura = grade.length;
  const largura = grade[0]?.length ?? 0;
  const camadas = useMemo(() => camadasDoMapa(dados), [dados]);
  const grupos = useMemo(() => celulasPorCamada(dados.estados), [dados]);
  const onda = useMemo(() => ondaDeExploracao(dados, resultado), [dados, resultado]);
  const cor = (chaves: string) => corDaCamada(camadas, chaves);
  const passoDoDeslocamento = Math.min(0.14, 0.5 / Math.max(1, camadas.length));
  const deslocar = (chaves: string) =>
    (camadas.findIndex((c) => c.chaves === chaves) - (camadas.length - 1) / 2) * passoDoDeslocamento;
  const atual = passos[Math.min(passo, passos.length - 1)];
  const chavesAtuais = atual.estado.chaves;
  const camadaVista = camadaFixa ?? chavesAtuais;
  const grupo = grupos.get(camadaVista);
  const anterior = useRef(passo);
  const avancou = passo === anterior.current + 1;
  useEffect(() => {
    anterior.current = passo;
  }, [passo]);

  const especiais = useMemo(() => {
    const lista: { l: number; c: number; casa: string }[] = [];
    grade.forEach((linha, l) => [...linha].forEach((casa, c) => {
      if ("abcdABCD+*".includes(casa)) lista.push({ l, c, casa });
    }));
    return lista;
  }, [grade]);
  const fontes = especiais.filter((e) => e.casa === "*");
  const indiceDoBonus = useMemo(() => new Map(dados.bonus.map(([l, c, i]) => [chave(l, c), i])), [dados]);

  const duracaoDaOnda = Math.min(4.5, Math.max(1.6, onda.total * 0.012));
  const tempoDaOnda = (ordem: number) => (ordem / Math.max(1, onda.total)) * duracaoDaOnda;
  const ciclo = resultado.status === "CICLO_NEGATIVO" && resultado.ciclo
    ? resultado.ciclo.estados.map((i) => centro(dados.estados[i].l, dados.estados[i].c)) : null;
  const caminhoDoCiclo = ciclo ? ciclo.map(([x, y], j) => `${j ? "L" : "M"} ${x} ${y}`).join(" ") : "";
  const mostrarTodasArmadilhas = mostrarArmadilhas || resultado.status === "SEM_SOLUCAO";

  return (
    <svg className={compacto ? "tabuleiro compacto" : "tabuleiro"} viewBox={`-0.3 -0.3 ${largura + 0.6} ${altura + 0.6}`}
      role="img" aria-label={`Labirinto ${dados.titulo}, passo ${passo}`}>
      <defs>
        <linearGradient id={`${prefixo}-parede`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#2c3a5e" />
          <stop offset="1" stopColor="#1b2440" />
        </linearGradient>
        <pattern id={`${prefixo}-hachura`} width="0.25" height="0.25" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <rect width="0.25" height="0.25" fill="rgba(248,113,113,0.12)" />
          <line x1="0" y1="0" x2="0" y2="0.25" stroke="rgba(248,113,113,0.7)" strokeWidth="0.07" />
        </pattern>
        <filter id={`${prefixo}-brilho`} x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="0.18" />
        </filter>
        {grade.flatMap((linha, l) => [...linha].map((casa, c) =>
          casa in ROTACAO_DA_ESTEIRA ? (
            <clipPath key={`${l}-${c}`} id={`${prefixo}-casa-${l}-${c}`}>
              <rect x={c + 0.04} y={l + 0.04} width={0.92} height={0.92} rx={0.16} />
            </clipPath>
          ) : null,
        ))}
      </defs>

      <rect x={-0.3} y={-0.3} width={largura + 0.6} height={altura + 0.6} rx={0.5} className="tabuleiro-fundo" />
      <Terreno grade={grade} prefixo={prefixo} />

      <AnimatePresence>
        {grupo && modo === "percurso" && (
          <motion.g key={`camada-${camadaVista}`} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}>
            {[...grupo.todas].map((k) => {
              const [l, c] = k.split(",").map(Number);
              return <rect key={k} x={c + 0.04} y={l + 0.04} width={0.92} height={0.92} rx={0.16} fill={cor(camadaVista)}
                opacity={0.07} />;
            })}
          </motion.g>
        )}
      </AnimatePresence>

      {modo === "exploracao" && (
        <g key={`onda-${props.repeticaoDaOnda ?? 0}-${resultado.status}`}>
          {[...onda.celulas].map(([k, { ordem, distancia }]) => {
            const [l, c] = k.split(",").map(Number);
            const fracao = (distancia - onda.menor) / Math.max(1, onda.maior - onda.menor);
            return (
              <g key={k}>
                <rect x={c + 0.08} y={l + 0.08} width={0.84} height={0.84} rx={0.18} fill={corDaDistancia(fracao)}
                  className="onda" style={{ animationDelay: `${tempoDaOnda(ordem)}s` }}>
                  <title>{`distância ${distancia} · ${ordem + 1}º descoberto`}</title>
                </rect>
                {largura * altura <= 420 && !compacto && (
                  <text x={c + 0.5} y={l + 0.62} className="onda-texto" style={{ animationDelay: `${tempoDaOnda(ordem)}s` }}>
                    {distancia}
                  </text>
                )}
              </g>
            );
          })}
        </g>
      )}

      {grupo && mostrarTodasArmadilhas && (
        <g>
          {[...grupo.armadilhas].map((k) => {
            const [l, c] = k.split(",").map(Number);
            return (
              <g key={k}>
                <rect x={c + 0.06} y={l + 0.06} width={0.88} height={0.88} rx={0.16} fill={`url(#${prefixo}-hachura)`}
                  className="armadilha" />
                <path d={`M ${c + 0.36} ${l + 0.36} L ${c + 0.64} ${l + 0.64} M ${c + 0.64} ${l + 0.36} L ${c + 0.36} ${l + 0.64}`}
                  className="armadilha-x" />
              </g>
            );
          })}
        </g>
      )}

      {resultado.status === "RECUSA" && (
        <g>
          {especiais.filter((e) => e.casa === "+" || e.casa === "*").map((e) => (
            <g key={`neg-${e.l}-${e.c}`}>
              <circle cx={e.c + 0.5} cy={e.l + 0.5} r={0.62} className="alerta-negativo" />
              <text x={e.c + 0.5} y={e.l - 0.18} className="rotulo-negativo">{e.casa === "+" ? "−4" : "−2"}</text>
            </g>
          ))}
        </g>
      )}

      {especiais.map((e) => {
        const [x, y] = centro(e.l, e.c);
        const k = `${e.l}-${e.c}`;
        if (e.casa >= "A" && e.casa <= "D") {
          return <Porta key={k} x={x} y={y} cor={CORES_CHAVE[e.casa.toLowerCase()]}
            aberta={chavesAtuais.includes(e.casa.toLowerCase())} />;
        }
        if (e.casa === "*") {
          const indice = dados.bonus.length + fontes.findIndex((f) => f.l === e.l && f.c === e.c);
          return <Estrela key={k} x={x} y={y} gasta={dados.fonte_consumivel && atual.estado.bonus.includes(indice)} />;
        }
        return null;
      })}
      <AnimatePresence>
        {especiais.map((e) => {
          const [x, y] = centro(e.l, e.c);
          const k = `${e.l}-${e.c}`;
          if (e.casa >= "a" && e.casa <= "d" && !chavesAtuais.includes(e.casa)) {
            return (
              <motion.g key={k} style={{ transformBox: "fill-box", transformOrigin: "center" }}
                initial={{ opacity: 0, scale: 0.4 }} animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.8, y: -0.5 }} transition={{ duration: 0.45 }}>
                <Chave x={x} y={y} cor={CORES_CHAVE[e.casa]} />
              </motion.g>
            );
          }
          if (e.casa === "+" && !atual.estado.bonus.includes(indiceDoBonus.get(chave(e.l, e.c)) ?? -1)) {
            return (
              <motion.g key={k} style={{ transformBox: "fill-box", transformOrigin: "center" }}
                initial={{ opacity: 0, scale: 0.4 }} animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0, rotate: 120 }} transition={{ duration: 0.45 }}>
                <Gema x={x} y={y} />
              </motion.g>
            );
          }
          return null;
        })}
      </AnimatePresence>

      {ciclo && (
        <g>
          <path d={caminhoDoCiclo} className="ciclo-fundo" />
          <path d={caminhoDoCiclo} className="ciclo-linha" />
          <circle r={0.2} className="ciclo-ponto">
            <animateMotion dur="1.4s" repeatCount="indefinite" path={caminhoDoCiclo} />
          </circle>
          <text x={ciclo[0][0]} y={ciclo[0][1] - 0.75} className="rotulo-ciclo">
            ciclo de custo {resultado.ciclo!.custo}
          </text>
        </g>
      )}

      {modo === "percurso" && resultado.status === "OK" && (
        <Rastro passos={passos} passo={passo} duracao={duracao} cor={props.corDoJogador ? () => props.corDoJogador! : cor}
          prefixo={prefixo} deslocar={deslocar} />
      )}
      {fantasma && (
        <Rastro deslocar={() => 0.12} passos={fantasma.passos} passo={Math.min(fantasma.passo, fantasma.passos.length - 1)} duracao={duracao}
          cor={() => fantasma.cor} prefixo={prefixo} tracejado />
      )}
      {fantasma && (
        <Jogador passo={fantasma.passos[Math.min(fantasma.passo, fantasma.passos.length - 1)]} cor={fantasma.cor}
          duracao={duracao} chaves="" fantasma />
      )}

      <Jogador passo={atual} cor={props.corDoJogador ?? cor(chavesAtuais)} duracao={duracao} chaves={chavesAtuais} />

      <AnimatePresence>
        {avancou && !compacto && atual.novaChave && (
          <Explosao key={`chave-${passo}`} x={atual.estado.c + 0.5} y={atual.estado.l + 0.5} cor={CORES_CHAVE[atual.novaChave]} />
        )}
        {avancou && !compacto && atual.novaChave && (
          <TextoFlutuante key={`chave-texto-${passo}`} x={atual.estado.c + 0.5} y={atual.estado.l + 0.5}
            texto={`chave ${atual.novaChave}!`} cor={CORES_CHAVE[atual.novaChave]} />
        )}
        {avancou && !compacto && !atual.novaChave && atual.delta !== 1 && (
          <TextoFlutuante key={`custo-${passo}`} x={atual.estado.c + 0.5} y={atual.estado.l + 0.5}
            texto={atual.delta > 0 ? `+${atual.delta}` : `−${Math.abs(atual.delta)}`}
            cor={atual.delta < 0 ? "#34d399" : "#fbbf24"} />
        )}
      </AnimatePresence>
    </svg>
  );
}
