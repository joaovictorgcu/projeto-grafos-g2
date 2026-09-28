# [IA] Claude Code (Claude Opus 5.5) – gera o index.html da apresentação
"""Junta os slides (na ordem do deck.json) num index.html que abre direto no navegador.

Uso: python gerar_index.py
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

AQUI = Path(__file__).resolve().parent

MODELO = """<!doctype html>
<!-- [IA] Claude Code (Claude Opus 5.5) – gerado por gerar_index.py -->
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITULO__</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@300..700&family=IBM+Plex+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
  html, body { margin: 0; height: 100%; overflow: hidden; background: #0B1222; }
  #palco { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; transform-origin: 0 0; }
  #palco * { box-sizing: border-box; }
  #palco > section { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; overflow: hidden;
                     opacity: 0; visibility: hidden; transition: opacity .3s ease, visibility .3s; }
  #palco > section.ativo { opacity: 1; visibility: visible; }
  #palco h1, #palco h2, #palco h3, #palco p, #palco ul, #palco ol, #palco table { margin: 0; }
  #palco p, #palco li { line-height: 1.4; }
  #palco h1 { line-height: 1.1; } #palco h2 { line-height: 1.15; } #palco h3 { line-height: 1.2; }
  #palco ul, #palco ol { padding-left: 1.3em; }
  #palco table { width: 100%; border-collapse: collapse; }
  #palco th, #palco td { border: 1px solid #D5CEC0; padding: .35em .6em; text-align: left; vertical-align: top; }
  #palco th { font-weight: 600; }
  #palco aside { display: none; }
  #barra { position: fixed; right: 16px; bottom: 10px; font: 14px 'IBM Plex Sans', Arial, sans-serif;
           color: #C9D3E0; opacity: .7; user-select: none; }
  @media print {
    @page { size: 1920px 1080px; margin: 0; }
    html, body { height: auto; overflow: visible; background: none; }
    #palco { position: static; transform: none !important; width: auto; height: auto; }
    #palco > section { position: relative; opacity: 1; visibility: visible; transition: none; break-after: page; }
    #barra { display: none; }
  }
