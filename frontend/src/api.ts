// [IA] Claude Code (Claude Opus 5.5) – chamadas ao servidor Python, com cache para não recalcular o mesmo mapa
import type { AlgoritmoDaParte2, DadosDaParte2, DadosDoMapa, FiguraDaParte1, GrafoDaParte2, ResumoDoGrafoDaParte2, ResumoDoMapa, RotaDaParte2 } from "./tipos";

const guardados = new Map<string, Promise<DadosDoMapa>>();

const SERVIDOR_ANTIGO = "O servidor que está rodando é de uma versão antiga. Feche-o com Ctrl+C no terminal e rode de novo: python -m src.servidor";

async function lerResposta<T>(resposta: Response): Promise<T> {
  if (!(resposta.headers.get("Content-Type") ?? "").includes("json")) throw new Error(SERVIDOR_ANTIGO);
  const corpo = await resposta.json().catch(() => ({ erro: `o servidor respondeu ${resposta.status}` }));
  if (!resposta.ok) throw new Error(corpo.erro ?? `o servidor respondeu ${resposta.status}`);
  return corpo as T;
}

export async function listarMapas(): Promise<ResumoDoMapa[]> {
  return lerResposta(await fetch("/api/mapas"));
}

export function carregarMapa(id: string, fonte: boolean): Promise<DadosDoMapa> {
  const chave = `${id}|${fonte}`;
  if (!guardados.has(chave)) {
    const pedido = fetch(`/api/mapas/${encodeURIComponent(id)}?fonte=${fonte ? 1 : 0}`).then((r) => lerResposta<DadosDoMapa>(r));
    pedido.catch(() => guardados.delete(chave));
    guardados.set(chave, pedido);
  }
  return guardados.get(chave)!;
}

export async function analisarTexto(texto: string, nome: string, fonte: boolean): Promise<DadosDoMapa> {
  const resposta = await fetch(`/api/analisar?nome=${encodeURIComponent(nome)}&fonte=${fonte ? 1 : 0}`, {
    method: "POST",
    headers: { "Content-Type": "text/plain; charset=utf-8" },
    body: texto,
  });
  return lerResposta(resposta);
}

export async function carregarParte2(): Promise<DadosDaParte2> {
  return lerResposta(await fetch("/api/parte2"));
}

export async function carregarFigurasDaParte1(): Promise<FiguraDaParte1[]> {
  return lerResposta(await fetch("/api/parte1/figuras"));
}

// [IA] Claude Code (Claude Opus 5.5) – grafo interativo da Visão geral da Parte 2
export async function carregarGrafoDaParte2(): Promise<ResumoDoGrafoDaParte2> {
  return lerResposta(await fetch("/api/parte2/grafo"));
}

export async function calcularRota(grafo: GrafoDaParte2, alg: AlgoritmoDaParte2, origem: number, destino: number, temporada?: number): Promise<RotaDaParte2> {
  const busca = new URLSearchParams({ grafo, alg, origem: String(origem), destino: String(destino) });
  if (grafo === "temporal" && temporada !== undefined) busca.set("temporada", String(temporada));
  return lerResposta(await fetch(`/api/parte2/rota?${busca}`));
}
