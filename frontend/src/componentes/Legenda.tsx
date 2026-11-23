// [IA] Claude Code (Claude Opus 5.5) – legenda do tabuleiro com o custo de cada tipo de casa
const ITENS = [
  { classe: "leg-chao", nome: "chão", custo: "+1" },
  { classe: "leg-lama", nome: "lama", custo: "+3" },
  { classe: "leg-agua", nome: "água", custo: "+5" },
  { classe: "leg-esteira", nome: "esteira", custo: "só na direção da seta" },
  { classe: "leg-chave", nome: "chave", custo: "fica para sempre" },
  { classe: "leg-porta", nome: "porta", custo: "só com a chave" },
  { classe: "leg-gema", nome: "bônus", custo: "−4 na 1ª vez" },
  { classe: "leg-fonte", nome: "fonte", custo: "−2 toda vez" },
  { classe: "leg-saida", nome: "saída G", custo: "arco de custo 0 até o ALVO" },
  { classe: "leg-armadilha", nome: "armadilha", custo: "nunca chega ao G" },
];

export function Legenda({ semRotulos }: { semRotulos?: boolean }) {
  return (
    <ul className="legenda" aria-label="Legenda do tabuleiro">
      {ITENS.map((i) => (
        <li key={i.nome}>
          <span className={`amostra ${i.classe}`} aria-hidden />
          <span className="legenda-nome">{i.nome}</span>
          {!semRotulos && <span className="legenda-custo">{i.custo}</span>}
        </li>
      ))}
    </ul>
  );
}