</style>
</head>
<body>
<div id="palco">
<!--SLIDES-->
</div>
<div id="barra"><span id="contador"></span> · ← → navegar · F tela cheia · Ctrl+P salva em PDF</div>
<script>
(() => {
  const NS = "http://www.w3.org/2000/svg";
  const px = v => parseFloat(v) || 0;
  let seq = 0;

  function novo(tag, attrs) {
    const el = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
    return el;
  }

  function ponta(svg, cor) {
    const id = "ponta" + (++seq);
    const m = novo("marker", { id, orient: "auto-start-reverse", markerWidth: 5, markerHeight: 5,
                               refX: 0.8, refY: 2, overflow: "visible" });
    m.appendChild(novo("path", { d: "M-3.2 -1.7 L0.8 0 L-3.2 1.7", transform: "translate(0 2)", fill: "none",
                                 stroke: cor, "stroke-width": 1, "stroke-linecap": "round",
                                 "stroke-linejoin": "round" }));
    const defs = novo("defs", {});
    defs.appendChild(m);
    svg.appendChild(defs);
    return `url(#${id})`;
  }

  function conector(el) {
    const cor = el.style.color || "#14213D";
    const esp = px(el.style.borderWidth) || 2;
    const cabeca = el.getAttribute("head") || "end";
    let svg, x1, y1, x2, y2;
    if (el.hasAttribute("x1")) {
      const pai = el.parentElement;
      svg = novo("svg", { width: pai.offsetWidth || 1920, height: pai.offsetHeight || 1080 });
      svg.style.cssText = "position:absolute; left:0; top:0; overflow:visible; pointer-events:none";
      [x1, y1, x2, y2] = ["x1", "y1", "x2", "y2"].map(a => px(el.getAttribute(a)));
    } else {
      const w = px(el.style.width), h = px(el.style.height), folga = esp * 3;
      svg = novo("svg", { width: Math.max(w, 2 * folga), height: Math.max(h, 2 * folga) });
      svg.style.cssText = "flex:none; overflow:visible";
      if (!h) { [x1, y1, x2, y2] = [0, folga, w, folga]; }
      else if (!w) { [x1, y1, x2, y2] = [folga, 0, folga, h]; }
      else { [x1, y1, x2, y2] = [0, 0, w, h]; }
    }
    const linha = novo("line", { x1, y1, x2, y2, stroke: cor, "stroke-width": esp, "stroke-linecap": "round" });
    if (el.style.borderStyle === "dashed") linha.setAttribute("stroke-dasharray", `${esp * 4} ${esp * 3}`);
    if (cabeca !== "none") {
      const url = ponta(svg, cor);
      linha.setAttribute("marker-end", url);
      if (cabeca === "both") linha.setAttribute("marker-start", url);
    }
    svg.appendChild(linha);
    el.replaceWith(svg);
  }

  const ICONES = {
    Check: '<polyline points="4.5 12.5 9.5 17.5 19.5 7"/>',
    Search: '<circle cx="10.5" cy="10.5" r="6"/><line x1="15" y1="15" x2="20" y2="20"/>',
    Lightning: '<polygon points="13 3 5 13.5 11 13.5 10 21 19 10 13 10 13 3"/>',
    Link: '<path d="M10 14a4.2 4.2 0 0 0 6 0l3-3a4.2 4.2 0 0 0-6-6l-1 1"/>' +
          '<path d="M14 10a4.2 4.2 0 0 0-6 0l-3 3a4.2 4.2 0 0 0 6 6l1-1"/>',
    Clock: '<circle cx="12" cy="12" r="8.5"/><polyline points="12 7.5 12 12 15 14"/>',
  };
  function icone(el) {
    const svg = novo("svg", { viewBox: "-4 -4 32 32", width: px(el.style.width) || 48,
                              height: px(el.style.height) || 48, fill: "none",
                              stroke: el.style.color || "currentColor", "stroke-width": 2,
                              "stroke-linecap": "round", "stroke-linejoin": "round" });
    svg.style.flex = "none";
    svg.innerHTML = ICONES[el.getAttribute("name")] || "";
    el.replaceWith(svg);
  }

  function forma(el) {
    const div = document.createElement("div");
    div.style.cssText = el.style.cssText;
    const tipo = el.getAttribute("kind");
    if (tipo === "ellipse") div.style.borderRadius = "50%";
    if (tipo === "diamond") div.style.clipPath = "polygon(50% 0, 100% 50%, 50% 100%, 0 50%)";
    el.replaceWith(div);
  }

  const palco = document.getElementById("palco");
  const slides = [...palco.children].filter(el => el.tagName === "SECTION");
  const contador = document.getElementById("contador");
  let atual = 0;

  function ajustar() {
    const s = Math.min(innerWidth / 1920, innerHeight / 1080);
    palco.style.transform = `translate(${(innerWidth - 1920 * s) / 2}px, ${(innerHeight - 1080 * s) / 2}px) scale(${s})`;
  }
  function mostrar(i) {
    atual = Math.max(0, Math.min(slides.length - 1, i));
    slides.forEach((sl, k) => sl.classList.toggle("ativo", k === atual));
    contador.textContent = `${atual + 1} / ${slides.length}`;
    history.replaceState(null, "", "#" + (atual + 1));
  }

  document.querySelectorAll("x-connector").forEach(conector);
  document.querySelectorAll("x-icon").forEach(icone);
  document.querySelectorAll("x-shape").forEach(forma);

  addEventListener("keydown", e => {
    if (["ArrowRight", "PageDown", " ", "Enter"].includes(e.key)) { e.preventDefault(); mostrar(atual + 1); }
    else if (["ArrowLeft", "PageUp", "Backspace"].includes(e.key)) { e.preventDefault(); mostrar(atual - 1); }
    else if (e.key === "Home") mostrar(0);
    else if (e.key === "End") mostrar(slides.length - 1);
    else if (e.key === "f" || e.key === "F") document.documentElement.requestFullscreen?.();
  });
  addEventListener("click", e => mostrar(atual + (e.clientX < innerWidth / 3 ? -1 : 1)));
  addEventListener("resize", ajustar);
  ajustar();
  mostrar((parseInt(location.hash.slice(1), 10) || 1) - 1);
})();
</script>
</body>
</html>
"""


def main():
    deck = json.loads((AQUI / "deck.json").read_text(encoding="utf-8"))
    partes = []
    for sid in deck["order"]:
        arquivo = AQUI / "slides" / f"{sid}.html"
        if not arquivo.exists():
            sys.exit(f"slide '{sid}' está no deck.json mas não existe em slides/")
        partes.append(arquivo.read_text(encoding="utf-8").strip())
    html = MODELO.replace("__TITULO__", deck["title"]).replace("<!--SLIDES-->", "\n".join(partes))
    (AQUI / "index.html").write_text(html, encoding="utf-8")
    print(f"index.html gerado com {len(partes)} slides")


if __name__ == "__main__":
    main()
