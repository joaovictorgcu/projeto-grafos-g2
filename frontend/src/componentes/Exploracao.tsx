// [IA] Claude Code (Claude Opus 5.5) – aba Exploração: os quatro algoritmos visitando o labirinto ao mesmo tempo, com expandidas, fronteira e o caminho achado
import { motion } from "motion/react";
import { useMemo } from "react";
import { chave } from "../modelo";
import type { DadosDoMapa, Expansao } from "../tipos";
import { usarReproducao } from "../usarReproducao";
import { Controles } from "./Controles";
import { Itens, Marcos, Terreno } from "./Tabuleiro";

type Situacao = 1 | 2 | 3;

interface Quadro {
  situacao: Map<number, Situacao>;
  expandidas: number;
  fronteira: number;
  terminou: boolean;
}

interface Busca {
  id: string;
  titulo: string;
  estrutura: string;
  explicacao: string;
  ultimo: number;
  achou: boolean;
  caminho: number[];
  aviso?: string;
  quadro: (k: number) => Quadro;
}

const COR = { 1: "var(--expandida)", 2: "var(--fronteira)", 3: "var(--atual)" };

function buscaPorExpansao(b: Expansao): Pick<Busca, "ultimo" | "achou" | "caminho" | "quadro"> {
  const ultimo = b.alvo ?? b.ordem.length - 1;
  return {
    ultimo,
    achou: b.alvo !== null,
    caminho: b.caminho,
    quadro: (k) => {
      const ate = Math.min(k, ultimo);
      const situacao = new Map<number, Situacao>();
      for (let i = 0; i < ate; i++) situacao.set(b.ordem[i], 1);
      let fronteira = 0;
      for (let i = ate + 1; i < b.ordem.length; i++) {
        if (b.descoberta[i] >= 0 && b.descoberta[i] <= ate) {
          situacao.set(b.ordem[i], 2);
          fronteira++;
        }
      }
      situacao.set(b.ordem[ate], 3);
      return { situacao, expandidas: ate + 1, fronteira, terminou: k >= ultimo };
    },
  };
}

function buscaEmProfundidade(dados: DadosDoMapa): Pick<Busca, "ultimo" | "achou" | "caminho" | "quadro"> {
  const b = dados.buscas.DFS;
  const ultimo = b.alvo ?? b.eventos.length - 1;
  return {
    ultimo,
    achou: b.alvo !== null,
    caminho: b.caminho,
    quadro: (k) => {
      const situacao = new Map<number, Situacao>();
      const pilha: number[] = [];
      let expandidas = 0;
      for (let i = 0; i <= Math.min(k, ultimo); i++) {
        const [estado, evento] = b.eventos[i];
        if (evento === 0) {
          pilha.push(estado);
          expandidas++;
          situacao.set(estado, 2);
        } else {
          pilha.pop();
          situacao.set(estado, 1);
        }
      }
      if (pilha.length) situacao.set(pilha[pilha.length - 1], 3);
      return { situacao, expandidas, fronteira: pilha.length, terminou: k >= ultimo };
    },
  };
}

function custoDoCaminho(dados: DadosDoMapa, caminho: number[]) {
  const peso = new Map(dados.arcos.map(([u, v, p]) => [`${u}-${v}`, p]));
  return caminho.slice(1).reduce((total, v, i) => total + (peso.get(`${caminho[i]}-${v}`) ?? 0), 0);
}

