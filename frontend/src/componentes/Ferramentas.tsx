// [IA] Claude Code (Claude Opus 5.5) – barra de ferramentas acima do tabuleiro: algoritmo, fonte consumível, armadilhas, camada e aviso de mapa inválido
import { FileWarning, X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import type { CSSProperties } from "react";
import { ALGORITMOS, NOME_DO_ALGORITMO, NOME_DO_STATUS, nomeDaCamada } from "../modelo";
import type { Algoritmo, DadosDoMapa } from "../tipos";

export function AvisoDeErro({ erro, limparErro }: { erro: string | null; limparErro: () => void }) {
  return (
    <div className="avisos">
      <AnimatePresence>
        {erro && (
          <motion.div className="erro-mapa" role="alert" initial={{ opacity: 0, x: 0 }}
            animate={{ opacity: 1, x: [0, -8, 8, -5, 5, 0] }} exit={{ opacity: 0, y: -12 }} transition={{ duration: 0.45 }}>
            <FileWarning size={20} aria-hidden />
            <div>
              <strong>Mapa inválido</strong>
              <p>{erro}</p>
            </div>
            <button type="button" className="botao-icone pequeno" onClick={limparErro} aria-label="Fechar aviso">
              <X size={16} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function Interruptor({ ligado, aoMudar, texto, desativado, dica }: {
  ligado: boolean; aoMudar: (v: boolean) => void; texto: string; desativado?: boolean; dica?: string;
}) {
  return (
    <label className={desativado ? "interruptor desativado" : "interruptor"} title={dica}>
      <input type="checkbox" checked={ligado} disabled={desativado} onChange={(ev) => aoMudar(ev.target.checked)} />
      <span className="interruptor-trilho" aria-hidden />
      <span>{texto}</span>
    </label>
  );
}

export function Ferramentas({ dados, algoritmo, setAlgoritmo, mostrarAlgoritmo, fonte, setFonte, armadilhas, setArmadilhas, camada, setCamada, camadas }: {
  dados: DadosDoMapa; algoritmo: Algoritmo; setAlgoritmo: (a: Algoritmo) => void; mostrarAlgoritmo: boolean;
  fonte: boolean; setFonte: (v: boolean) => void;
  armadilhas?: boolean; setArmadilhas?: (v: boolean) => void;
  camada?: string | null; setCamada?: (c: string | null) => void; camadas?: { chaves: string; estados: number; cor: string }[];
}) {
  const temFonte = dados.grade.some((linha) => linha.includes("*"));
  return (
    <div className="ferramentas">
      {mostrarAlgoritmo && (
        <div className="segmentado" role="radiogroup" aria-label="Algoritmo">
          {ALGORITMOS.map((a) => {
            const status = dados.algoritmos[a].status;
            return (
              <button key={a} type="button" role="radio" aria-checked={a === algoritmo} className={a === algoritmo ? "ativo" : ""}
                onClick={() => setAlgoritmo(a)} title={NOME_DO_STATUS[status]}>
                {a === algoritmo && <motion.span layoutId="algoritmo-ativo" className="segmentado-fundo" />}
                <span>{NOME_DO_ALGORITMO[a]}</span>
                <span className={`ponto-status status-${status.toLowerCase()}`} />
              </button>
            );
          })}
        </div>
      )}
      <Interruptor ligado={fonte} aoMudar={setFonte} texto="Fonte consumível" desativado={!temFonte}
        dica={temFonte ? "a fonte * vale −2 só na primeira passagem" : "este mapa não tem fonte *"} />
      {setArmadilhas && <Interruptor ligado={!!armadilhas} aoMudar={setArmadilhas} texto="Destacar armadilhas" />}
      {setCamada && camadas && (
        <div className="chips" aria-label="Camada em destaque">
          <button type="button" className={camada === null ? "chip ativo" : "chip"} onClick={() => setCamada(null)}>seguir o jogador</button>
          {camadas.map((c) => (
            <button key={c.chaves || "-"} type="button" className={camada === c.chaves ? "chip ativo" : "chip"}
              style={{ "--cor": c.cor } as CSSProperties} onClick={() => setCamada(c.chaves)} title={`${c.estados} estados nesta camada`}>
              <i className="ponto" style={{ background: c.cor }} />
              {nomeDaCamada(c.chaves)}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
