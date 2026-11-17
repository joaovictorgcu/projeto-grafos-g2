// mostra as notas analíticas escritas pelo grupo (negrito e código do markdown, tabelas e os trechos "Insight", "Por que esse gráfico")
import { Fragment } from "react";
import type { BlocoDaNota } from "../tipos";
import { Rosto } from "./Pixel";

export function TextoEmLinha({ texto }: { texto: string }) {
  const partes = texto.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return (
    <>
      {partes.map((parte, i) => parte.startsWith("**") ? <b key={i}>{parte.slice(2, -2)}</b>
        : parte.startsWith("`") ? <code key={i}>{parte.slice(1, -1)}</code>
          : <Fragment key={i}>{parte}</Fragment>)}
    </>
  );
}

function Trecho({ titulo, children }: { titulo?: string; children: React.ReactNode }) {
  return (
    <section className="nota-trecho">
      <Rosto camisa="#1a6b3c" tamanho={34} />
      <div className="balao">
        {titulo && <h5>{titulo}</h5>}
        {children}
      </div>
    </section>
  );
}

const maiuscula = (t: string) => t.charAt(0).toUpperCase() + t.slice(1);

const ROTULOS = ["De onde nasceu", "Insight", "Por que esse gráfico"];

// Nota da Parte 2: um parágrafo só, com "Insight:", "Por que esse gráfico:" etc. no meio do texto
export function NotaCorrida({ texto }: { texto: string }) {
  const padrao = new RegExp(`(${ROTULOS.join("|")}):`, "g");
  const pedacos = texto.split(padrao);
  const trechos: { titulo: string; texto: string }[] = [{ titulo: "O que mostra", texto: pedacos[0].trim() }];
  for (let i = 1; i < pedacos.length; i += 2) trechos.push({ titulo: pedacos[i], texto: maiuscula(pedacos[i + 1].trim()) });
  return (
    <div className="nota">
      {trechos.filter((t) => t.texto).map((t) => (
        <Trecho key={t.titulo} titulo={t.titulo}><p><TextoEmLinha texto={t.texto} /></p></Trecho>
      ))}
    </div>
  );
}

// Nota da Parte 1: blocos do markdown; cada "**Título.**" no começo de um parágrafo abre um trecho novo
export function NotaEmBlocos({ blocos }: { blocos: BlocoDaNota[] }) {
  const trechos: { titulo?: string; blocos: BlocoDaNota[] }[] = [];
  for (const bloco of blocos) {
    const titulo = bloco.tipo === "paragrafo" ? /^\*\*([^*]+?)\.\*\*\s*/.exec(bloco.texto) : null;
    if (titulo && bloco.tipo === "paragrafo") {
      trechos.push({ titulo: titulo[1], blocos: [{ tipo: "paragrafo", texto: bloco.texto.slice(titulo[0].length) }] });
    } else if (trechos.length) {
      trechos[trechos.length - 1].blocos.push(bloco);
    } else {
      trechos.push({ blocos: [bloco] });
    }
  }
  return (
    <div className="nota">
      {trechos.map((t, i) => (
        <Trecho key={i} titulo={t.titulo}>
          {t.blocos.map((b, j) => b.tipo === "paragrafo" ? <p key={j}><TextoEmLinha texto={b.texto} /></p> : (
            <table key={j} className="nota-tabela">
              <thead><tr>{b.linhas[0].map((c) => <th key={c}>{c}</th>)}</tr></thead>
              <tbody>{b.linhas.slice(1).map((linha, k) => <tr key={k}>{linha.map((c, m) => <td key={m}><TextoEmLinha texto={c} /></td>)}</tr>)}</tbody>
            </table>
          ))}
        </Trecho>
      ))}
    </div>
  );
}
