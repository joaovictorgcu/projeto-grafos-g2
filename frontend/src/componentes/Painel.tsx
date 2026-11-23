// [IA] Claude Code (Claude Opus 5.5) – painel do passo atual: rótulo do estado, posição, chaves, bônus e custo acumulado
import { Gem, KeyRound, MapPin, Skull } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import type { CSSProperties } from "react";
import { CORES_CHAVE } from "../modelo";
import type { DadosDoMapa, Passo } from "../tipos";
import { GraficoCusto } from "./GraficoCusto";
import { NumeroAnimado } from "./NumeroAnimado";

export function Painel({ dados, passos, passo, cor }: {
  dados: DadosDoMapa; passos: Passo[]; passo: number; cor: string;
}) {
  const atual = passos[passo];
  const e = atual.estado;
  const totalDeBonus = dados.bonus.length;

  return (
    <aside className="painel" aria-label="Estado do jogador">
      <section className="cartao estado-cartao">
        <span className="rotulo-pequeno">estado atual</span>
        <div className="rotulo-estado" aria-live="polite">
          <span className="parte-posicao">({e.l},{e.c})</span>
          <span className="separador">|</span>
          <span className="parte-chaves">{e.chaves || "-"}</span>
          <span className="separador">|</span>
          <span className="parte-bonus">{`{${e.bonus.join(",")}}`}</span>
        </div>
        <div className="legenda-rotulo">
          <span><i className="ponto parte-posicao-fundo" />posição</span>
          <span><i className="ponto parte-chaves-fundo" />chaves</span>
          <span><i className="ponto parte-bonus-fundo" />bônus usados</span>
        </div>
      </section>

      <section className="cartao custo-cartao" style={{ "--cor": cor } as CSSProperties}>
        <span className="rotulo-pequeno">custo acumulado</span>
        <div className="custo-linha">
          <NumeroAnimado valor={atual.total} className="custo-numero" />
          <AnimatePresence mode="popLayout">
            {passo > 0 && (
              <motion.span key={passo} className={atual.delta < 0 ? "delta negativo" : atual.delta > 1 ? "delta caro" : "delta"}
                initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.18 }}>
                {atual.delta > 0 ? `+${atual.delta}` : `−${Math.abs(atual.delta)}`}
              </motion.span>
            )}
          </AnimatePresence>
        </div>
        <span className="passo-texto">passo {passo} de {passos.length - 1}</span>
        <GraficoCusto compacto altura={56} passo={passo} series={[{ nome: "custo", cor, custos: passos.map((p) => p.total) }]} />
      </section>

      <section className="cartao">
        <div className="linha-info">
          <MapPin size={18} aria-hidden />
          <span>linha <b>{e.l}</b>, coluna <b>{e.c}</b></span>
        </div>
        <span className="rotulo-pequeno">chaves</span>
        <div className="slots">
          {dados.chaves.length === 0 && <span className="vazio">este mapa não tem chaves</span>}
          {dados.chaves.map((k) => {
            const tem = e.chaves.includes(k);
            return (
              <motion.span key={k} className={tem ? "slot cheio" : "slot"} style={{ "--cor": CORES_CHAVE[k] } as CSSProperties}
                animate={tem ? { scale: [1, 1.25, 1] } : { scale: 1 }} transition={{ duration: 0.4 }}
                title={tem ? `tem a chave ${k}` : `ainda não tem a chave ${k}`}>
                <KeyRound size={16} aria-hidden />
                {k}
              </motion.span>
            );
          })}
        </div>
        <span className="rotulo-pequeno">bônus</span>
        <div className="slots">
          {totalDeBonus === 0 && <span className="vazio">este mapa não tem bônus</span>}
          {dados.bonus.map(([, , i]) => {
            const usado = e.bonus.includes(i);
            return (
              <motion.span key={i} className={usado ? "slot cheio gema-slot" : "slot gema-slot"}
                animate={usado ? { scale: [1, 1.25, 1] } : { scale: 1 }} transition={{ duration: 0.4 }}
                title={usado ? `bônus ${i} já usado (valeu −4)` : `bônus ${i} ainda não usado`}>
                <Gem size={16} aria-hidden />
                {i}
              </motion.span>
            );
          })}
        </div>
      </section>

      <AnimatePresence>
        {e.armadilha && (
          <motion.section className="cartao alerta-armadilha" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}>
            <Skull size={18} aria-hidden />
            <span>Estado-armadilha: daqui não dá mais para chegar no G.</span>
          </motion.section>
        )}
      </AnimatePresence>
    </aside>
  );
}
