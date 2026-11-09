// [IA] Claude Code (Claude Opus 5.5) – chamadas ao servidor Python, com cache para não recalcular o mesmo mapa
import type { DadosDaParte2, DadosDoMapa, ResumoDoMapa } from "./tipos";

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
