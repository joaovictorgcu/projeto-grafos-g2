// [IA] Claude Code (Claude Opus 5.5) – miniatura do mapa para os cartões de escolha
import { memo } from "react";

const COR: Record<string, string> = { "#": "#1c1c1a", "~": "#9cc9f2", ",": "#dcc09a", S: "#1c1c1a", G: "#ff5a00" };

export const Miniatura = memo(function Miniatura({ grade }: { grade: string[] }) {
  const altura = grade.length;
  const largura = grade[0]?.length ?? 0;
  if (!altura) return <div className="miniatura miniatura-vazia" />;
  return (
    <svg className="miniatura" viewBox={`0 0 ${largura} ${altura}`} preserveAspectRatio="xMidYMid meet" aria-hidden>
      {grade.flatMap((linha, l) => [...linha].map((casa, c) => {
        const cor = COR[casa] ?? ("abcd".includes(casa) ? "#d97706" : "ABCD".includes(casa) ? "#c026d3"
          : "+*".includes(casa) ? "#10b981" : "<>^v".includes(casa) ? "#b8ada0" : "#ffffff");
        return <rect key={`${l}-${c}`} x={c} y={l} width={1} height={1} fill={cor} />;
      }))}
    </svg>
  );
});
