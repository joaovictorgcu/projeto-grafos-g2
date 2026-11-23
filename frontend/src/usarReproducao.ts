// [IA] Claude Code (Claude Opus 5.5) – controle da animação passo a passo: tocar, pausar, avançar, voltar e velocidade
import { useCallback, useEffect, useRef, useState } from "react";

export function usarReproducao(ultimo: number, chaveDeReinicio: string, teclado = true, velocidadeInicial = 6) {
  const [passo, setPasso] = useState(0);
  const [tocando, setTocando] = useState(false);
  const [velocidade, setVelocidade] = useState(velocidadeInicial);
  const ultimoRef = useRef(ultimo);
  ultimoRef.current = ultimo;

  useEffect(() => {
    setPasso(0);
    setTocando(false);
  }, [chaveDeReinicio]);

  useEffect(() => {
    if (!tocando) return;
    const intervalo = Math.max(1000 / velocidade, 33);
    const salto = Math.max(1, Math.round((velocidade * intervalo) / 1000));
    const id = window.setInterval(() => {
      setPasso((p) => {
        if (p >= ultimoRef.current) {
          setTocando(false);
          return p;
        }
        return Math.min(ultimoRef.current, p + salto);
      });
    }, intervalo);
    return () => window.clearInterval(id);
  }, [tocando, velocidade]);

  const irPara = useCallback((p: number) => {
    setTocando(false);
    setPasso(Math.max(0, Math.min(ultimoRef.current, p)));
  }, []);

  const alternar = useCallback(() => {
    setTocando((t) => {
      if (!t) setPasso((p) => (p >= ultimoRef.current ? 0 : p));
      return !t;
    });
  }, []);

  useEffect(() => {
    if (!teclado) return;
    function tecla(evento: KeyboardEvent) {
      const alvo = evento.target as HTMLElement;
      if (alvo.closest("input, select, textarea, [contenteditable]")) return;
      if (evento.key === " ") {
        evento.preventDefault();
        alternar();
      } else if (evento.key === "ArrowRight") {
        setTocando(false);
        setPasso((p) => Math.min(ultimoRef.current, p + 1));
      } else if (evento.key === "ArrowLeft") {
        setTocando(false);
        setPasso((p) => Math.max(0, p - 1));
      } else if (evento.key === "Home") irPara(0);
      else if (evento.key === "End") irPara(ultimoRef.current);
    }
    window.addEventListener("keydown", tecla);
    return () => window.removeEventListener("keydown", tecla);
  }, [alternar, irPara, teclado]);

  return { passo: Math.min(passo, ultimo), tocando, velocidade, setVelocidade, irPara, alternar };
}

export type Reproducao = ReturnType<typeof usarReproducao>;
