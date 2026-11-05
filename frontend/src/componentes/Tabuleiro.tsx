// [IA] Claude Code (Claude Opus 5.5) – tabuleiro em SVG no estilo plano: terreno, chaves, portas, bônus, rastro por camada, jogador, armadilhas e ciclo negativo
import { AnimatePresence, motion } from "motion/react";
import { memo, useEffect, useId, useMemo, useRef, type ReactNode } from "react";
import { CORES_CHAVE, camadasDoMapa, celulasPorCamada, chave, corDaCamada } from "../modelo";
import type { DadosDoMapa, Passo, Resultado } from "../tipos";

const ROTACAO_DA_ESTEIRA: Record<string, number> = { ">": 0, v: 90, "<": 180, "^": 270 };

function centro(l: number, c: number): [number, number] {
  return [c + 0.5, l + 0.5];
}

export const Terreno = memo(function Terreno({ grade }: { grade: string[] }) {
  const casas: ReactNode[] = [];
  grade.forEach((linha, l) => {
    [...linha].forEach((casa, c) => {
      const k = `${l}-${c}`;
      if (casa === "#") {
        casas.push(<rect key={k} x={c - 0.01} y={l - 0.01} width={1.02} height={1.02} className="parede" />);
      } else if (casa === "~") {
        casas.push(
          <g key={k}>
            <rect x={c} y={l} width={1} height={1} className="agua" />
            <path d={`M ${c + 0.15} ${l + 0.42} q 0.175 -0.12 0.35 0 t 0.35 0 M ${c + 0.15} ${l + 0.66} q 0.175 -0.12 0.35 0 t 0.35 0`}
              className="agua-onda" style={{ animationDelay: `${((l * 3 + c) % 5) * -0.4}s` }} />
          </g>,
        );
      } else if (casa === ",") {
        casas.push(
          <g key={k}>
            <rect x={c} y={l} width={1} height={1} className="lama" />
            <circle cx={c + 0.3} cy={l + 0.35} r={0.06} className="lama-ponto" />
            <circle cx={c + 0.66} cy={l + 0.52} r={0.08} className="lama-ponto" />
            <circle cx={c + 0.38} cy={l + 0.74} r={0.05} className="lama-ponto" />
          </g>,
        );
      } else if (casa in ROTACAO_DA_ESTEIRA) {
        const [x, y] = centro(l, c);
        casas.push(
          <g key={k}>
            <rect x={c} y={l} width={1} height={1} className="esteira" />
            <g transform={`rotate(${ROTACAO_DA_ESTEIRA[casa]} ${x} ${y})`}>
              <svg x={c} y={l} width={1} height={1} viewBox={`${c} ${l} 1 1`} overflow="hidden">
                <g className="esteira-fluxo">
                  {[-0.75, -0.25, 0.25, 0.75].map((d) => (
                    <path key={d} d={`M ${x + d - 0.1} ${y - 0.18} L ${x + d + 0.08} ${y} L ${x + d - 0.1} ${y + 0.18}`}
                      className="esteira-seta" />
                  ))}
                </g>
              </svg>
            </g>
          </g>,
        );
      } else {
        casas.push(<rect key={k} x={c} y={l} width={1} height={1} className="chao" />);
      }
    });
  });
  return <g>{casas}</g>;
});

export function Marcos({ grade }: { grade: string[] }) {
  const marcos: ReactNode[] = [];
  grade.forEach((linha, l) => [...linha].forEach((casa, c) => {
    const [x, y] = centro(l, c);
    if (casa === "S") marcos.push(<circle key={`s${l}-${c}`} cx={x} cy={y} r={0.26} className="marco-inicio" />);
    if (casa === "G") {
      marcos.push(
        <g key={`g${l}-${c}`}>
          <circle cx={x} cy={y} r={0.36} className="marco-saida-pulso" />
          <circle cx={x} cy={y} r={0.25} className="marco-saida" />
        </g>,
      );
    }
  }));
  return <g>{marcos}</g>;
}

function Chave({ x, y, cor }: { x: number; y: number; cor: string }) {
  return (
    <g>
      <circle cx={x - 0.14} cy={y} r={0.15} fill="none" stroke={cor} strokeWidth={0.09} />
      <path d={`M ${x + 0.01} ${y} H ${x + 0.33} M ${x + 0.23} ${y} V ${y + 0.12} M ${x + 0.33} ${y} V ${y + 0.1}`}
        stroke={cor} strokeWidth={0.09} strokeLinecap="round" fill="none" />
    </g>
  );
}

function Gema({ x, y }: { x: number; y: number }) {
  return <path d={`M ${x} ${y - 0.28} L ${x + 0.24} ${y} L ${x} ${y + 0.28} L ${x - 0.24} ${y} Z`} className="gema" />;
}

