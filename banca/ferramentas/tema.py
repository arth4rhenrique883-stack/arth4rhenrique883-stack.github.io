"""Modo claro e escuro (10/11/2026) em todas as páginas do Xeque News.

aplicar(html) põe (ou atualiza) o bloco de ferramentas/tema.html no <head> da página e,
nos jornais em tinta preta (Terra Brasilis, O Carijó, painel de sugestões), troca o preto
fixo do CSS por variáveis, para as tarjas pretas virarem marfim no modo escuro.
No modo claro nada muda: as variáveis valem o mesmo preto de antes.

Uso avulso: python3 tema.py arquivo.html [...]   (altera os arquivos no lugar)
"""
import os, re, sys

TEMA = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tema.html"), encoding="utf-8").read().strip()
TROCAS = [(r"#111111\b", "var(--tinta)"), (r"#111\b", "var(--tinta)"), (r"#0A0A0A\b", "var(--tinta-forte,#0A0A0A)"),
          (r"#333\b", "var(--tinta-hover,#333)"), (r"#D9D1C2\b", "var(--tarja-suave,#D9D1C2)")]

def _preto(css):
    def decl(m):
        prop, val = m.group(1), m.group(2)
        if prop.lstrip("{; \t\r\n").startswith("--"):
            return m.group(0)
        for a, b in TROCAS:
            val = re.sub(a, b, val, flags=re.I)
        return prop + ":" + val
    return re.sub(r"([{;]\s*[\w-]+)\s*:([^;{}]*)", decl, css)

def aplicar(html):
    if "<!--tema:inicio-->" in html:
        i, j = html.find("<!--tema:inicio-->"), html.find("<!--tema:fim-->") + len("<!--tema:fim-->")
        html = html[:i] + TEMA + html[j:]
    else:
        m = re.search(r"<head[^>]*>", html, re.I) or re.search(r'<meta charset="[^"]*">', html, re.I)
        html = html[:m.end()] + "\n" + TEMA + "\n" + html[m.end():] if m else TEMA + "\n" + html
    if "UnifrakturMaguntia" in html or "--tinta:#111" in html:
        html = re.sub(r"(<style(?![^>]*tema-xeque)[^>]*>)(.*?)(</style>)",
                      lambda m: m.group(1) + _preto(m.group(2)) + m.group(3), html, flags=re.S)
    return html

if __name__ == "__main__":
    for p in sys.argv[1:]:
        s = open(p, encoding="utf-8").read()
        n = aplicar(s)
        if n != s:
            open(p, "w", encoding="utf-8").write(n)
            print(p, "ok")
