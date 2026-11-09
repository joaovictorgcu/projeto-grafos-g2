// [IA] Claude Code (Claude Opus 5.5) – barra do topo: volta para o início e mostra as abas da parte aberta
import { motion } from "motion/react";

export interface Aba<T extends string> {
  id: T;
  nome: string;
}

export function Topo<T extends string>({ parte, abas, ativa, aoTrocar, aoInicio }: {
  parte?: string; abas?: Aba<T>[]; ativa?: T; aoTrocar?: (id: T) => void; aoInicio: () => void;
}) {
  return (
    <header className="topo">
      <button type="button" className="marca" onClick={aoInicio} aria-label="Voltar para o início">
        <svg viewBox="0 0 32 32" className="logo" aria-hidden>
          <path d="M7 7h8v6h6V7h4v12h-6v6H7z" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinejoin="round" />
          <circle cx="23" cy="23" r="3" className="logo-ponto" />
        </svg>
        <span className="marca-texto">
          <span className="marca-titulo">Grafos · Grupo 2</span>
          <span className="marca-sub">{parte ?? "Teoria dos Grafos e AVD · CESAR School"}</span>
        </span>
      </button>
      {abas && ativa && aoTrocar && (
        <nav className="abas" aria-label="Seções">
          {abas.map(({ id, nome }) => (
            <button key={id} type="button" className={ativa === id ? "aba ativa" : "aba"} onClick={() => aoTrocar(id)}
              aria-current={ativa === id ? "page" : undefined}>
              {ativa === id && <motion.span layoutId="aba-ativa" className="aba-fundo" transition={{ type: "spring", stiffness: 400, damping: 32 }} />}
              <span>{nome}</span>
            </button>
          ))}
        </nav>
      )}
    </header>
  );
}
