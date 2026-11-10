"""Monta a Banca: UM site e UM aplicativo (PWA) com a tela inicial e todos os jornais.

Uso: python3 banca/ferramentas/montar.py [pasta_origem]   (padrão: /mnt/project-files)

Para cada jornal copia index.html e edicoes.json da pasta de origem, injeta o
manifest único, a barra "voltar à Banca" e o registro do service worker único
(banca/sw.js). Gera a tela inicial (banca/index.html) com a manchete do dia de
cada jornal e um sw.js com versão nova sempre que algo muda, para o celular
baixar as edições do dia. Para incluir um jornal novo, acrescente-o em PUBS e
rode também ferramentas/icones.py.
"""
import hashlib, html as H, json, os, re, sys
from datetime import date

ORIGEM = sys.argv[1] if len(sys.argv) > 1 else "/mnt/project-files"
BANCA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAPEL, TINTA = "#ECE3D4", "#3A2D2B"
ICONES = ["icone-180.png", "icone-192.png", "icone-512.png", "icone-maskable-512.png"]

PUBS = [
    # pasta no site, pasta de origem, nome, para quem / do que trata
    ("jornal", "revista-leiga", "Jornal de Cada Dia",
     "Leitura fácil para a família: o Brasil e o mundo em linguagem simples, com muita saúde e dicas contra golpes."),
    ("brasil", "jornal-brasil", "Terra Brasilis",
     "Só o Brasil, Minas e Conselheiro Lafaiete: Brasília, bolso, saúde, escola e a cidade, em linguagem simples."),
    ("lafaiete", "jornal-lafaiete", "O Carijó",
     "O jornal de Conselheiro Lafaiete: prefeitura, saúde, empregos e agenda da cidade."),
    ("observatorio", "revista", "Observatório Diário",
     "Para estudar o mundo: geopolítica completa, guerras, energia, clima, IA e espaço, com história e filosofia."),
    ("xequemate", "medicina", "Xeque-Mate",
     "Medicina para estudantes: estudos, ensaios clínicos e saúde pública."),
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
<meta name="apple-mobile-web-app-title" content="Banca">
<link rel="manifest" href="{raiz}manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="{raiz}icone-192.png">
<link rel="apple-touch-icon" href="{raiz}icone-180.png">
"""

BARRA = """
<style>
.banca-volta{position:sticky;top:0;z-index:9999;display:flex;align-items:center;justify-content:space-between;gap:12px;
  background:#3A2D2B;color:#ECE3D4;padding:8px max(14px, env(safe-area-inset-right, 0px)) 8px max(14px, env(safe-area-inset-left, 0px));
  padding-top:max(8px, env(safe-area-inset-top, 0px));font:600 15px/1.2 "Archivo","Archivo Narrow","Helvetica Neue",Arial,sans-serif;
  letter-spacing:.08em;text-transform:uppercase}
.banca-volta a{color:inherit;text-decoration:none;display:inline-flex;align-items:center;gap:8px;padding:8px 14px 8px 10px;
  border:1.5px solid #ECE3D4;min-height:44px}
.banca-volta a:hover,.banca-volta a:focus-visible{background:#ECE3D4;color:#3A2D2B;outline:none}
.banca-volta span{opacity:.85;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@media print{.banca-volta{display:none}}
</style>
<nav class="banca-volta" aria-label="Banca"><a href="../">&#8249;&nbsp;Todos os jornais</a><span>{nome}</span></nav>
"""

REGISTRO = """
<script>
/* Banca: guarda os jornais para ler sem internet e recarrega quando chega edição nova */
if ("serviceWorker" in navigator) {
  addEventListener("load", function () {
    navigator.serviceWorker.register("{raiz}sw.js", {scope: "{raiz}"}).then(function (r) {
      r.addEventListener("updatefound", function () {
        var w = r.installing; if (!w) return;
        w.addEventListener("statechange", function () {
          if (w.state === "activated" && navigator.serviceWorker.controller) location.reload();
        });
      });
    }).catch(function () {});
  });
}
</script>
"""

SW = """/* Service worker único da Banca. Versão gerada automaticamente pelo montar.py. */
const V = "{versao}";
const CACHE = "banca-" + V;
const BASE = {base};

self.addEventListener("install", e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting()));
}});
self.addEventListener("activate", e => {{
  e.waitUntil(caches.keys().then(ks => Promise.all(
    ks.filter(k => k.startsWith("banca-") && k !== CACHE).map(k => caches.delete(k))
  )).then(() => self.clients.claim()));
}});
self.addEventListener("fetch", e => {{
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  // Fontes do Google: guarda na primeira vez e reaproveita (funciona sem internet).
  if (url.hostname.endsWith("fonts.googleapis.com") || url.hostname.endsWith("fonts.gstatic.com")) {{
    e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => {{
      const c = res.clone(); caches.open(CACHE).then(k => k.put(req, c)); return res;
    }})));
    return;
  }}
  if (url.origin !== location.origin) return;
  // Páginas e edições: internet primeiro (edição do dia); sem rede, a cópia guardada.
  e.respondWith(fetch(req, {{cache: "no-store"}}).then(res => {{
    if (res.ok) {{ const c = res.clone(); caches.open(CACHE).then(k => k.put(req, c)); }}
    return res;
  }}).catch(() => caches.match(req, {{ignoreSearch: true}}).then(r => r || caches.match("./"))));
}});
"""

# Os jornais tinham, cada um, o seu service worker. Este substituto se desliga
# sozinho, para que o service worker único da Banca passe a cuidar de tudo.
SW_ANTIGO = """/* Substituído pelo service worker único da Banca (../sw.js). Este se remove sozinho. */
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => /^banca-[a-z]+-/.test(k)).map(k => caches.delete(k))))
    .then(() => self.registration.unregister())
    .then(() => self.clients.matchAll())
    .then(cs => cs.forEach(c => c.navigate(c.url))));
});
"""

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]

def data_bonita(iso):
    try:
        a, m, d = (int(x) for x in str(iso)[:10].split("-"))
        return f"{d} de {MESES[m - 1]}"
    except Exception:
        return ""

def montar(pasta, origem, nome, desc):
    """Prepara um jornal; devolve (manchete, data) da edição mais recente."""
    d = os.path.join(BANCA, pasta)
    o = os.path.join(ORIGEM, origem)
    if os.path.exists(os.path.join(o, "index.html")) and os.path.exists(os.path.join(o, "edicoes.json")):
        html = open(os.path.join(o, "index.html"), encoding="utf-8").read()
        dados = open(os.path.join(o, "edicoes.json"), encoding="utf-8").read()
        json.loads(dados)  # aborta se o JSON estiver quebrado
        html = re.sub(r'<meta name="claude:[^>]*>\s*', "", html)
        html = re.sub(r'<meta charset="[^"]*">\s*', "", html, count=1)
        html = re.sub(r'<!doctype html>\s*', "", html, flags=re.I)
        # a barra "voltar" entra logo depois de <body>; se a página não tiver <body>, no começo do conteúdo
        barra = BARRA.replace("{nome}", H.escape(nome))
        if re.search(r"<body[^>]*>", html):
            html = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + barra, html, count=1)
        else:  # sem <body>: entra antes do primeiro elemento visível da página
            m = re.search(r"<(div|header|main|nav|section|article|p|h1|a)\b", html)
            html = html[:m.start()] + barra + html[m.start():] if m else barra + html
        pagina = (CABECA.format(desc=H.escape(desc), tinta=TINTA, raiz="../")
                  + html + REGISTRO.replace("{raiz}", "../"))
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(pagina)
        open(os.path.join(d, "edicoes.json"), "w", encoding="utf-8").write(dados)
        print(f"{pasta}: atualizado")
    else:
        print(f"{pasta}: origem ausente, mantida a versão anterior")
    # o jornal agora faz parte do app único: sai o manifest próprio, o sw antigo se desliga
    if os.path.exists(os.path.join(d, "manifest.webmanifest")):
        os.remove(os.path.join(d, "manifest.webmanifest"))
    open(os.path.join(d, "sw.js"), "w", encoding="utf-8").write(SW_ANTIGO)
    try:
        e = json.load(open(os.path.join(d, "edicoes.json"), encoding="utf-8"))["edicoes"][0]
        return e.get("capa", {}).get("titulo", ""), e.get("data", "")
    except Exception:
        return "", ""

def tela_inicial(cards):
    hoje = date.today()
    itens = []
    for pasta, nome, desc, manchete, dt in cards:
        quando = f"Edição de {data_bonita(dt)}" if dt else "Edição do dia"
        m = f'<q>{H.escape(manchete)}</q>' if manchete else ""
        itens.append(f"""  <a class="pub" href="{pasta}/">
    <img src="{pasta}/icone-192.png" alt="" width="84" height="84">
    <div class="txt"><small>{H.escape(quando)}</small><b>{H.escape(nome)}</b><span>{H.escape(desc)}</span>{m}</div>
    <i aria-hidden="true">&#8250;</i>
  </a>""")
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Banca</title>
<meta name="description" content="Os jornais do dia num só lugar: Jornal de Cada Dia, Terra Brasilis, O Carijó, Observatório Diário e Anamnese.">
<meta name="theme-color" content="{TINTA}">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Banca">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icone-192.png">
<link rel="apple-touch-icon" href="icone-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Playfair+Display:wght@600;700&family=Newsreader:ital,opsz,wght@0,6..72,400;1,6..72,400;1,6..72,500&family=Archivo:wght@600;800&display=swap">
<style>
/* Layout: capa de jornal antigo; nome enorme condensado entre filetes duplos, linha de edição com asteriscos, e um cartão grande por jornal */
:root{{--papel:{PAPEL};--tinta:{TINTA};--suave:#5E4E48;--fio:#B9A993}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--papel);color:var(--tinta);font-family:"Newsreader",Georgia,"Times New Roman",serif;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 .35  0 0 0 0 .27  0 0 0 0 .2  0 0 0 .10 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}}
.wrap{{max-width:780px;margin:0 auto;padding:max(22px, env(safe-area-inset-top, 0px)) max(16px, env(safe-area-inset-right, 0px)) 48px max(16px, env(safe-area-inset-left, 0px))}}
.duplo{{border-top:6px solid var(--tinta);border-bottom:2px solid var(--tinta);height:11px}}
.duplo.inv{{border-top-width:2px;border-bottom-width:6px}}
h1{{font-family:"Anton",Impact,"Arial Narrow",sans-serif;font-weight:400;font-size:clamp(76px,24vw,168px);line-height:.95;text-align:center;margin:12px 0 8px;text-transform:uppercase;letter-spacing:.01em}}
.linha{{display:flex;justify-content:space-between;align-items:center;gap:8px;font-family:"Archivo",Arial,sans-serif;font-weight:800;letter-spacing:.1em;font-size:13px;text-transform:uppercase;padding:12px 2px;border-bottom:1px solid var(--tinta)}}
h2{{font-family:"Playfair Display",Georgia,serif;font-weight:600;text-transform:uppercase;text-align:center;font-size:clamp(26px,6.5vw,40px);margin:18px 0 6px;letter-spacing:.02em}}
.sub{{text-align:center;font-style:italic;font-size:19px;color:var(--suave);margin:0 0 22px}}
a.pub{{display:flex;gap:16px;align-items:center;text-decoration:none;color:inherit;border:2px solid var(--tinta);outline:1px solid var(--tinta);outline-offset:3px;padding:16px;margin:0 4px 22px;background:rgba(255,255,255,.22);min-height:120px}}
a.pub:hover,a.pub:focus-visible{{background:rgba(255,255,255,.5)}}
a.pub:focus-visible{{outline-width:3px}}
a.pub img{{width:84px;height:84px;flex:none;border:1px solid var(--tinta)}}
.txt{{flex:1;min-width:0}}
.txt small{{display:block;font-family:"Archivo",Arial,sans-serif;font-weight:600;font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--suave);margin-bottom:2px}}
.txt b{{display:block;font-family:"Anton",Impact,"Arial Narrow",sans-serif;font-weight:400;font-size:clamp(28px,7vw,38px);line-height:1.05;text-transform:uppercase;letter-spacing:.01em}}
.txt span{{display:block;font-style:italic;font-size:18px;line-height:1.35;color:var(--suave);margin-top:4px}}
.txt q{{display:block;font-family:"Playfair Display",Georgia,serif;font-weight:600;font-size:17px;line-height:1.3;margin-top:10px;padding-top:8px;border-top:1px solid var(--fio)}}
.txt q::before{{content:"Manchete: ";font-family:"Archivo",Arial,sans-serif;font-weight:800;font-size:11px;letter-spacing:.1em;text-transform:uppercase}}
.txt q::after{{content:""}}
a.pub i{{font-style:normal;font-family:"Anton",Impact,sans-serif;font-size:46px;line-height:1;flex:none}}
.caixa{{border:2px solid var(--tinta);padding:14px 16px;margin:30px 4px 0;text-align:center;font-family:"Playfair Display",Georgia,serif;text-transform:uppercase;font-weight:600;font-size:17px;line-height:1.35}}
p.nota{{font-style:italic;font-size:17px;line-height:1.5;text-align:justify;margin:22px 4px 0}}
.linha span{{white-space:nowrap}}
@media (max-width:420px){{.linha .larga{{display:none}} a.pub{{padding:14px 12px;gap:12px}} a.pub img{{width:64px;height:64px}} a.pub i{{display:none}}}}
</style>
</head>
<body>
<div class="wrap">
  <div class="duplo"></div>
  <h1>Banca</h1>
  <div class="duplo inv"></div>
  <div class="linha"><span>{len(cards)} jornais</span><span>✱</span><span class="larga">Edição todo dia</span><span class="larga">✱</span><span>{hoje.strftime('%d/%m/%Y')}</span></div>
  <h2>Escolha o seu jornal</h2>
  <p class="sub">Toque num jornal para ler a edição de hoje.</p>
{chr(10).join(itens)}
  <div class="caixa">"Cada página impressa aproximava o mundo"</div>
  <p class="nota">Para ter a Banca como aplicativo no celular: no Android, abra no Chrome, toque nos três pontinhos e em "Instalar app" ou "Adicionar à tela inicial"; no iPhone, abra no Safari, toque em Compartilhar e em "Adicionar à Tela de Início". Depois da primeira visita, os jornais abrem até sem internet. Textos escritos com a ajuda do Claude, IA da Anthropic; não substituem orientação médica.</p>
</div>
{REGISTRO.replace("{raiz}", "./")}
</body>
</html>
"""

