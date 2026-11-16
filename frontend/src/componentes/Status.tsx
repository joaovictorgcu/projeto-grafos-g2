// faixa com o resultado do algoritmo: caminho, recusa, ciclo negativo ou sem solução
import { AnimatePresence, motion } from "motion/react";
import { NOME_DO_ALGORITMO, NOME_DO_STATUS } from "../modelo";
import { Cartao, type CorDoCartao } from "./Futebol";
import type { Algoritmo, Resultado } from "../tipos";

// cartão do árbitro para cada resultado: verde = caminho, amarelo = recusa, vermelho = ciclo negativo, azul = sem solução
export const CARTAO: Record<Resultado["status"], CorDoCartao> = { OK: "verde", RECUSA: "amarelo", CICLO_NEGATIVO: "vermelho", SEM_SOLUCAO: "azul" };

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
  return (
    <AnimatePresence mode="wait">
      <motion.div key={`${algoritmo}-${resultado.status}-${resultado.custo}`} className={`status status-${resultado.status.toLowerCase()}`}
        initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 8 }} transition={{ duration: 0.22 }}
        role="status">
        <Cartao cor={CARTAO[resultado.status]} className="cartao-grande" />
        <div>
          <strong>{NOME_DO_STATUS[resultado.status]}</strong>
          <p>{explicacao(algoritmo, resultado, fonte)}</p>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
