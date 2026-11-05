// [IA] Claude Code (Claude Opus 5.5) – faixa com o resultado do algoritmo: caminho, recusa, ciclo negativo ou sem solução
import { Ban, CircleCheck, Infinity as Infinito, Route } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { NOME_DO_ALGORITMO, NOME_DO_STATUS } from "../modelo";
import type { Algoritmo, Resultado } from "../tipos";

const ICONE = { OK: CircleCheck, RECUSA: Ban, CICLO_NEGATIVO: Infinito, SEM_SOLUCAO: Route };

function explicacao(algoritmo: Algoritmo, r: Resultado, fonte: boolean) {
  const nome = NOME_DO_ALGORITMO[algoritmo];
  if (r.status === "OK") {
    return `${nome} chegou ao G em ${r.passos} passos, com custo ${r.custo}.`;
  }
  if (r.status === "RECUSA") {
    return `${nome} não aceita peso negativo. As casas marcadas valem menos que zero; use o Bellman-Ford.`;
  }
  if (r.status === "CICLO_NEGATIVO") {
    return `Ir e voltar no ciclo marcado sempre diminui o custo, então não existe caminho mais barato.${fonte ? "" : " Ative a fonte consumível."}`;
  }
  return "Nenhum estado em G é alcançável a partir do início: todos os estados alcançáveis são armadilhas.";
}

export function Status({ algoritmo, resultado, fonte }: { algoritmo: Algoritmo; resultado: Resultado; fonte: boolean }) {
  const Icone = ICONE[resultado.status];
  return (
    <AnimatePresence mode="wait">
      <motion.div key={`${algoritmo}-${resultado.status}-${resultado.custo}`} className={`status status-${resultado.status.toLowerCase()}`}
        initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 8 }} transition={{ duration: 0.22 }}
        role="status">
        <span className="status-icone"><Icone size={20} aria-hidden /></span>
        <div>
          <strong>{NOME_DO_STATUS[resultado.status]}</strong>
          <p>{explicacao(algoritmo, resultado, fonte)}</p>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
