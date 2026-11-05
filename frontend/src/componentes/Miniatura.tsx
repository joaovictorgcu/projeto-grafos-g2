// [IA] Claude Code (Claude Opus 5.5) – miniatura do mapa para os cartões de escolha
import { memo } from "react";

const COR: Record<string, string> = { "#": "#25304f", "~": "#2563eb", ",": "#8a6a3f", S: "#34d399", G: "#fbbf24" };

export const Miniatura = memo(function Miniatura({ grade }: { grade: string[] }) {
  const altura = grade.length;
  const largura = grade[0]?.length ?? 0;
  if (!altura) return <div className="miniatura miniatura-vazia" />;
  return (
    <svg className="miniatura" viewBox={`0 0 ${largura} ${altura}`} preserveAspectRatio="xMidYMid meet" aria-hidden>
      {grade.flatMap((linha, l) => [...linha].map((casa, c) => {
        const cor = COR[casa] ?? ("abcd".includes(casa) ? "#f59e0b" : "ABCD".includes(casa) ? "#f472b6"
          : "+*".includes(casa) ? "#22d3ee" : "<>^v".includes(casa) ? "#64748b" : "#141c30");
        return <rect key={`${l}-${c}`} x={c} y={l} width={1} height={1} fill={cor} />;
      }))}
    </svg>
  );
});