cards = []
for pasta, origem, nome, desc in PUBS:
    manchete, dt = montar(pasta, origem, nome, desc)
    cards.append((pasta, nome, desc, manchete, dt))

open(os.path.join(BANCA, "index.html"), "w", encoding="utf-8").write(tela_inicial(cards))

# caminhos antigos que mudaram de nome: redirecionam e desligam o service worker velho
REDIRECIONA = {"anamnese": "xequemate"}
for velho, novo in REDIRECIONA.items():
    d = os.path.join(BANCA, velho)
    if os.path.isdir(d):
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(
        f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Mudou de endereço</title>'
        f'<meta http-equiv="refresh" content="0; url=../{novo}/"><link rel="canonical" href="../{novo}/">'
        f'<script>location.replace("../{novo}/"+location.search+location.hash)</script></head>'
        f'<body style="background:{PAPEL};color:{TINTA};font:18px Georgia,serif;padding:24px">'
        f'<p>Este jornal mudou de endereço: <a href="../{novo}/" style="color:inherit">abrir</a>.</p></body></html>\n')
    open(os.path.join(d, "sw.js"), "w", encoding="utf-8").write(SW_ANTIGO)

manifest = {
    "name": "Banca", "short_name": "Banca",
    "description": "Os jornais do dia num só lugar: Jornal de Cada Dia, Terra Brasilis, O Carijó, Observatório Diário e Anamnese.",
    "lang": "pt-BR", "id": "/banca/", "start_url": "./", "scope": "./",
    "display": "standalone", "orientation": "portrait",
    "background_color": PAPEL, "theme_color": TINTA,
    "icons": [
        {"src": "icone-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icone-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icone-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
    "shortcuts": [{"name": nome, "url": f"{pasta}/", "icons": [{"src": f"{pasta}/icone-192.png", "sizes": "192x192"}]}
                  for pasta, _, nome, _ in PUBS],
}
open(os.path.join(BANCA, "manifest.webmanifest"), "w", encoding="utf-8").write(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

base = ["./", "index.html", "manifest.webmanifest"] + ICONES
for pasta, *_ in PUBS:
    base += [f"{pasta}/", f"{pasta}/index.html", f"{pasta}/edicoes.json", f"{pasta}/icone-192.png"]
h = hashlib.sha256()
for rel in base:
    p = os.path.join(BANCA, rel if not rel.endswith("/") else rel + "index.html")
    if os.path.exists(p):
        h.update(open(p, "rb").read())
versao = h.hexdigest()[:10]
open(os.path.join(BANCA, "sw.js"), "w", encoding="utf-8").write(
    SW.format(versao=versao, base=json.dumps(base, ensure_ascii=False)))
print(f"banca: versão {versao}")
