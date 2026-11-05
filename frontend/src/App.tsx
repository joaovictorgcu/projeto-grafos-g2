// [IA] Claude Code (Claude Opus 5.5) – tela principal: abas, estado compartilhado (mapa, algoritmo, passo) e envio do mapa surpresa
import { Boxes, GitCompareArrows, Network, Radar, ServerCrash, Waypoints } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { analisarTexto, carregarMapa, listarMapas } from "./api";
import { Comparacao } from "./componentes/Comparacao";
import { Controles } from "./componentes/Controles";
import { Exploracao } from "./componentes/Exploracao";
import { GrafoDeEstados } from "./componentes/GrafoDeEstados";
import { AvisoDeErro, EscolhaDeAlgoritmo, EscolhaDeMapa, InterruptorDaFonte, Opcoes } from "./componentes/Lateral";
import { Legenda } from "./componentes/Legenda";
import { Metricas } from "./componentes/Metricas";
import { Painel } from "./componentes/Painel";
import { Status } from "./componentes/Status";
import { Tabuleiro } from "./componentes/Tabuleiro";
import { ALGORITMOS, camadasDoMapa, corDaCamada, nomeDaCamada, passosDoResultado } from "./modelo";
import type { Algoritmo, DadosDoMapa, ResumoDoMapa, Vista } from "./tipos";
import { usarReproducao } from "./usarReproducao";

const ABAS: { id: Vista; nome: string; Icone: typeof Network }[] = [
  { id: "labirinto", nome: "Labirinto", Icone: Waypoints },
  { id: "exploracao", nome: "Exploração", Icone: Radar },
  { id: "grafo", nome: "Grafo de estados", Icone: Boxes },
  { id: "comparar", nome: "Comparar", Icone: GitCompareArrows },
];

const parametros = new URLSearchParams(window.location.search);

