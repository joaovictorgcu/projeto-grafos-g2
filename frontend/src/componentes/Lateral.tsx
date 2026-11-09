// [IA] Claude Code (Claude Opus 5.5) – barra lateral: escolha do mapa, envio do mapa surpresa, algoritmo e opções de visualização
import { FileWarning, Layers, Skull, Sparkles, Upload, X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useRef, useState, type CSSProperties } from "react";
import { ALGORITMOS, NOME_DO_ALGORITMO, NOME_DO_STATUS, O_QUE_O_ALGORITMO_BUSCA, nomeDaCamada } from "../modelo";
import type { Algoritmo, DadosDoMapa, ResumoDoMapa } from "../tipos";
import { Miniatura } from "./Miniatura";

const NOME_DA_ORIGEM = { enunciado: "enunciado", grupo: "do grupo", enviado: "enviado" };

export function EscolhaDeMapa({ mapas, escolhido, aoEscolher, aoEnviar, enviando }: {
  mapas: ResumoDoMapa[]; escolhido: string; aoEscolher: (id: string) => void; aoEnviar: (arquivo: File) => void;
  enviando: boolean;
}) {
  const entrada = useRef<HTMLInputElement>(null);
  const [arrastando, setArrastando] = useState(false);

  return (
    <section className="secao-lateral">
      <h2>Mapa</h2>
      <div className="lista-mapas">
        {mapas.map((m, i) => (
          <motion.button key={m.id} type="button" className={m.id === escolhido ? "cartao-mapa ativo" : "cartao-mapa"}
            onClick={() => aoEscolher(m.id)} aria-pressed={m.id === escolhido}
            initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}
            whileHover={{ y: -2 }} whileTap={{ scale: 0.97 }}>
            <Miniatura grade={m.grade} />
            <span className="cartao-mapa-texto">
              <span className="cartao-mapa-titulo">{m.titulo}</span>
              {m.origem !== "enunciado" && <span className={`selo selo-${m.origem}`}>{NOME_DA_ORIGEM[m.origem]}</span>}
            </span>
            {m.id === escolhido && <motion.span layoutId="mapa-ativo" className="mapa-ativo-borda" />}
          </motion.button>
        ))}
      </div>

      <div className={arrastando ? "zona-envio arrastando" : "zona-envio"}
        onDragOver={(ev) => { ev.preventDefault(); setArrastando(true); }}
        onDragLeave={() => setArrastando(false)}
        onDrop={(ev) => {
          ev.preventDefault();
          setArrastando(false);
          const arquivo = ev.dataTransfer.files[0];
          if (arquivo) aoEnviar(arquivo);
        }}>
        <button type="button" className="botao-envio" onClick={() => entrada.current?.click()} disabled={enviando}>
          <Upload size={18} aria-hidden />
          {enviando ? "Analisando…" : "Enviar um mapa .txt"}
        </button>
        <span className="dica">ou arraste o arquivo aqui · é por aqui que entra o mapa surpresa</span>
        <input ref={entrada} type="file" accept=".txt,text/plain" hidden
          onChange={(ev) => {
            const arquivo = ev.target.files?.[0];
            if (arquivo) aoEnviar(arquivo);
            ev.target.value = "";
          }} />
      </div>

    </section>
  );
}

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

export function EscolhaDeAlgoritmo({ dados, algoritmo, aoEscolher }: {
  dados: DadosDoMapa | null; algoritmo: Algoritmo; aoEscolher: (a: Algoritmo) => void;
}) {
  return (
    <section className="secao-lateral">
      <h2>Algoritmo</h2>
      <div className="lista-algoritmos" role="radiogroup" aria-label="Algoritmo">
        {ALGORITMOS.map((a) => {
          const status = dados?.algoritmos[a].status;
          return (
            <button key={a} type="button" role="radio" aria-checked={a === algoritmo}
              className={a === algoritmo ? "opcao-algoritmo ativa" : "opcao-algoritmo"} onClick={() => aoEscolher(a)}>
              {a === algoritmo && <motion.span layoutId="algoritmo-ativo" className="opcao-fundo"
                transition={{ type: "spring", stiffness: 420, damping: 34 }} />}
              <span className="opcao-nome">{NOME_DO_ALGORITMO[a]}</span>
              <span className="opcao-descricao">{O_QUE_O_ALGORITMO_BUSCA[a]}</span>
              {status && <span className={`ponto-status status-${status.toLowerCase()}`} title={NOME_DO_STATUS[status]} />}
            </button>
          );
        })}
      </div>
    </section>
  );
}

export function InterruptorDaFonte({ dados, fonte, setFonte }: {
  dados: DadosDoMapa | null; fonte: boolean; setFonte: (v: boolean) => void;
}) {
  const temFonte = dados?.grade.some((linha) => linha.includes("*")) ?? false;
  return (
    <label className={temFonte ? "interruptor" : "interruptor desativado"}
      title={temFonte ? undefined : "este mapa não tem fonte *"}>
      <input type="checkbox" checked={fonte} disabled={!temFonte} onChange={(ev) => setFonte(ev.target.checked)} />
      <span className="interruptor-trilho" aria-hidden />
      <Sparkles size={16} aria-hidden />
      <span>Fonte consumível <small>(* vale −2 só uma vez)</small></span>
    </label>
  );
}

export function Opcoes({ dados, fonte, setFonte, camada, setCamada, armadilhas, setArmadilhas, coresDasCamadas }: {
  dados: DadosDoMapa | null; fonte: boolean; setFonte: (v: boolean) => void;
  camada: string | null; setCamada: (c: string | null) => void; armadilhas: boolean; setArmadilhas: (v: boolean) => void;
  coresDasCamadas: { chaves: string; estados: number; cor: string }[];
}) {
  return (
    <section className="secao-lateral">
      <h2>Visualização</h2>
      <label className="interruptor">
        <input type="checkbox" checked={armadilhas} onChange={(ev) => setArmadilhas(ev.target.checked)} />
        <span className="interruptor-trilho" aria-hidden />
        <Skull size={16} aria-hidden />
        <span>Destacar estados-armadilha</span>
      </label>

      <InterruptorDaFonte dados={dados} fonte={fonte} setFonte={setFonte} />

      <div className="camadas-escolha">
        <span className="rotulo-pequeno"><Layers size={14} aria-hidden /> camada em destaque</span>
        <div className="chips">
          <button type="button" className={camada === null ? "chip ativo" : "chip"} onClick={() => setCamada(null)}>
            seguir o jogador
          </button>
          {coresDasCamadas.map((c) => (
            <button key={c.chaves || "-"} type="button" className={camada === c.chaves ? "chip ativo" : "chip"}
              style={{ "--cor": c.cor } as CSSProperties} onClick={() => setCamada(c.chaves)}
              title={`${c.estados} estados nesta camada`}>
              <i className="ponto" style={{ background: c.cor }} />
              {nomeDaCamada(c.chaves)}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
