// [IA] Claude Code (Claude Opus 5.5) – grafo de estados em 3D: uma camada por conjunto de chaves, empilhadas, com o jogador subindo de andar ao pegar chave
import { Box, Eye, Layers, Move3d, Rows3 } from "lucide-react";
import { motion } from "motion/react";
import { useMemo, useRef, useState, type CSSProperties, type PointerEvent } from "react";
import { camadasDoMapa, chave, nomeDaCamada } from "../modelo";
import type { DadosDoMapa, Passo } from "../tipos";

const VISTAS = {
  isometrica: { x: 58, z: -32, nome: "Isométrica", Icone: Box },
  cima: { x: 0, z: 0, nome: "De cima", Icone: Eye },
  lado: { x: 78, z: -12, nome: "De lado", Icone: Rows3 },
};

export function GrafoDeEstados({ dados, passos, passo, duracao }: {
  dados: DadosDoMapa; passos: Passo[]; passo: number; duracao: number;
}) {
  const altura = dados.grade.length;
  const largura = dados.grade[0]?.length ?? 1;
  const camadas = useMemo(() => camadasDoMapa(dados), [dados]);
  const tamanho = Math.max(5, Math.min(40, Math.floor(Math.min(540 / largura, 300 / altura))));
  const [rotacao, setRotacao] = useState({ x: 58, z: -32 });
  const [espaco, setEspaco] = useState(Math.max(60, Math.min(150, altura * tamanho * 0.6)));
  const [arrastando, setArrastando] = useState(false);
  const inicio = useRef<{ x: number; y: number; rx: number; rz: number } | null>(null);
  const andar = (chaves: string) => camadas.findIndex((c) => c.chaves === chaves);
  const alturaDoAndar = (i: number) => (i - (camadas.length - 1) / 2) * espaco;

  const porCamada = useMemo(() => {
    const grupos = camadas.map(() => ({ estados: [] as number[], arcos: [] as [number, number][] }));
    dados.estados.forEach((e, i) => grupos[andar(e.chaves)].estados.push(i));
    const desenharArcos = dados.arcos.length <= 3200;
    const feixes = new Map<string, { l: number; c: number; de: number; para: number }>();
    for (const [u, v] of dados.arcos) {
      const eu = dados.estados[u];
      const ev = dados.estados[v];
      const iu = andar(eu.chaves);
      const iv = andar(ev.chaves);
      if (iu === iv) {
        if (desenharArcos) grupos[iu].arcos.push([u, v]);
      } else {
        feixes.set(`${chave(ev.l, ev.c)}|${iu}|${iv}`, { l: ev.l, c: ev.c, de: iu, para: iv });
      }
    }
    return { grupos, feixes: [...feixes.values()] };
  }, [dados, camadas]);

  const atual = passos[Math.min(passo, passos.length - 1)].estado;
  const usados = new Set<string>();
  for (let n = 1; n <= passo; n++) {
    const de = passos[n - 1].estado;
    const para = passos[n].estado;
    if (de.chaves !== para.chaves) usados.add(`${chave(para.l, para.c)}|${andar(de.chaves)}|${andar(para.chaves)}`);
  }

  function aoPressionar(ev: PointerEvent<HTMLDivElement>) {
    ev.currentTarget.setPointerCapture(ev.pointerId);
    inicio.current = { x: ev.clientX, y: ev.clientY, rx: rotacao.x, rz: rotacao.z };
    setArrastando(true);
  }
  function aoMover(ev: PointerEvent<HTMLDivElement>) {
    if (!inicio.current) return;
    const dx = ev.clientX - inicio.current.x;
    const dy = ev.clientY - inicio.current.y;
    setRotacao({ x: Math.max(0, Math.min(85, inicio.current.rx - dy * 0.3)), z: inicio.current.rz + dx * 0.3 });
  }
  function aoSoltar() {
    inicio.current = null;
    setArrastando(false);
  }

  const larguraDoPlano = largura * tamanho;
  const alturaDoPlano = altura * tamanho;

  return (
    <div className="grafo-estados">
      <div className={arrastando ? "cena arrastando" : "cena"} onPointerDown={aoPressionar} onPointerMove={aoMover}
        onPointerUp={aoSoltar} onPointerCancel={aoSoltar} role="img"
        aria-label={`Grafo de estados de ${dados.titulo} em ${camadas.length} camadas empilhadas. Arraste para girar.`}>
        <div className="flutuacao">
        <div className="palco" style={{
          width: larguraDoPlano, height: alturaDoPlano,
          transform: `rotateX(${rotacao.x}deg) rotateZ(${rotacao.z}deg)`,
          transition: arrastando ? "none" : "transform 0.7s cubic-bezier(.2,.8,.2,1)",
        }}>
          {camadas.map((camada, i) => {
            const grupo = porCamada.grupos[i];
            const ativa = atual.chaves === camada.chaves;
            const trechos: string[] = [];
            for (let n = 1; n <= passo; n++) {
              const de = passos[n - 1].estado;
              const para = passos[n].estado;
              if (de.chaves === camada.chaves && para.chaves === camada.chaves) {
                trechos.push(`M ${de.c + 0.5} ${de.l + 0.5} L ${para.c + 0.5} ${para.l + 0.5}`);
              }
            }
            return (
              <motion.div key={camada.chaves || "-"} className={ativa ? "plano ativo" : "plano"}
                style={{ "--cor": camada.cor, width: larguraDoPlano, height: alturaDoPlano } as CSSProperties}
                initial={{ z: alturaDoAndar(i) + 260, opacity: 0 }} animate={{ z: alturaDoAndar(i), opacity: 1 }}
                transition={{ delay: 0.12 * i, type: "spring", stiffness: 90, damping: 18 }}>
                <span className="plano-rotulo">{nomeDaCamada(camada.chaves)} · {camada.estados} estados</span>
                <svg viewBox={`0 0 ${largura} ${altura}`} width={larguraDoPlano} height={alturaDoPlano}>
                  {dados.grade.flatMap((linha, l) => [...linha].map((casa, c) =>
                    casa === "#" ? <rect key={`${l}-${c}`} x={c} y={l} width={1} height={1} className="plano-parede" /> : null))}
                  {grupo.arcos.map(([u, v], j) => {
                    const a = dados.estados[u];
                    const b = dados.estados[v];
                    return <line key={j} x1={a.c + 0.5} y1={a.l + 0.5} x2={b.c + 0.5} y2={b.l + 0.5} className="plano-arco" />;
                  })}
                  {trechos.length > 0 && <path d={trechos.join(" ")} className="plano-rastro" />}
                  {grupo.estados.map((idx) => {
                    const e = dados.estados[idx];
                    return (
                      <circle key={idx} cx={e.c + 0.5} cy={e.l + 0.5} r={e.saida ? 0.34 : 0.2}
                        className={e.armadilha ? "plano-no armadilha" : e.saida ? "plano-no saida" : "plano-no"}>
                        <title>{e.rotulo}{e.armadilha ? " · armadilha" : ""}</title>
                      </circle>
                    );
                  })}
                </svg>
              </motion.div>
            );
          })}

          {porCamada.feixes.map((f) => {
            const id = `${chave(f.l, f.c)}|${f.de}|${f.para}`;
            const baixo = Math.min(f.de, f.para);
            const alto = Math.max(f.de, f.para);
            const estilo = {
              left: (f.c + 0.5) * tamanho, top: (f.l + 0.5) * tamanho, height: alturaDoAndar(alto) - alturaDoAndar(baixo),
              "--de": camadas[baixo].cor, "--para": camadas[alto].cor, "--z": `${alturaDoAndar(baixo)}px`,
            } as CSSProperties;
            return (
              <div key={id} className={usados.has(id) ? "feixe usado" : "feixe"} style={estilo}>
                <span className="feixe-face" />
                <span className="feixe-face cruzada" />
              </div>
            );
          })}

          <div className="jogador3d" style={{
            left: (atual.c + 0.5) * tamanho, top: (atual.l + 0.5) * tamanho,
            transform: `translate(-50%, -50%) translateZ(${alturaDoAndar(andar(atual.chaves)) + 3}px)`,
            transition: `left ${duracao}s ease-in-out, top ${duracao}s ease-in-out, transform 0.6s cubic-bezier(.2,.8,.2,1)`,
            "--cor": camadas[andar(atual.chaves)]?.cor,
          } as CSSProperties} />
        </div>
        </div>
      </div>

      <div className="controles-3d">
        {Object.entries(VISTAS).map(([chaveDaVista, v]) => (
          <button key={chaveDaVista} type="button" className="chip" onClick={() => setRotacao({ x: v.x, z: v.z })}>
            <v.Icone size={15} aria-hidden /> {v.nome}
          </button>
        ))}
        <label className="velocidade">
          <Layers size={16} aria-hidden />
          <input type="range" min={20} max={220} value={espaco} onChange={(ev) => setEspaco(Number(ev.target.value))}
            aria-label="Distância entre as camadas" />
          <span>afastar camadas</span>
        </label>
        <span className="dica"><Move3d size={15} aria-hidden /> arraste para girar</span>
      </div>
    </div>
  );
}
