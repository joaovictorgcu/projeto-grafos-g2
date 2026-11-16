// galeria das figuras: índice agrupado à esquerda, uma figura grande por vez com a nota do grupo, ← → para navegar e clique para ampliar
import { ChevronLeft, ChevronRight, Maximize2, X } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState, type ReactNode } from "react";

export interface ItemDaGaleria {
  id: string;
  codigo: string;
  titulo: string;
  subtitulo: string;
  src: string;
  nota: ReactNode;
}

export interface GrupoDaGaleria {
  nome: string;
  itens: ItemDaGaleria[];
}

const TITULOS: Record<string, string> = {
  graus: "Graus", pesos: "Pesos", faltantes: "Dados faltantes", relacoes: "Relações", outliers: "Outliers",
  explanatoria_caminho: "Caminho de menor custo", explanatoria_ligas: "Ligas de destino",
  tempos: "Tempos", escalabilidade: "Escalabilidade", camadas_bfs: "Camadas da BFS", caminhos: "Caminhos do Dijkstra",
  percurso_m03: "Percurso no m03", percurso_m08: "Percurso no m08", camadas_m02: "Camadas do m02",
  arvore_bfs_m02: "Árvore da BFS no m02", multiplicidade_m08: "Multiplicidade no m08",
};

export function tituloDoArquivo(arquivo: string) {
  const base = arquivo.replace(/\.png$/, "").replace(/^[a-z]\d_/, "");
  if (TITULOS[base]) return TITULOS[base];
  const nome = base.replace(/_/g, " ");
  return nome.charAt(0).toUpperCase() + nome.slice(1);
}

export function Galeria({ grupos }: { grupos: GrupoDaGaleria[] }) {
  const itens = grupos.flatMap((g) => g.itens);
  const [indice, setIndice] = useState(0);
  const [ampliada, setAmpliada] = useState(false);
  const atual = itens[Math.min(indice, itens.length - 1)];

  useEffect(() => {
    function tecla(ev: KeyboardEvent) {
      const alvo = ev.target as HTMLElement;
      if (alvo.closest("input, textarea, select")) return;
      if (ev.key === "Escape") setAmpliada(false);
      if (ev.key === "ArrowRight") setIndice((i) => Math.min(itens.length - 1, i + 1));
      if (ev.key === "ArrowLeft") setIndice((i) => Math.max(0, i - 1));
    }
    window.addEventListener("keydown", tecla);
    return () => window.removeEventListener("keydown", tecla);
  }, [itens.length]);

  if (!atual) return <div className="carregando">Nenhuma figura em out/.</div>;

  return (
    <div className="galeria">
      <nav className="galeria-indice" aria-label="Figuras">
        {grupos.map((grupo) => (
          <div key={grupo.nome} className="galeria-grupo">
            <h4>{grupo.nome}</h4>
            <ol>
              {grupo.itens.map((item) => {
                const i = itens.indexOf(item);
                return (
                  <li key={item.id}>
                    <button type="button" className={i === indice ? "ativo" : ""} onClick={() => setIndice(i)} aria-current={i === indice ? "true" : undefined}>
                      <span className="galeria-codigo">{item.codigo}</span>
                      <span className="galeria-nome">{item.titulo}</span>
                    </button>
                  </li>
                );
              })}
            </ol>
          </div>
        ))}
      </nav>

      <article className="galeria-palco">
        <header className="galeria-topo">
          <div>
            <span className="rotulo-pequeno"><b className="galeria-numero">{atual.codigo}</b> {atual.subtitulo}</span>
            <h3>{atual.titulo}</h3>
          </div>
          <div className="galeria-setas">
            <span className="galeria-posicao">{indice + 1}/{itens.length}</span>
            <button type="button" className="botao-icone" onClick={() => setIndice(indice - 1)} disabled={indice === 0} aria-label="Figura anterior"><ChevronLeft size={18} /></button>
            <button type="button" className="botao-icone" onClick={() => setIndice(indice + 1)} disabled={indice === itens.length - 1} aria-label="Próxima figura"><ChevronRight size={18} /></button>
          </div>
        </header>
        <AnimatePresence mode="wait">
          <motion.div key={atual.id} className="galeria-conteudo" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.15 }}>
            <button type="button" className="galeria-imagem" onClick={() => setAmpliada(true)} aria-label={`Ampliar ${atual.titulo}`}>
              <img src={atual.src} alt={`${atual.codigo}: ${atual.titulo}`} />
              <span className="galeria-ampliar"><Maximize2 size={14} aria-hidden /> ampliar</span>
            </button>
            {atual.nota}
          </motion.div>
        </AnimatePresence>
      </article>

      <AnimatePresence>
        {ampliada && (
          <motion.div className="visor" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setAmpliada(false)}
            role="dialog" aria-modal="true" aria-label={atual.titulo}>
            <button type="button" className="botao-icone visor-fechar" onClick={() => setAmpliada(false)} aria-label="Fechar"><X size={18} /></button>
            <img src={atual.src} alt={`${atual.codigo}: ${atual.titulo}`} onClick={(ev) => ev.stopPropagation()} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
