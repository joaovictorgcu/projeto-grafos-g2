// [IA] Claude Code (Claude Opus 5.5) – escolhe a tela: início, Parte 1 ou Parte 2
import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";
import { Inicio } from "./componentes/Inicio";
import { Topo } from "./componentes/Topo";
import { Parte1 } from "./Parte1";
import { Parte2 } from "./Parte2";

type Tela = "inicio" | "parte1" | "parte2";

function telaInicial(): Tela {
  const parte = new URLSearchParams(window.location.search).get("parte");
  return parte === "1" ? "parte1" : parte === "2" ? "parte2" : "inicio";
}

export default function App() {
  const [tela, setTela] = useState<Tela>(telaInicial);

  function irPara(nova: Tela) {
    if (nova === "inicio") window.history.replaceState(null, "", window.location.pathname);
    setTela(nova);
    window.scrollTo({ top: 0 });
  }

  return (
    <AnimatePresence mode="wait">
      <motion.div key={tela} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}>
        {tela === "parte1" ? <Parte1 aoInicio={() => irPara("inicio")} />
          : tela === "parte2" ? <Parte2 aoInicio={() => irPara("inicio")} />
            : (
              <div className="app">
                <div className="fundo-animado" aria-hidden />
                <Topo aoInicio={() => irPara("inicio")} />
                <Inicio aoEscolher={irPara} />
              </div>
            )}
      </motion.div>
    </AnimatePresence>
  );
}
