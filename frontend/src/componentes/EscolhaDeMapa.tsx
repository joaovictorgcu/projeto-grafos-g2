// [IA] Claude Code (Claude Opus 5.5) – página de escolha do mapa da Parte 1, com o envio do mapa surpresa
import { Upload } from "lucide-react";
import { motion } from "motion/react";
import { useRef, useState } from "react";
import type { ResumoDoMapa } from "../tipos";

const SELO = { enunciado: "", grupo: "do grupo", enviado: "enviado" };

export function EscolhaDeMapa({ mapas, aoEscolher, aoEnviar, enviando }: {
  mapas: ResumoDoMapa[]; aoEscolher: (id: string) => void; aoEnviar: (arquivo: File) => void; enviando: boolean;
}) {
  const entrada = useRef<HTMLInputElement>(null);
  const [arrastando, setArrastando] = useState(false);

  return (
    <main className="escolha">
      <motion.section className="escolha-cartao" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
        <h2>Escolha um mapa</h2>
        <ol className="escolha-lista">
          {mapas.map((m, i) => (
            <motion.li key={m.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.03 * i }}>
              <motion.button type="button" className="escolha-opcao" onClick={() => aoEscolher(m.id)} whileTap={{ scale: 0.98 }}>
                <span className="escolha-numero">{i + 1}</span>
                <span className="escolha-nome">{m.titulo}</span>
                {SELO[m.origem] && <span className={`selo selo-${m.origem}`}>{SELO[m.origem]}</span>}
              </motion.button>
            </motion.li>
          ))}
        </ol>

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
          <span className="dica">ou arraste o arquivo para cá. É por aqui que entra o mapa surpresa.</span>
          <input ref={entrada} type="file" accept=".txt,text/plain" hidden
            onChange={(ev) => {
              const arquivo = ev.target.files?.[0];
              if (arquivo) aoEnviar(arquivo);
              ev.target.value = "";
            }} />
        </div>
      </motion.section>
    </main>
  );
}
