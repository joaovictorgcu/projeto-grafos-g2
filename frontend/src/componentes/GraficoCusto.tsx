// [IA] Claude Code (Claude Opus 5.5) – curva do custo acumulado por passo, com o passo atual marcado
import { motion } from "motion/react";

interface Serie {
  nome: string;
  cor: string;
  custos: number[];
}

export function GraficoCusto({ series, passo, altura = 150, compacto }: {
  series: Serie[]; passo: number; altura?: number; compacto?: boolean;
}) {
  const largura = 520;
  const margem = compacto ? { e: 6, d: 6, t: 8, b: 8 } : { e: 40, d: 14, t: 14, b: 26 };
  const validas = series.filter((s) => s.custos.length > 1);
  const maxPasso = Math.max(1, ...validas.map((s) => s.custos.length - 1));
  const todos = validas.flatMap((s) => s.custos);
  const menor = Math.min(0, ...todos);
  const maior = Math.max(1, ...todos);
  const x = (i: number) => margem.e + (i / maxPasso) * (largura - margem.e - margem.d);
  const y = (v: number) => margem.t + (1 - (v - menor) / (maior - menor || 1)) * (altura - margem.t - margem.b);
  const marcas = [menor, Math.round((menor + maior) / 2), maior].filter((v, i, a) => a.indexOf(v) === i);

  if (!validas.length) {
    return <div className="grafico-vazio">Sem percurso para desenhar o custo.</div>;
  }

  return (
    <svg className="grafico-custo" viewBox={`0 0 ${largura} ${altura}`} role="img"
      aria-label={`Custo acumulado por passo: ${validas.map((s) => `${s.nome} termina em ${s.custos[s.custos.length - 1]}`).join(", ")}`}>
      {!compacto && marcas.map((v) => (
        <g key={v}>
          <line x1={margem.e} x2={largura - margem.d} y1={y(v)} y2={y(v)} className="grade-grafico" />
          <text x={margem.e - 8} y={y(v) + 4} className="eixo-grafico" textAnchor="end">{v}</text>
        </g>
      ))}
      {!compacto && (
        <>
          <text x={largura - margem.d} y={altura - 6} className="eixo-grafico" textAnchor="end">passo →</text>
          <text x={margem.e} y={altura - 6} className="eixo-grafico">0</text>
        </>
      )}
      {validas.map((s) => {
        const d = s.custos.map((v, i) => `${i ? "L" : "M"} ${x(i)} ${y(v)}`).join(" ");
        const agora = Math.min(passo, s.custos.length - 1);
        return (
          <g key={s.nome}>
            <motion.path d={d} fill="none" stroke={s.cor} strokeWidth={compacto ? 2 : 2.5} strokeLinejoin="round"
              initial={{ pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 1, ease: "easeOut" }} />
            <motion.circle r={compacto ? 3.5 : 5} fill={s.cor} stroke="#0b1020" strokeWidth={2}
              initial={false} animate={{ cx: x(agora), cy: y(s.custos[agora]) }} transition={{ duration: 0.18 }} />
          </g>
        );
      })}
      <motion.line y1={margem.t} y2={altura - margem.b} className="cursor-grafico" initial={false}
        animate={{ x1: x(Math.min(passo, maxPasso)), x2: x(Math.min(passo, maxPasso)) }} transition={{ duration: 0.18 }} />
    </svg>
  );
}
