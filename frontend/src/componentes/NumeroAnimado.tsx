// [IA] Claude Code (Claude Opus 5.5) – número que desliza até o valor novo, usado no custo acumulado e nas métricas
import { motion, useSpring, useTransform } from "motion/react";
import { useEffect } from "react";
import { formatar } from "../modelo";

export function NumeroAnimado({ valor, casas = 0, className }: { valor: number; casas?: number; className?: string }) {
  const mola = useSpring(valor, { stiffness: 180, damping: 26 });
  const texto = useTransform(mola, (v) => formatar(v, casas));
  useEffect(() => {
    mola.set(valor);
  }, [mola, valor]);
  return <motion.span className={className}>{texto}</motion.span>;
}
