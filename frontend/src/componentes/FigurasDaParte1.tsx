// [IA] Claude Code (Claude Opus 5.5) – aba Visualizações da Parte 1: as figuras de out/parte1/ com as notas de docs/parte1/notas_visualizacoes.md
import { useEffect, useState } from "react";
import { carregarFigurasDaParte1 } from "../api";
import type { FiguraDaParte1 } from "../tipos";
import { Carregando } from "./Futebol";
import { Galeria, tituloDoArquivo, type GrupoDaGaleria } from "./Galeria";
import { NotaEmBlocos } from "./TextoDaNota";

const GRUPOS: [string, RegExp][] = [["Percursos", /^percurso/], ["Grafo de estados", /./]];

export function FigurasDaParte1() {
  const [figuras, setFiguras] = useState<FiguraDaParte1[] | null>(null);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    carregarFigurasDaParte1().then(setFiguras).catch((e: Error) => setErro(e.message));
  }, []);

  if (erro) return <div className="carregando">{erro}</div>;
  if (!figuras) return <Carregando texto="Carregando as figuras…" />;

  const restantes = [...figuras];
  const grupos: GrupoDaGaleria[] = GRUPOS.map(([nome, padrao]) => {
    const deste = restantes.filter((f) => padrao.test(f.arquivo));
    deste.forEach((f) => restantes.splice(restantes.indexOf(f), 1));
    return {
      nome,
      itens: deste.map((f) => ({
        id: f.arquivo, codigo: f.codigo, titulo: tituloDoArquivo(f.arquivo), subtitulo: f.tipo || f.arquivo,
        src: `/parte1/${f.arquivo}`, nota: f.blocos.length ? <NotaEmBlocos blocos={f.blocos} /> : null,
      })),
    };
  }).filter((g) => g.itens.length);
  return <Galeria grupos={grupos} />;
}
