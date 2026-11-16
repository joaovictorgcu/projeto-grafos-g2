// [IA] Claude Code (Claude Opus 5.5) – barra do topo: volta para o início e mostra as abas da parte aberta
import { motion } from "motion/react";

export interface Aba<T extends string> {
  id: T;
  nome: string;
}

export function Escudo({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden>
      <rect x="3" y="7" width="26" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <path d="M16 7v18M3 12h4v8H3M29 12h-4v8h4" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="16" cy="16" r="3.6" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <circle cx="16" cy="16" r="1.5" className="escudo-bola" />
    </svg>
  );
}

export function Topo<T extends string>({ parte, abas, ativa, aoTrocar, aoInicio }: {
  parte?: string; abas?: Aba<T>[]; ativa?: T; aoTrocar?: (id: T) => void; aoInicio: () => void;
}) {
  return (
    <header className="topo">
      <button type="button" className="marca" onClick={aoInicio} aria-label="Voltar para o início">
        <Escudo className="logo" />
        <span className="marca-texto">
          <span className="marca-titulo">Grupo 2</span>
          <span className="marca-sub">{parte ?? "Teoria dos Grafos e AVD, CESAR School"}</span>
        </span>
      </button>
      {abas && ativa && aoTrocar && (
        <nav className="abas" aria-label="Seções">
          {abas.map(({ id, nome }) => (
            <button key={id} type="button" className={ativa === id ? "aba ativa" : "aba"} onClick={() => aoTrocar(id)}
              aria-current={ativa === id ? "page" : undefined}>
              <span>{nome}</span>
              {ativa === id && <motion.span layoutId="aba-ativa" className="aba-fundo" transition={{ type: "spring", stiffness: 500, damping: 40 }} />}
            </button>
          ))}
        </nav>
      )}
    </header>
  );
}