function Estrela({ x, y, gasta }: { x: number; y: number; gasta: boolean }) {
  const pontas = Array.from({ length: 10 }, (_, i) => {
    const r = i % 2 === 0 ? 0.3 : 0.13;
    const a = (Math.PI / 5) * i - Math.PI / 2;
    return `${x + r * Math.cos(a)},${y + r * Math.sin(a)}`;
  }).join(" ");
  return <polygon points={pontas} className={gasta ? "fonte fonte-gasta" : "fonte"} />;
}

function Porta({ x, y, cor, aberta }: { x: number; y: number; cor: string; aberta: boolean }) {
  return (
    <g>
      <motion.rect x={x - 0.5} y={y - 0.5} width={1} height={1} fill={cor}
        style={{ transformBox: "fill-box", transformOrigin: "top" }}
        initial={false} animate={{ scaleY: aberta ? 0.12 : 1, opacity: aberta ? 0.55 : 1 }}
        transition={{ type: "spring", stiffness: 260, damping: 24 }} />
      {!aberta && (
        <g stroke="#fff" strokeWidth={0.07} fill="none" strokeLinecap="round">
          <path d={`M ${x - 0.1} ${y - 0.02} V ${y - 0.12} A 0.1 0.1 0 0 1 ${x + 0.1} ${y - 0.12} V ${y - 0.02}`} />
          <rect x={x - 0.15} y={y - 0.03} width={0.3} height={0.22} rx={0.04} fill="#fff" stroke="none" />
        </g>
      )}
    </g>
  );
}

export function Itens({ dados, chaves, bonus, animar = true }: {
  dados: DadosDoMapa; chaves: string; bonus: number[]; animar?: boolean;
}) {
  const especiais = useMemo(() => {
    const lista: { l: number; c: number; casa: string }[] = [];
    dados.grade.forEach((linha, l) => [...linha].forEach((casa, c) => {
      if ("abcdABCD+*".includes(casa)) lista.push({ l, c, casa });
    }));
    return lista;
  }, [dados.grade]);
  const fontes = especiais.filter((e) => e.casa === "*");
  const indiceDoBonus = useMemo(() => new Map(dados.bonus.map(([l, c, i]) => [chave(l, c), i])), [dados]);

  return (
    <g>
      {especiais.map((e) => {
        const [x, y] = centro(e.l, e.c);
        const k = `${e.l}-${e.c}`;
        if (e.casa >= "A" && e.casa <= "D") {
          return <Porta key={k} x={x} y={y} cor={CORES_CHAVE[e.casa.toLowerCase()]} aberta={chaves.includes(e.casa.toLowerCase())} />;
        }
        if (e.casa === "*") {
          const indice = dados.bonus.length + fontes.findIndex((f) => f.l === e.l && f.c === e.c);
          return <Estrela key={k} x={x} y={y} gasta={dados.fonte_consumivel && bonus.includes(indice)} />;
        }
        return null;
      })}
      <AnimatePresence>
        {especiais.map((e) => {
          const [x, y] = centro(e.l, e.c);
          const k = `${e.l}-${e.c}`;
          const visivel = (e.casa >= "a" && e.casa <= "d" && !chaves.includes(e.casa))
            || (e.casa === "+" && !bonus.includes(indiceDoBonus.get(chave(e.l, e.c)) ?? -1));
          if (!visivel) return null;
          return (
            <motion.g key={k} style={{ transformBox: "fill-box", transformOrigin: "center" }}
              initial={animar ? { opacity: 0, scale: 0.4 } : false} animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.8 }} transition={{ duration: 0.4 }}>
              {e.casa === "+" ? <Gema x={x} y={y} /> : <Chave x={x} y={y} cor={CORES_CHAVE[e.casa]} />}
            </motion.g>
          );
        })}
      </AnimatePresence>
    </g>
  );
}

function Explosao({ x, y, cor }: { x: number; y: number; cor: string }) {
  return (
    <g>
      {Array.from({ length: 12 }, (_, i) => {
        const a = (Math.PI * 2 * i) / 12;
        return (
          <motion.circle key={i} cx={x} cy={y} r={0.07} fill={cor} initial={{ opacity: 1, cx: x, cy: y }}
            animate={{ opacity: 0, cx: x + Math.cos(a) * 1.2, cy: y + Math.sin(a) * 1.2 }} transition={{ duration: 0.7, ease: "easeOut" }} />
        );
      })}
      <motion.circle cx={x} cy={y} fill="none" stroke={cor} strokeWidth={0.07}
        initial={{ r: 0.2, opacity: 1 }} animate={{ r: 1.3, opacity: 0 }} transition={{ duration: 0.6, ease: "easeOut" }} />
    </g>
  );
}

