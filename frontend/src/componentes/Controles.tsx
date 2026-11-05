// [IA] Claude Code (Claude Opus 5.5) – controles da animação: tocar/pausar, passo a passo, linha do tempo com marcos e velocidade
import { ChevronLeft, ChevronRight, Gauge, Pause, Play, SkipBack, SkipForward } from "lucide-react";
import { motion } from "motion/react";
import type { CSSProperties } from "react";
import { CORES_CHAVE } from "../modelo";
import type { Passo } from "../tipos";
import type { Reproducao } from "../usarReproducao";

export function Controles({ reproducao, ultimo, passos, cor, velocidadeMaxima = 30, rotulo = "passos/s" }: {
  reproducao: Reproducao; ultimo: number; passos?: Passo[]; cor: string; velocidadeMaxima?: number; rotulo?: string;
}) {
  const { passo, tocando, velocidade, setVelocidade, irPara, alternar } = reproducao;
  const desativado = ultimo === 0;
  const marcos = (passos ?? []).flatMap((p, i) =>
    p.novaChave ? [{ i, tipo: "chave", cor: CORES_CHAVE[p.novaChave], texto: `pega a chave ${p.novaChave}` }]
      : p.novoBonus !== null ? [{ i, tipo: "bonus", cor: "#10b981", texto: `usa o bônus ${p.novoBonus}` }] : [],
  );

  return (
    <div className="controles" style={{ "--cor": cor } as CSSProperties}>
      <div className="botoes">
        <button type="button" className="botao-icone" onClick={() => irPara(0)} disabled={desativado} aria-label="Voltar ao início">
          <SkipBack size={18} />
        </button>
        <button type="button" className="botao-icone" onClick={() => irPara(passo - 1)} disabled={desativado || passo === 0}
          aria-label="Voltar um passo">
          <ChevronLeft size={20} />
        </button>
        <motion.button type="button" className="botao-tocar" onClick={alternar} disabled={desativado}
          whileTap={{ scale: 0.92 }} aria-label={tocando ? "Pausar" : "Reproduzir"}>
          {tocando ? <Pause size={22} /> : <Play size={22} />}
        </motion.button>
        <button type="button" className="botao-icone" onClick={() => irPara(passo + 1)} disabled={desativado || passo === ultimo}
          aria-label="Avançar um passo">
          <ChevronRight size={20} />
        </button>
        <button type="button" className="botao-icone" onClick={() => irPara(ultimo)} disabled={desativado} aria-label="Ir ao fim">
          <SkipForward size={18} />
        </button>
      </div>

      <div className="linha-do-tempo">
        <div className="trilho">
          <motion.div className="trilho-cheio" initial={false} animate={{ width: `${ultimo ? (passo / ultimo) * 100 : 0}%` }}
            transition={{ duration: 0.15 }} />
          {marcos.map((m) => (
            <button key={m.i} type="button" className={`marco marco-${m.tipo}`} title={`passo ${m.i}: ${m.texto}`}
              aria-label={`Ir ao passo ${m.i}: ${m.texto}`}
              style={{ left: `${(m.i / Math.max(1, ultimo)) * 100}%`, "--cor-marco": m.cor } as CSSProperties}
              onClick={() => irPara(m.i)} />
          ))}
          <input type="range" min={0} max={Math.max(1, ultimo)} value={passo} disabled={desativado}
            onChange={(ev) => irPara(Number(ev.target.value))} aria-label="Linha do tempo do percurso" />
        </div>
        <span className="contador">{passo}<small>/{ultimo}</small></span>
      </div>

      <label className="velocidade">
        <Gauge size={16} aria-hidden />
        <input type="range" min={1} max={velocidadeMaxima} value={velocidade} onChange={(ev) => setVelocidade(Number(ev.target.value))}
          aria-label={`Velocidade em ${rotulo}`} />
        <span>{velocidade} {rotulo}</span>
      </label>
    </div>
  );
}
