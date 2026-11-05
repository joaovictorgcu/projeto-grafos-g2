// [IA] Claude Code (Claude Opus 5.5) – contas do frontend sobre os dados prontos: camadas, passos do percurso, onda de exploração
import type { Algoritmo, DadosDoMapa, Estado, Passo, Resultado, Status } from "./tipos";

export const ALGORITMOS: Algoritmo[] = ["BFS", "DIJKSTRA", "BELLMAN_FORD"];

export const NOME_DO_ALGORITMO: Record<Algoritmo, string> = {
  BFS: "BFS",
  DIJKSTRA: "Dijkstra",
  BELLMAN_FORD: "Bellman-Ford",
};

export const O_QUE_O_ALGORITMO_BUSCA: Record<Algoritmo, string> = {
  BFS: "menor número de passos",
  DIJKSTRA: "menor custo, só com pesos ≥ 0",
  BELLMAN_FORD: "menor custo, aceita pesos negativos",
};

export const NOME_DO_STATUS: Record<Status, string> = {
  OK: "Caminho encontrado",
  RECUSA: "Recusou o mapa",
  CICLO_NEGATIVO: "Ciclo negativo",
  SEM_SOLUCAO: "Sem solução",
};

export const CORES_CAMADA = ["#5aa2ff", "#ff8a4c", "#34d399", "#f78fb8", "#a78bfa", "#facc15", "#22d3ee", "#fb7185"];

export const CORES_CHAVE: Record<string, string> = { a: "#fbbf24", b: "#22d3ee", c: "#e879f9", d: "#a3e635" };

export function chave(l: number, c: number) {
  return `${l},${c}`;
}

export function nomeDaCamada(chaves: string) {
  return chaves ? `chaves {${chaves.split("").join(",")}}` : "sem chaves";
}

export function camadasDoMapa(dados: DadosDoMapa) {
  const contagem = new Map<string, number>();
  for (const e of dados.estados) contagem.set(e.chaves, (contagem.get(e.chaves) ?? 0) + 1);
  const ordem = [...contagem.keys()].sort((a, b) => a.length - b.length || a.localeCompare(b));
  return ordem.map((chaves, i) => ({ chaves, estados: contagem.get(chaves)!, cor: CORES_CAMADA[i % CORES_CAMADA.length] }));
}

export function corDaCamada(camadas: ReturnType<typeof camadasDoMapa>, chaves: string) {
  return camadas.find((c) => c.chaves === chaves)?.cor ?? CORES_CAMADA[0];
}

export function passosDoResultado(dados: DadosDoMapa, resultado: Resultado): Passo[] {
  const indices = resultado.caminho ?? [dados.inicial];
  const custos = resultado.custos ?? [0];
  return indices.map((i, n) => {
    const estado = dados.estados[i];
    const anterior = n > 0 ? dados.estados[indices[n - 1]] : null;
    const novaChave = anterior ? [...estado.chaves].find((k) => !anterior.chaves.includes(k)) ?? null : null;
    const novoBonus = anterior ? estado.bonus.find((b) => !anterior.bonus.includes(b)) ?? null : null;
    return { estado, total: custos[n] ?? 0, delta: n > 0 ? custos[n] - custos[n - 1] : 0, novaChave, novoBonus };
  });
}

export function celulasPorCamada(estados: Estado[]) {
  const mapa = new Map<string, { todas: Set<string>; armadilhas: Set<string> }>();
  for (const e of estados) {
    if (!mapa.has(e.chaves)) mapa.set(e.chaves, { todas: new Set(), armadilhas: new Set() });
    const grupo = mapa.get(e.chaves)!;
    grupo.todas.add(chave(e.l, e.c));
    if (e.armadilha) grupo.armadilhas.add(chave(e.l, e.c));
  }
  return mapa;
}

export function ondaDeExploracao(dados: DadosDoMapa, resultado: Resultado) {
  const primeira = new Map<string, { ordem: number; distancia: number }>();
  resultado.exploracao.forEach(([i, distancia], ordem) => {
    const e = dados.estados[i];
    const k = chave(e.l, e.c);
    if (!primeira.has(k)) primeira.set(k, { ordem, distancia });
  });
  const distancias = [...primeira.values()].map((v) => v.distancia);
  return {
    celulas: primeira,
    total: resultado.exploracao.length,
    menor: Math.min(...distancias, 0),
    maior: Math.max(...distancias, 1),
  };
}

export function formatar(numero: number, casas = 0) {
  return numero.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
}

export function resumoDaComparacao(
  a: { nome: string; resultado: Resultado },
  b: { nome: string; resultado: Resultado },
) {
  const ok = (r: Resultado) => r.status === "OK";
  if (!ok(a.resultado) && !ok(b.resultado)) return `Nenhum dos dois chega ao G: ${NOME_DO_STATUS[a.resultado.status].toLowerCase()} × ${NOME_DO_STATUS[b.resultado.status].toLowerCase()}.`;
  if (!ok(a.resultado)) return `Só o lado B chega ao G. O lado A: ${NOME_DO_STATUS[a.resultado.status].toLowerCase()}.`;
  if (!ok(b.resultado)) return `Só o lado A chega ao G. O lado B: ${NOME_DO_STATUS[b.resultado.status].toLowerCase()}.`;
  const dp = (b.resultado.passos ?? 0) - (a.resultado.passos ?? 0);
  const dc = (b.resultado.custo ?? 0) - (a.resultado.custo ?? 0);
  if (dp === 0 && dc === 0) return "Os dois fazem o mesmo número de passos com o mesmo custo.";
  const passos = dp === 0 ? "o mesmo número de passos" : `${Math.abs(dp)} passo${Math.abs(dp) > 1 ? "s" : ""} a ${dp > 0 ? "mais" : "menos"}`;
  const custo = dc === 0 ? "o mesmo custo" : `custo ${Math.abs(dc)} ${dc > 0 ? "maior" : "menor"}`;
  return `${b.nome} faz ${passos} que ${a.nome}, com ${custo}.`;
}
