"""Monta a Banca (PWA) a partir das cópias das publicações em /mnt/project-files.

Uso: python3 banca/ferramentas/montar.py [pasta_origem]
Para cada publicação copia index.html e edicoes.json, injeta manifest, ícones,
cor de tema e o registro do service worker, e gera um sw.js com versão nova
sempre que o conteúdo muda (assim o celular baixa a edição do dia).
"""
import hashlib, json, os, re, sys

ORIGEM = sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files"
BANCA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPEL, TINTA = "#ECE3D4", "#3A2D2B"

PUBS = [
    # pasta no site, pasta de origem, nome, nome curto, descrição
    ("jornal", "revista-leiga", "Jornal de Cada Dia", "Jornal",
     "As notícias do dia em linguagem simples: política, saúde e tecnologia."),
    ("observatorio", "revista", "Observatório Diário", "Observatório",
     "Revista diária de geopolítica, ciência, IA e medicina."),
    ("anamnese", "medicina", "Anamnese", "Anamnese",
     "Jornal diário de medicina: estudos, ensaios clínicos e saúde pública."),
]

CABECA = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{desc}">
<meta name="theme-color" content="{tinta}">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="{curto}">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icone-192.png">
<link rel="apple-touch-icon" href="icone-180.png">
"""

REGISTRO = """
<script>
/* PWA: guarda a página para ler sem internet e avisa quando chega edição nova */
if ("serviceWorker" in navigator) {
  addEventListener("load", function () {
    navigator.serviceWorker.register("sw.js").then(function (r) {
      r.addEventListener("updatefound", function () {
        var w = r.installing;
        if (!w) return;
        w.addEventListener("statechange", function () {
          if (w.state === "activated" && navigator.serviceWorker.controller) location.reload();
        });
      });
    }).catch(function () {});
  });
}
</script>
"""

SW = """/* Service worker da Banca: {nome}. Versão gerada automaticamente. */
const V = "{versao}";
const CACHE = "banca-{pasta}-" + V;
const BASE = ["./", "index.html", "edicoes.json", "manifest.webmanifest",
  "icone-180.png", "icone-192.png", "icone-512.png", "icone-maskable-512.png"];

self.addEventListener("install", e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting()));
}});
self.addEventListener("activate", e => {{
  e.waitUntil(caches.keys().then(ks => Promise.all(
    ks.filter(k => k.startsWith("banca-{pasta}-") && k !== CACHE).map(k => caches.delete(k))
  )).then(() => self.clients.claim()));
}});
self.addEventListener("fetch", e => {{
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  // Fontes do Google: guarda a primeira vez e reaproveita (funciona sem internet).
  if (url.hostname.endsWith("fonts.googleapis.com") || url.hostname.endsWith("fonts.gstatic.com")) {{
    e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => {{
      const c = res.clone(); caches.open(CACHE).then(k => k.put(req, c)); return res;
    }})));
    return;
  }}
  if (url.origin !== location.origin) return;
  // Página e edições: tenta a internet primeiro (edição do dia); sem rede, usa a cópia guardada.
  e.respondWith(fetch(req, {{cache: "no-store"}}).then(res => {{
    if (res.ok) {{ const c = res.clone(); caches.open(CACHE).then(k => k.put(req, c)); }}
    return res;
  }}).catch(() => caches.match(req, {{ignoreSearch: true}}).then(r => r || caches.match("index.html"))));
}});
"""

def montar(pasta, origem, nome, curto, desc):
    o = os.path.join(ORIGEM, origem)
    html = open(os.path.join(o, "index.html"), encoding="utf-8").read()
    dados = open(os.path.join(o, "edicoes.json"), encoding="utf-8").read()
    json.loads(dados)  # aborta se o JSON estiver quebrado
    # tira o que só faz sentido dentro do Claude e cabeçalhos duplicados
    html = re.sub(r'<meta name="claude:[^>]*>\s*', "", html)
    html = re.sub(r'<meta charset="[^"]*">\s*', "", html, count=1)
    html = re.sub(r'<!doctype html>\s*', "", html, flags=re.I)
    d = os.path.join(BANCA, pasta)
    os.makedirs(d, exist_ok=True)
    pagina = CABECA.format(desc=desc, tinta=TINTA, curto=curto) + html + REGISTRO
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(pagina)
    open(os.path.join(d, "edicoes.json"), "w", encoding="utf-8").write(dados)
    manifest = {
        "name": nome, "short_name": curto, "description": desc, "lang": "pt-BR",
        "id": f"/banca/{pasta}/", "start_url": "./", "scope": "./",
        "display": "standalone", "orientation": "portrait",
        "background_color": PAPEL, "theme_color": TINTA,
        "icons": [
            {"src": "icone-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icone-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "icone-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    open(os.path.join(d, "manifest.webmanifest"), "w", encoding="utf-8").write(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    versao = hashlib.sha256((pagina + dados).encode()).hexdigest()[:10]
    open(os.path.join(d, "sw.js"), "w", encoding="utf-8").write(SW.format(nome=nome, versao=versao, pasta=pasta))
    print(f"{pasta}: versão {versao}")

for p in PUBS:
    if os.path.exists(os.path.join(ORIGEM, p[1], "index.html")):
        montar(*p)
    else:
        print(f"{p[0]}: origem ausente, mantida a versão anterior")