export default function App() {
  const [mapas, setMapas] = useState<ResumoDoMapa[]>([]);
  const [mapaId, setMapaId] = useState(parametros.get("mapa") ?? "");
  const [algoritmo, setAlgoritmo] = useState<Algoritmo>(
    ALGORITMOS.includes(parametros.get("alg") as Algoritmo) ? (parametros.get("alg") as Algoritmo) : "DIJKSTRA");
  const [vista, setVista] = useState<Vista>((["labirinto", "exploracao", "grafo", "comparar"] as Vista[]).includes(parametros.get("vista") as Vista)
    ? (parametros.get("vista") as Vista) : "labirinto");
  const [fonte, setFonte] = useState(parametros.get("fonte") === "1");
  const [camada, setCamada] = useState<string | null>(null);
  const [armadilhas, setArmadilhas] = useState(false);
  const [dados, setDados] = useState<DadosDoMapa | null>(null);
  const [erroServidor, setErroServidor] = useState<string | null>(null);
  const [erroEnvio, setErroEnvio] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);
  const enviados = useRef(new Map<string, string>());
  const analisesEnviadas = useRef(new Map<string, Promise<DadosDoMapa>>());

  const obterDados = useCallback((id: string, comFonte: boolean) => {
    const texto = enviados.current.get(id);
    if (texto === undefined) return carregarMapa(id, comFonte);
    const k = `${id}|${comFonte}`;
    if (!analisesEnviadas.current.has(k)) analisesEnviadas.current.set(k, analisarTexto(texto, id, comFonte));
    return analisesEnviadas.current.get(k)!;
  }, []);

  useEffect(() => {
    listarMapas()
      .then((lista) => {
        setMapas(lista);
        setMapaId((atual) => (lista.some((m) => m.id === atual) ? atual : lista[0]?.id ?? ""));
      })
      .catch(() => setErroServidor("Não consegui falar com o servidor Python."));
  }, []);

  useEffect(() => {
    if (!mapaId) return;
    let vivo = true;
    obterDados(mapaId, fonte)
      .then((d) => {
        if (!vivo) return;
        setDados(d);
        setCamada(null);
      })
      .catch((e: Error) => vivo && setErroEnvio(e.message));
    return () => { vivo = false; };
  }, [mapaId, fonte, obterDados]);

  useEffect(() => {
    const p = new URLSearchParams();
    if (mapaId) p.set("mapa", mapaId);
    p.set("alg", algoritmo);
    p.set("vista", vista);
    if (fonte) p.set("fonte", "1");
    window.history.replaceState(null, "", `?${p}`);
  }, [mapaId, algoritmo, vista, fonte]);

  const pronto = dados && dados.id === mapaId && dados.fonte_consumivel === fonte ? dados : null;
  const resultado = pronto?.algoritmos[algoritmo] ?? null;
  const passos = useMemo(() => (pronto && resultado ? passosDoResultado(pronto, resultado) : []), [pronto, resultado]);
  const camadas = useMemo(() => (pronto ? camadasDoMapa(pronto) : []), [pronto]);
  const reproducao = usarReproducao(Math.max(0, passos.length - 1), `${mapaId}|${fonte}|${algoritmo}`, vista === "labirinto" || vista === "grafo");
  const duracao = Math.min(0.32, 0.85 / reproducao.velocidade);
  const atual = passos[reproducao.passo];
  const corAtual = atual ? corDaCamada(camadas, atual.estado.chaves) : "#2563eb";
  const inicialDoParametro = useRef(Number(parametros.get("passo") ?? 0));

  useEffect(() => {
    if (inicialDoParametro.current && passos.length > 1) {
      reproducao.irPara(inicialDoParametro.current);
      inicialDoParametro.current = 0;
    }
  }, [passos, reproducao]);

  async function enviarArquivo(arquivo: File) {
    setErroEnvio(null);
    setEnviando(true);
    const base = arquivo.name.replace(/\.txt$/i, "").replace(/[^\w-]+/g, "_") || "enviado";
    const nome = mapas.some((m) => m.id === base && m.origem !== "enviado") ? `${base}_enviado` : base;
    try {
      const texto = await arquivo.text();
      const analise = await analisarTexto(texto, nome, false);
      enviados.current.set(nome, texto);
      analisesEnviadas.current.set(`${nome}|false`, Promise.resolve(analise));
      [...analisesEnviadas.current.keys()].filter((k) => k.startsWith(`${nome}|true`)).forEach((k) => analisesEnviadas.current.delete(k));
      setMapas((lista) => [...lista.filter((m) => m.id !== nome),
        { id: nome, titulo: `${base.replace(/_/g, " ")} · enviado`, origem: "enviado", grade: analise.grade }]);
      setFonte(false);
      setMapaId(nome);
    } catch (e) {
      setErroEnvio((e as Error).message);
    } finally {
      setEnviando(false);
    }
  }

  if (erroServidor) {
    return (
      <div className="tela-erro">
        <ServerCrash size={42} aria-hidden />
        <h1>{erroServidor}</h1>
        <p>Abra um terminal na pasta do projeto e rode <code>python -m src.servidor</code>.</p>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="fundo-animado" aria-hidden />
      <AvisoDeErro erro={erroEnvio} limparErro={() => setErroEnvio(null)} />
      <header className="topo">
        <div className="marca">
          <svg viewBox="0 0 32 32" className="logo" aria-hidden>
            <path d="M7 7h8v6h6V7h4v12h-6v6H7z" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinejoin="round" />
            <circle cx="23" cy="23" r="3" className="logo-ponto" />
          </svg>
          <div>
            <h1>Labirinto de Estados</h1>
            <span>Teoria dos Grafos · Grupo 2 · CESAR School</span>
          </div>
        </div>
        <nav className="abas" aria-label="Seções">
          {ABAS.map(({ id, nome, Icone }) => (
            <button key={id} type="button" className={vista === id ? "aba ativa" : "aba"} onClick={() => setVista(id)}
              aria-current={vista === id ? "page" : undefined}>
              {vista === id && <motion.span layoutId="aba-ativa" className="aba-fundo" transition={{ type: "spring", stiffness: 400, damping: 32 }} />}
              <Icone size={17} aria-hidden />
              <span>{nome}</span>
            </button>
          ))}
        </nav>
      </header>

      <div className={vista === "comparar" ? "corpo sem-lateral" : "corpo"}>
        {vista !== "comparar" && (
          <aside className="lateral">
            <EscolhaDeMapa mapas={mapas} escolhido={mapaId} aoEscolher={setMapaId} aoEnviar={enviarArquivo} enviando={enviando} />
            {vista !== "exploracao" && <EscolhaDeAlgoritmo dados={pronto} algoritmo={algoritmo} aoEscolher={setAlgoritmo} />}
            {vista === "labirinto" && (
              <Opcoes dados={pronto} fonte={fonte} setFonte={setFonte} camada={camada}
                setCamada={setCamada} armadilhas={armadilhas} setArmadilhas={setArmadilhas} coresDasCamadas={camadas} />
            )}
            {(vista === "grafo" || vista === "exploracao") && (
              <section className="secao-lateral">
                <h2>Opções</h2>
                <InterruptorDaFonte dados={pronto} fonte={fonte} setFonte={setFonte} />
              </section>
            )}
          </aside>
        )}

        <main className="conteudo">
          <AnimatePresence mode="wait">
            <motion.div key={vista} className="vista" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.28, ease: "easeOut" }}>
              {vista === "comparar" ? (
                mapas.length > 0 && <Comparacao mapas={mapas} mapaInicial={mapaId || mapas[0].id} obterDados={obterDados} />
              ) : !pronto || !resultado || !atual ? (
                <div className="carregando"><span className="girando" />Montando o grafo de estados…</div>
              ) : (
                vista === "exploracao" ? (
                  <>
                    <div className="titulo-vista">
                      <div>
                        <h2>{pronto.titulo}</h2>
                        <span>{pronto.grade[0].length}×{pronto.grade.length} casas · {pronto.metricas.ordem} estados · os quatro
                          algoritmos partindo do S ao mesmo tempo</span>
                      </div>
                    </div>
                    <Exploracao dados={pronto} />
                  </>
                ) : (
                <>
                  <div className="titulo-vista">
                    <div>
                      <h2>{pronto.titulo}</h2>
                      <span>{pronto.grade[0].length}×{pronto.grade.length} casas · {pronto.metricas.ordem} estados · camada atual:{" "}
                        <b style={{ color: corAtual }}>{nomeDaCamada(atual.estado.chaves)}</b></span>
                    </div>
                    <Status algoritmo={algoritmo} resultado={resultado} fonte={fonte} />
                  </div>

                  {vista === "labirinto" ? (
                    <div className="grade-labirinto">
                      <div className="quadro">
                        <Tabuleiro dados={pronto} resultado={resultado} passos={passos} passo={reproducao.passo} duracao={duracao}
                          camadaFixa={camada} mostrarArmadilhas={armadilhas} />
                        <Legenda />
                      </div>
                      <Painel dados={pronto} passos={passos} passo={reproducao.passo} cor={corAtual} />
                    </div>
                  ) : (
                    <div className="grade-grafo">
                      <GrafoDeEstados dados={pronto} passos={passos} passo={reproducao.passo} duracao={duracao} />
                      <aside className="painel">
                        <section className="cartao">
                          <span className="rotulo-pequeno">como ler</span>
                          <ul className="explicacao">
                            <li>Cada <b>andar</b> é uma camada: o mesmo labirinto para um conjunto de chaves.</li>
                            <li>Cada <b>ponto</b> é um estado: posição + chaves + bônus usados.</li>
                            <li>Os <b>feixes verticais</b> são os arcos que trocam de camada: pegar uma chave sobe de andar.</li>
                            <li>Pontos <b className="texto-armadilha">vermelhos</b> são armadilhas; os maiores são estados em G.</li>
                          </ul>
                        </section>
                        <section className="cartao">
                          <span className="rotulo-pequeno">camadas deste mapa</span>
                          <ul className="lista-camadas">
                            {camadas.map((c) => (
                              <li key={c.chaves || "-"} className={c.chaves === atual.estado.chaves ? "ativa" : ""}>
                                <i className="ponto" style={{ background: c.cor }} />
                                <span>{nomeDaCamada(c.chaves)}</span>
                                <b>{c.estados}</b>
                              </li>
                            ))}
                          </ul>
                        </section>
                        <Painel dados={pronto} passos={passos} passo={reproducao.passo} cor={corAtual} />
                      </aside>
                    </div>
                  )}

                  <Controles reproducao={reproducao} ultimo={passos.length - 1} passos={passos} cor={corAtual} />
                  {vista === "labirinto" && <Metricas dados={pronto} algoritmo={algoritmo} aoEscolher={setAlgoritmo} />}
                </>
                )
              )}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
