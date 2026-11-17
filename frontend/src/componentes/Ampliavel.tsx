// [IA] Claude Code (Claude Opus 5.5) – zoom, arrastar e tela cheia para o tabuleiro, com a opção de a câmera seguir o jogador
import { Maximize2, Minimize2, Minus, Plus } from "lucide-react";
import { useEffect, useRef, useState, type CSSProperties, type PointerEvent, type ReactNode } from "react";

const NIVEIS = [1, 1.5, 2, 3, 4];

export function Ampliavel({ children, foco, rotulo }: { children: ReactNode; foco?: { x: number; y: number }; rotulo: string }) {
  const caixa = useRef<HTMLDivElement>(null);
  const area = useRef<HTMLDivElement>(null);
  const arrasto = useRef<{ x: number; y: number; esquerda: number; topo: number } | null>(null);
  const [nivel, setNivel] = useState(0);
  const [cheia, setCheia] = useState(false);
  const [seguir, setSeguir] = useState(true);
  const zoom = NIVEIS[nivel];

  useEffect(() => {
    const mudou = () => setCheia(document.fullscreenElement === caixa.current);
    document.addEventListener("fullscreenchange", mudou);
    return () => document.removeEventListener("fullscreenchange", mudou);
  }, []);

  useEffect(() => {
    const el = area.current;
    if (!el || !foco || !seguir || zoom === 1) return;
    el.scrollTo({
      left: foco.x * el.scrollWidth - el.clientWidth / 2,
      top: foco.y * el.scrollHeight - el.clientHeight / 2,
      behavior: "smooth",
    });
  }, [foco?.x, foco?.y, zoom, seguir, cheia]);

  function mudarZoom(delta: number) {
    setNivel((n) => Math.max(0, Math.min(NIVEIS.length - 1, n + delta)));
  }

  function alternarTelaCheia() {
    if (document.fullscreenElement) document.exitFullscreen();
    else caixa.current?.requestFullscreen();
  }

  useEffect(() => {
    const el = area.current;
    if (!el) return;
    function aoRolar(ev: globalThis.WheelEvent) {
      if (!ev.ctrlKey) return;
      ev.preventDefault();
      setNivel((n) => Math.max(0, Math.min(NIVEIS.length - 1, n + (ev.deltaY < 0 ? 1 : -1))));
    }
    el.addEventListener("wheel", aoRolar, { passive: false });
    return () => el.removeEventListener("wheel", aoRolar);
  }, []);

  function aoPressionar(ev: PointerEvent<HTMLDivElement>) {
    if (zoom === 1 || !area.current) return;
    area.current.setPointerCapture(ev.pointerId);
    arrasto.current = { x: ev.clientX, y: ev.clientY, esquerda: area.current.scrollLeft, topo: area.current.scrollTop };
  }

  function aoMover(ev: PointerEvent<HTMLDivElement>) {
    if (!arrasto.current || !area.current) return;
    setSeguir(false);
    area.current.scrollLeft = arrasto.current.esquerda - (ev.clientX - arrasto.current.x);
    area.current.scrollTop = arrasto.current.topo - (ev.clientY - arrasto.current.y);
  }

  const classes = ["ampliavel", zoom > 1 ? "ampliado" : "", cheia ? "cheia" : ""].join(" ");
  return (
    <div ref={caixa} className={classes} style={{ "--zoom": zoom } as CSSProperties}>
      <div className="ampliavel-barra" aria-label={`Zoom de ${rotulo}`}>
        <button type="button" className="botao-icone pequeno" onClick={() => mudarZoom(-1)} disabled={nivel === 0} aria-label="Diminuir o zoom">
          <Minus size={16} />
        </button>
        <span className="ampliavel-nivel">{Math.round(zoom * 100)}%</span>
        <button type="button" className="botao-icone pequeno" onClick={() => mudarZoom(1)} disabled={nivel === NIVEIS.length - 1} aria-label="Aumentar o zoom">
          <Plus size={16} />
        </button>
        {foco && zoom > 1 && (
          <label className="ampliavel-seguir">
            <input type="checkbox" checked={seguir} onChange={(ev) => setSeguir(ev.target.checked)} />
            seguir o jogador
          </label>
        )}
        <button type="button" className="botao-icone pequeno" onClick={alternarTelaCheia} aria-label={cheia ? "Sair da tela cheia" : "Tela cheia"}
          title={cheia ? "Sair da tela cheia (Esc)" : "Tela cheia"}>
          {cheia ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
        </button>
      </div>
      <div ref={area} className={zoom > 1 ? "ampliavel-area arrastavel" : "ampliavel-area"}
        onPointerDown={aoPressionar} onPointerMove={aoMover} onPointerUp={() => { arrasto.current = null; }}
        onPointerCancel={() => { arrasto.current = null; }}>
        {children}
      </div>
    </div>
  );
}