function TextoFlutuante({ x, y, texto, cor }: { x: number; y: number; texto: string; cor: string }) {
  return (
    <motion.text x={x} className="texto-flutuante" fill={cor}
      initial={{ y: y - 0.2, opacity: 0 }} animate={{ y: y - 1.1, opacity: [0, 1, 1, 0] }} transition={{ duration: 1.1, ease: "easeOut" }}>
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

function Rastro({ passos, passo, duracao, cor, tracejado, deslocar }: {
  passos: Passo[]; passo: number; duracao: number; cor: (chaves: string) => string; tracejado?: boolean;
  deslocar: (chaves: string) => number;
}) {
  const completos = trechos(passos, Math.max(0, passo - 1), cor, deslocar);
  const d = passo > 0 ? deslocar(passos[passo - 1].estado.chaves) : 0;
  const ultimo = passo > 0 ? { de: passos[passo - 1].estado, para: passos[passo].estado } : null;
  return (
    <g className={tracejado ? "rastro rastro-fantasma" : "rastro"}>
      {completos.map((t, i) => (
        <path key={i} d={t.pontos.map(([x, y], j) => `${j ? "L" : "M"} ${x} ${y}`).join(" ")} stroke={t.cor} className="rastro-linha" />
      ))}
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
      {!fantasma && <circle r={0.5} fill={cor} className="jogador-aura" />}
      <circle r={fantasma ? 0.24 : 0.3} fill={cor} stroke="#fff" strokeWidth={0.08}
        strokeDasharray={fantasma ? "0.12 0.08" : undefined} className="jogador-corpo" />
      {!fantasma && chaves && (
        <g className="orbita">
          {[...chaves].map((k, i) => {
            const a = (Math.PI * 2 * i) / chaves.length;
            return <circle key={k} cx={Math.cos(a) * 0.48} cy={Math.sin(a) * 0.48} r={0.1} fill={CORES_CHAVE[k]} stroke="#fff" strokeWidth={0.04} />;
          })}
        </g>
      )}
    </motion.g>
  );
}

interface Props {
  dados: DadosDoMapa;
  resultado: Resultado;
  passos: Passo[];
  passo: number;
  duracao: number;
  camadaFixa: string | null;
  mostrarArmadilhas: boolean;
  compacto?: boolean;
  corDoJogador?: string;
  fantasma?: { passos: Passo[]; passo: number; cor: string };
}

export function Tabuleiro(props: Props) {
  const { dados, resultado, passos, passo, duracao, camadaFixa, mostrarArmadilhas, compacto, fantasma } = props;
  const prefixo = "t" + useId().replace(/[^a-zA-Z0-9]/g, "");
  const grade = dados.grade;
  const altura = grade.length;
  const largura = grade[0]?.length ?? 0;
  const camadas = useMemo(() => camadasDoMapa(dados), [dados]);
  const grupos = useMemo(() => celulasPorCamada(dados.estados), [dados]);
  const cor = (chaves: string) => corDaCamada(camadas, chaves);
  const passoDoDeslocamento = Math.min(0.14, 0.5 / Math.max(1, camadas.length));
  const deslocar = (chaves: string) => (camadas.findIndex((c) => c.chaves === chaves) - (camadas.length - 1) / 2) * passoDoDeslocamento;
  const atual = passos[Math.min(passo, passos.length - 1)];
  const chavesAtuais = atual.estado.chaves;
  const camadaVista = camadaFixa ?? chavesAtuais;
  const grupo = grupos.get(camadaVista);
  const anterior = useRef(passo);
  const avancou = passo === anterior.current + 1;
  useEffect(() => {
    anterior.current = passo;
  }, [passo]);

  const negativas = useMemo(() => {
    const lista: [number, number, string][] = [];
    grade.forEach((linha, l) => [...linha].forEach((casa, c) => { if (casa === "+" || casa === "*") lista.push([l, c, casa]); }));
    return lista;
  }, [grade]);
  const ciclo = resultado.status === "CICLO_NEGATIVO" && resultado.ciclo
    ? resultado.ciclo.estados.map((i) => centro(dados.estados[i].l, dados.estados[i].c)) : null;
  const caminhoDoCiclo = ciclo ? ciclo.map(([x, y], j) => `${j ? "L" : "M"} ${x} ${y}`).join(" ") : "";
  const mostrarTodasArmadilhas = mostrarArmadilhas || resultado.status === "SEM_SOLUCAO";

  return (
    <svg className={compacto ? "tabuleiro compacto" : "tabuleiro"} viewBox={`-0.15 -0.15 ${largura + 0.3} ${altura + 0.3}`}
      role="img" aria-label={`Labirinto ${dados.titulo}, passo ${passo}`}>
      <defs>
        <pattern id={`${prefixo}-hachura`} width="0.25" height="0.25" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <rect width="0.25" height="0.25" fill="rgba(220,38,38,0.08)" />
          <line x1="0" y1="0" x2="0" y2="0.25" stroke="rgba(220,38,38,0.55)" strokeWidth="0.06" />
        </pattern>
      </defs>
      <rect x={-0.15} y={-0.15} width={largura + 0.3} height={altura + 0.3} className="tabuleiro-moldura" />
      <Terreno grade={grade} />

      <AnimatePresence>
        {grupo && (
          <motion.g key={`camada-${camadaVista}`} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.4 }}>
            {[...grupo.todas].map((k) => {
              const [l, c] = k.split(",").map(Number);
              return <rect key={k} x={c} y={l} width={1} height={1} fill={cor(camadaVista)} opacity={0.08} />;
            })}
          </motion.g>
        )}
      </AnimatePresence>

      {grupo && mostrarTodasArmadilhas && (
        <g>
          {[...grupo.armadilhas].map((k) => {
            const [l, c] = k.split(",").map(Number);
            return (
              <g key={k}>
                <rect x={c} y={l} width={1} height={1} fill={`url(#${prefixo}-hachura)`} />
                <path d={`M ${c + 0.36} ${l + 0.36} L ${c + 0.64} ${l + 0.64} M ${c + 0.64} ${l + 0.36} L ${c + 0.36} ${l + 0.64}`} className="armadilha-x" />
              </g>
            );
          })}
        </g>
      )}

      {resultado.status === "RECUSA" && negativas.map(([l, c, casa]) => (
        <g key={`neg-${l}-${c}`}>
          <circle cx={c + 0.5} cy={l + 0.5} r={0.6} className="alerta-negativo" />
          <text x={c + 0.5} y={l - 0.18} className="rotulo-negativo">{casa === "+" ? "−4" : "−2"}</text>
        </g>
      ))}

      <Itens dados={dados} chaves={chavesAtuais} bonus={atual.estado.bonus} />
      <Marcos grade={grade} />

      {ciclo && (
        <g>
          <path d={caminhoDoCiclo} className="ciclo-fundo" />
          <path d={caminhoDoCiclo} className="ciclo-linha" />
          <circle r={0.18} className="ciclo-ponto">
            <animateMotion dur="1.4s" repeatCount="indefinite" path={caminhoDoCiclo} />
          </circle>
          <text x={ciclo[0][0]} y={ciclo[0][1] - 0.75} className="rotulo-ciclo">ciclo de custo {resultado.ciclo!.custo}</text>
        </g>
      )}

      {resultado.status === "OK" && (
        <Rastro passos={passos} passo={passo} duracao={duracao} cor={props.corDoJogador ? () => props.corDoJogador! : cor} deslocar={deslocar} />
      )}
      {fantasma && (
        <Rastro deslocar={() => 0.12} passos={fantasma.passos} passo={Math.min(fantasma.passo, fantasma.passos.length - 1)} duracao={duracao}
          cor={() => fantasma.cor} tracejado />
      )}
      {fantasma && (
        <Jogador passo={fantasma.passos[Math.min(fantasma.passo, fantasma.passos.length - 1)]} cor={fantasma.cor} duracao={duracao} chaves="" fantasma />
      )}
      <Jogador passo={atual} cor={props.corDoJogador ?? cor(chavesAtuais)} duracao={duracao} chaves={chavesAtuais} />

      <AnimatePresence>
        {avancou && !compacto && atual.novaChave && (
          <Explosao key={`chave-${passo}`} x={atual.estado.c + 0.5} y={atual.estado.l + 0.5} cor={CORES_CHAVE[atual.novaChave]} />
        )}
        {avancou && !compacto && atual.novaChave && (
          <TextoFlutuante key={`chave-texto-${passo}`} x={atual.estado.c + 0.5} y={atual.estado.l + 0.5} texto={`chave ${atual.novaChave}!`}
            cor={CORES_CHAVE[atual.novaChave]} />
        )}
        {avancou && !compacto && !atual.novaChave && atual.delta !== 1 && (
          <TextoFlutuante key={`custo-${passo}`} x={atual.estado.c + 0.5} y={atual.estado.l + 0.5}
            texto={atual.delta > 0 ? `+${atual.delta}` : `−${Math.abs(atual.delta)}`} cor={atual.delta < 0 ? "#059669" : "#c2410c"} />
        )}
      </AnimatePresence>
    </svg>
  );
}
