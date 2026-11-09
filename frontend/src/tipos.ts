// [IA] Claude Code (Claude Opus 5.5) – tipos dos dados que o servidor Python (src/servidor.py) envia ao frontend
export type Algoritmo = "BFS" | "DIJKSTRA" | "BELLMAN_FORD";
export type Status = "OK" | "RECUSA" | "CICLO_NEGATIVO" | "SEM_SOLUCAO";
export type Origem = "enunciado" | "grupo" | "enviado";
export type Vista = "labirinto" | "exploracao" | "grafo" | "comparar";

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
  buscas: Buscas;
}

export interface Expansao {
  ordem: number[];
  descoberta: number[];
  alvo: number | null;
  caminho: number[];
}

export interface Buscas {
  DFS: { eventos: [number, 0 | 1][]; alvo: number | null; caminho: number[] };
  BFS: Expansao;
  DIJKSTRA: Expansao | { recusa: string };
  BELLMAN_FORD: Expansao | { ciclo: number };
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

export interface ParDoDijkstra {
  origem: string;
  destino: string;
  status: string;
  arcos: number;
  custo_original: number;
  caminho: string[];
  passos_bfs: number;
  transferencias: Record<string, string[]>;
}

export interface Figura {
  arquivo: string;
  codigo: string;
  tipo: string;
  nota: string;
}

export interface DadosDaParte2 {
  figuras: Figura[];
  relatorio: {
    dataset: {
      fonte: string;
      funil: { etapa: string; linhas: number }[];
      V: number;
      E: number;
      densidade: number;
      arcos_peso_negativo_pct: number;
      peso_min: number;
      peso_mediana: number;
      peso_max: number;
      temporal: { V: number; E: number };
    };
    bfs: { nome: string; alcancados: number; camadas: number[] }[];
    dfs: { nome: string; arcos: Record<string, number>; tem_ciclo: boolean }[];
    dijkstra: { transformacao: { formula: string; deslocamento_eur: number }; pares: ParDoDijkstra[] };
    bellman_ford: {
      sem_ciclo_negativo: {
        grafo: string; ordem: number; tamanho: number; arcos_negativos: number; fonte: string;
        menor_custo: { destino: string; custo: number; caminho: string[]; transferencias: Record<string, string[]> };
      };
      com_ciclo_negativo: {
        grafo: string; ordem: number; tamanho: number; fonte: string;
        ciclo: { clubes: string[]; custo: number; transferencias: Record<string, string[]> };
      }[];
    };
    ciclos_de_comprimento_2: { total: number; mais_negativos: { clubes: string[]; ida: number; volta: number; soma: number }[] };
    desempenho: { algoritmo: string; tarefa: string; tamanho_pct: number; V: number; E: number; media_s: number; desvio_s: number; memoria_pico_kb: number | null }[];
    escalabilidade: { algoritmo: string; complexidade: string; tamanho_pct: number; V: number; E: number; media_s: number; tempo_relativo: number; teoria_relativa: number }[];
    parametros: { repeticoes: number };
  };
}
