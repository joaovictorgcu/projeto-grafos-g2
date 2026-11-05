// [IA] Claude Code (Claude Opus 5.5) – tipos dos dados que o servidor Python (src/servidor.py) envia ao frontend
export type Algoritmo = "BFS" | "DIJKSTRA" | "BELLMAN_FORD";
export type Status = "OK" | "RECUSA" | "CICLO_NEGATIVO" | "SEM_SOLUCAO";
export type Origem = "enunciado" | "grupo" | "enviado";
export type Vista = "labirinto" | "grafo" | "comparar";
export type Modo = "percurso" | "exploracao";

export interface Estado {
  rotulo: string;
  l: number;
  c: number;
  chaves: string;
  bonus: number[];
  armadilha: boolean;
  saida: boolean;
}

export interface Resultado {
  status: Status;
  motivo?: string;
  caminho?: number[];
  custos?: number[];
  passos?: number;
  custo?: number;
  exploracao: [number, number][];
  ciclo?: { estados: number[]; custo: number };
}

export interface DadosDoMapa {
  id: string;
  titulo: string;
  origem: Origem;
  fonte_consumivel: boolean;
  grade: string[];
  chaves: string[];
  bonus: [number, number, number][];
  inicial: number;
  estados: Estado[];
  arcos: [number, number, number][];
  metricas: { ordem: number; tamanho: number; densidade: number };
  algoritmos: Record<Algoritmo, Resultado>;
}

export interface ResumoDoMapa {
  id: string;
  titulo: string;
  origem: Origem;
  grade: string[];
}

export interface Passo {
  estado: Estado;
  total: number;
  delta: number;
  novaChave: string | null;
  novoBonus: number | null;
}
