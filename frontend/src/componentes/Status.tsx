// [IA] Claude Code (Claude Opus 5.5) – faixa com o resultado do algoritmo; textos da função explicacao revisados com auxílio do ChatGPT.
import { AnimatePresence, motion } from "motion/react";
import { NOME_DO_ALGORITMO, NOME_DO_STATUS } from "../modelo";
import { Cartao, type CorDoCartao } from "./Futebol";
import type { Algoritmo, Resultado } from "../tipos";

// cartão do árbitro para cada resultado: verde = caminho, amarelo = recusa, vermelho = ciclo negativo, azul = sem solução
export const CARTAO: Record<Resultado["status"], CorDoCartao> = { OK: "verde", RECUSA: "amarelo", CICLO_NEGATIVO: "vermelho", SEM_SOLUCAO: "azul" };

function explicacao(algoritmo: Algoritmo, r: Resultado, fonte: boolean) {
  const nome = NOME_DO_ALGORITMO[algoritmo];
  if (r.status === "OK") {
    return `${nome} conseguiu encontrar um caminho até a saída G. Foram ${r.passos} passos, com custo total de ${r.custo}.`;
  }
  if (r.status === "RECUSA") {
    return `${nome} recusou a busca porque o grafo tem arcos com peso negativo, como os de bônus (+) e fonte (*). O Bellman-Ford aceita pesos negativos.`;
  }
  if (r.status === "CICLO_NEGATIVO") {
    return `O algoritmo encontrou um ciclo negativo: cada volta reduz o custo, então não existe menor custo definido.${fonte ? "" : " Se o mapa tiver fonte (*), tente ativar a opção de fonte consumível."}`;
  }
  return "Não foi possível encontrar um caminho entre o início S e a saída G. O destino não pode ser alcançado nesse mapa.";
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