function PainelDeBusca({ dados, busca, k }: { dados: DadosDoMapa; busca: Busca; k: number }) {
  const grade = dados.grade;
  const altura = grade.length;
  const largura = grade[0]?.length ?? 0;
  const quadro = busca.aviso ? null : busca.quadro(k);
  const celulas = new Map<string, Situacao>();
  quadro?.situacao.forEach((s, i) => {
    const e = dados.estados[i];
    const k2 = chave(e.l, e.c);
    if ((celulas.get(k2) ?? 0) < s) celulas.set(k2, s);
  });
  const pontos = busca.caminho.map((i) => `${dados.estados[i].c + 0.5},${dados.estados[i].l + 0.5}`).join(" ");
  const pronto = quadro?.terminou && busca.achou;

  return (
    <section className="painel-busca">
      <header>
        <div>
          <h3>{busca.titulo} <span>({busca.estrutura})</span></h3>
          <p>{busca.explicacao}</p>
        </div>
        {quadro && <span className="expandidas">expandidas: <b>{quadro.expandidas}</b></span>}
      </header>
      <div className="busca-quadro">
        <svg viewBox={`0 0 ${largura} ${altura}`} className="tabuleiro-busca" role="img"
          aria-label={`${busca.titulo} em ${dados.titulo}: ${quadro?.expandidas ?? 0} estados expandidos`}>
          <Terreno grade={grade} />
          {[...celulas].map(([k2, s]) => {
            const [l, c] = k2.split(",").map(Number);
            return <rect key={k2} x={c} y={l} width={1} height={1} fill={COR[s]} className={s === 3 ? "celula-busca atual" : "celula-busca"} />;
          })}
          <Itens dados={dados} chaves="" bonus={[]} animar={false} />
          <Marcos grade={grade} />
          {pronto && pontos && (
            <motion.polyline points={pontos} className="caminho-achado" initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
              transition={{ duration: 1.1, ease: "easeInOut" }} />
          )}
        </svg>
        {busca.aviso && <div className="busca-aviso">{busca.aviso}</div>}
      </div>
      <footer>
        {busca.aviso ? <span>não rodou</span>
          : !quadro?.terminou ? <span>fronteira: {quadro?.fronteira} · procurando o G…</span>
            : busca.achou ? <span className="achou">achou o G · caminho de {busca.caminho.length - 1} passos, custo {custoDoCaminho(dados, busca.caminho)}</span>
              : <span className="esgotou">explorou tudo e não chegou ao G</span>}
      </footer>
    </section>
  );
}

export function Exploracao({ dados }: { dados: DadosDoMapa }) {
  const buscas = useMemo<Busca[]>(() => {
    const dij = dados.buscas.DIJKSTRA;
    const bf = dados.buscas.BELLMAN_FORD;
    const vazia = { ultimo: 0, achou: false, caminho: [], quadro: () => ({ situacao: new Map(), expandidas: 0, fronteira: 0, terminou: true }) };
    return [
      { id: "dfs", titulo: "DFS", estrutura: "pilha", explicacao: "vai até o fundo de um corredor antes de voltar", ...buscaEmProfundidade(dados) },
      { id: "bfs", titulo: "BFS", estrutura: "fila", explicacao: "expande por níveis: primeiro tudo a 1 passo, depois a 2…", ...buscaPorExpansao(dados.buscas.BFS) },
      "recusa" in dij
        ? { id: "dij", titulo: "Dijkstra", estrutura: "fila de prioridade", explicacao: "expande sempre o estado mais barato", ...vazia,
          aviso: "Recusou: o mapa tem arco de peso negativo." }
        : { id: "dij", titulo: "Dijkstra", estrutura: "fila de prioridade", explicacao: "expande sempre o estado mais barato", ...buscaPorExpansao(dij) },
      "ciclo" in bf
        ? { id: "bf", titulo: "Bellman-Ford", estrutura: "rodadas de relaxação", explicacao: "relaxa todos os arcos |V|−1 vezes", ...vazia,
          aviso: `Ciclo negativo de custo ${bf.ciclo}: não há caminho de menor custo.` }
        : { id: "bf", titulo: "Bellman-Ford", estrutura: "rodadas de relaxação",
          explicacao: "não expande um estado por vez; aqui eles aparecem na ordem do custo final", ...buscaPorExpansao(bf) },
    ];
  }, [dados]);
  const ultimo = Math.max(0, ...buscas.map((b) => b.ultimo));
  const reproducao = usarReproducao(ultimo, `${dados.id}|${dados.fonte_consumivel}`, true, Math.max(8, Math.round(ultimo / 12)));

  return (
    <div className="exploracao">
      <div className="legenda-busca">
        <span><i style={{ background: "var(--expandida)" }} />já expandido</span>
        <span><i style={{ background: "var(--fronteira)" }} />na fronteira (pilha, fila ou heap)</span>
        <span><i style={{ background: "var(--atual)" }} />sendo expandido agora</span>
        <span><i className="legenda-inicio" />início S</span>
        <span><i className="legenda-saida" />saída G</span>
        <span><i style={{ background: "var(--caminho)" }} />caminho achado</span>
      </div>
      <div className="grade-buscas">
        {buscas.map((b) => <PainelDeBusca key={b.id} dados={dados} busca={b} k={reproducao.passo} />)}
      </div>
      <Controles reproducao={reproducao} ultimo={ultimo} cor="#ff5a00" velocidadeMaxima={240} rotulo="expansões/s" />
    </div>
  );
}
