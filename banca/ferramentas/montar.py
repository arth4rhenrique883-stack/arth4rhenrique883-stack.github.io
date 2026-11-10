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
    # pasta no site, pasta de origem, nome, para quem / do que trata, opções
    #   destaque: cartão grande na tela inicial (os outros vão para "Também no Xeque News")
    #   semMedicina: tira o caderno de medicina (que agora vive no Xeque-Mate)
    #   encarte: junta o caderno de Conselheiro Lafaiete do O Carijó ("jornal" ou "obs")
    ("jornal", "revista-leiga", "Jornal de Cada Dia",
     "Leitura fácil para a família: o Brasil e o mundo em linguagem simples, mais o caderno de Conselheiro Lafaiete.",
     {"destaque": True, "encarte": "jornal"}),
    ("mundo-lafaiete", "revista", "Do Mundo a Lafaiete",
     "O Observatório completo, com geopolítica, guerras, energia, IA e espaço, mais o caderno de Conselheiro Lafaiete.",
     {"destaque": True, "semMedicina": True, "encarte": "obs"}),
    # Caderno Brasil (10/11/2026): ao abrir, o leitor escolhe "Mundo + Brasil" ou
    # "Apenas Brasil". O caderno é o mesmo do Terra Brasilis (jornal-brasil/edicoes.json, sem Lafaiete),
    # copiado como brasil.json; a página só mostra a escolha se brasil.json existir ao lado dela.
    ("observatorio", "revista", "Observatório Diário",
     "O mundo para estudar (geopolítica, guerras, energia, clima, IA e espaço, com história e filosofia) e o caderno do Brasil. Ao abrir, escolha Mundo + Brasil ou Apenas Brasil.",
     {"destaque": True, "semMedicina": True, "extras": {"brasil.json": "jornal-brasil/edicoes.json"}}),
    ("xequemate", "medicina", "Xeque-Mate",
     "Só medicina, para estudantes: estudos, ensaios clínicos, aprovações e saúde pública.",
     {"destaque": True}),
    # Terra Brasilis (10/11/2026): só o Brasil e Minas Gerais; abre direto, sem tela de escolha.
    ("brasil", "jornal-brasil", "Terra Brasilis",
     "O Brasil e Minas Gerais: Brasília, o seu bolso, saúde, escola e Minas. Toda notícia diz como afeta o trabalhador e cada classe.",
     {"destaque": True}),
    # O Carijó (10/11/2026): Conselheiro Lafaiete voltou a ser jornal próprio, de uso pessoal por enquanto.
    #   oculto: fica fora da tela inicial e dos atalhos do app; abre só pelo link direto (/banca/lafaiete/).
    # O lafaiete/edicoes.json também alimenta o encarte-lafaiete.js (Jornal de Cada Dia e Do Mundo a Lafaiete).
    ("lafaiete", "jornal-lafaiete", "O Carijó",
     "O jornal de Conselheiro Lafaiete: Prefeitura e Câmara, saúde, emprego, segurança, cidade e esporte. Toda notícia diz como afeta o trabalhador e cada classe.",
     {"oculto": True}),
]

# Dossiês de estudo: páginas avulsas (sem edicoes.json), cada uma com seu próprio
# manifest, para poder ser instalada sozinha como aplicativo e enviada por link.
DOSSIES = [
    # pasta no site, pasta de origem, nome, descrição
    ("caso-master", "caso-master-stf", "O Caso Moraes–Vorcaro",
     "Dossiê de estudo: por que um ministro do STF citado no caso Banco Master continua no cargo."),
]

# Logo da rainha (10/11/2026): em TODOS os jornais e dossiês, parada,
# em tinta, como selo no canto. Se a página de origem já a tiver, não duplica.
RAINHA = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rainha.html"), encoding="utf-8").read()

def com_rainha(html):
    return com_compromisso(html) if "rainha-canto" in html else com_compromisso(html) + "\n" + RAINHA

# Fontes e compromisso editorial (10/11/2026): expediente no pé de TODOS os
# jornais e dossiês, com as fontes de referência, a linha editorial sem partido e os limites.
# Página completa em /banca/fontes/. Se a página de origem já o tiver, não duplica.
COMPROMISSO = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "compromisso.html"), encoding="utf-8").read()
FONTES = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fontes.html"), encoding="utf-8").read()

def com_compromisso(html):
    if "compromisso-editorial" in html:
        return html
    i = html.find("<!--rainha:inicio-->")
    return html[:i] + COMPROMISSO + "\n" + html[i:] if i >= 0 else html + "\n" + COMPROMISSO

ENCARTE = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "encarte-lafaiete.js"), encoding="utf-8").read()

def sem_medicina(dados):
    """O Observatório não traz mais medicina (10/11/2026): ela fica no Xeque-Mate."""
    d = json.loads(dados)
    for e in d.get("edicoes", []):
        e.pop("medicina", None)
        if isinstance(e.get("chamadas"), list):
            e["chamadas"] = [c for c in e["chamadas"] if c.get("secao") != "medicina"]
    return json.dumps(d, ensure_ascii=False, indent=1)

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
<meta name="apple-mobile-web-app-title" content="Xeque News">
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
.banca-volta a.banca-fontes{padding:8px 12px;flex:none}
.banca-volta span{flex:1;text-align:right;opacity:.85;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
@media (max-width:430px){.banca-volta span{display:none}}
@media print{.banca-volta{display:none}}
</style>
<nav class="banca-volta" aria-label="Xeque News"><a href="../">&#8249;&nbsp;Todos os jornais</a><span>{nome}</span><a href="../fontes/" class="banca-fontes">Fontes</a></nav>
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

def montar(pasta, origem, nome, desc, opts):
    """Prepara um jornal; devolve (manchete, data) da edição mais recente."""
    d = os.path.join(BANCA, pasta)
    o = os.path.join(ORIGEM, origem)
    if os.path.exists(os.path.join(o, "index.html")) and os.path.exists(os.path.join(o, "edicoes.json")):
        html = open(os.path.join(o, "index.html"), encoding="utf-8").read()
        dados = open(os.path.join(o, "edicoes.json"), encoding="utf-8").read()
        json.loads(dados)  # aborta se o JSON estiver quebrado
        if opts.get("semMedicina"):
            dados = sem_medicina(dados)
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
        cabeca = CABECA.format(desc=H.escape(desc), tinta=TINTA, raiz="../")
        if opts.get("oculto"):
            cabeca += '<meta name="robots" content="noindex, nofollow">\n'
        pagina = (cabeca
                  + com_rainha(html) + REGISTRO.replace("{raiz}", "../"))
        if opts.get("encarte"):
            pagina += "\n<script>\n" + ENCARTE.replace("{modo}", opts["encarte"]) + "</script>\n"
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(pagina)
        open(os.path.join(d, "edicoes.json"), "w", encoding="utf-8").write(dados)
        for nome_extra, orig_extra in opts.get("extras", {}).items():
            p_extra = os.path.join(ORIGEM, orig_extra)
            if os.path.exists(p_extra):
                txt = open(p_extra, encoding="utf-8").read()
                json.loads(txt)  # aborta se o JSON estiver quebrado
                open(os.path.join(d, nome_extra), "w", encoding="utf-8").write(txt)
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

VOLTA_DOSSIE = """
<style>.banca-mini{font:600 13px/1.2 "IBM Plex Mono","Courier New",monospace;letter-spacing:.08em;text-transform:uppercase;text-align:center;padding:12px 0 0}
.banca-mini a{color:#3A2D2B}</style>
<div class="banca-mini"><a href="../">&#8249; Ver também os jornais do Xeque News</a></div>
"""

def montar_dossie(pasta, origem, nome, desc):
    """Copia um dossiê e o transforma em aplicativo próprio (manifest e ícones da pasta)."""
    d = os.path.join(BANCA, pasta)
    o = os.path.join(ORIGEM, origem, "index.html")
    if not os.path.exists(o):
        print(f"{pasta}: origem ausente, mantida a versão anterior")
        return
    html = open(o, encoding="utf-8").read()
    html = re.sub(r'<meta name="claude:[^>]*>\s*', "", html)
    m = re.search(r"<(div|header|main|nav|section|article)\b", html)
    html = html[:m.start()] + VOLTA_DOSSIE + html[m.start():] if m else VOLTA_DOSSIE + html
    cab = (CABECA.format(desc=H.escape(desc), tinta=TINTA, raiz="")
           .replace('content="Xeque News"', f'content="{H.escape(nome)}"'))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(
        cab + com_rainha(html) + REGISTRO.replace("{raiz}", "../") + "</body>\n</html>\n")
    man = {"name": nome, "short_name": "Caso Master" if pasta == "caso-master" else nome,
           "description": desc, "lang": "pt-BR", "id": f"/banca/{pasta}/", "start_url": "./", "scope": "./",
           "display": "standalone", "background_color": PAPEL, "theme_color": TINTA,
           "icons": [{"src": "icone-192.png", "sizes": "192x192", "type": "image/png"},
                     {"src": "icone-512.png", "sizes": "512x512", "type": "image/png"},
                     {"src": "icone-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}
    open(os.path.join(d, "manifest.webmanifest"), "w", encoding="utf-8").write(
        json.dumps(man, ensure_ascii=False, indent=2) + "\n")
    print(f"{pasta}: dossiê atualizado")

def tela_inicial(cards):
    hoje = date.today()
    itens, outros = [], []
    for pasta, nome, desc, manchete, dt, destaque in cards:
        if not destaque:
            outros.append(f'  <a class="outro" href="{pasta}/"><img src="{pasta}/icone-192.png" alt="" width="44" height="44"><span><b>{H.escape(nome)}</b> {H.escape(desc)}</span></a>')
            continue
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
<title>Xeque News</title>
<meta name="description" content="Os jornais do dia num só lugar: Jornal de Cada Dia, Do Mundo a Lafaiete, Observatório Diário, Xeque-Mate e Terra Brasilis (Brasil e Minas).">
<meta name="theme-color" content="{TINTA}">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Xeque News">
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
h1{{font-family:"Anton",Impact,"Arial Narrow",sans-serif;font-weight:400;font-size:clamp(50px,13.5vw,150px);line-height:.95;text-align:center;margin:12px 0 8px;text-transform:uppercase;letter-spacing:.01em}}
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
h3.tamb{{font-family:"Archivo",Arial,sans-serif;font-weight:800;font-size:13px;letter-spacing:.14em;text-transform:uppercase;text-align:center;margin:8px 4px 10px;padding:8px 0;border-top:2px solid var(--tinta);border-bottom:1px solid var(--tinta)}}
a.outro{{display:flex;gap:12px;align-items:center;text-decoration:none;color:inherit;padding:10px 6px;margin:0 4px;border-bottom:1px solid var(--fio);min-height:56px}}
a.outro img{{width:44px;height:44px;flex:none;border:1px solid var(--tinta)}}
a.outro span{{font-style:italic;font-size:17px;line-height:1.3;color:var(--suave)}}
a.outro b{{font-family:"Playfair Display",Georgia,serif;font-style:normal;font-weight:700;color:var(--tinta);text-transform:uppercase;margin-right:4px}}
a.outro:hover,a.outro:focus-visible{{background:rgba(255,255,255,.4)}}
@media (max-width:420px){{.linha .larga{{display:none}} a.pub{{padding:14px 12px;gap:12px}} a.pub img{{width:64px;height:64px}} a.pub i{{display:none}}}}
</style>
</head>
<body>
<div class="wrap">
  <div class="duplo"></div>
  <h1>Xeque News</h1>
  <div class="duplo inv"></div>
  <div class="linha"><span>{len(cards)} jornais</span><span>✱</span><span class="larga">Edição todo dia</span><span class="larga">✱</span><span>{hoje.strftime('%d/%m/%Y')}</span></div>
  <h2>Escolha o seu jornal</h2>
  <p class="sub">Toque num jornal para ler a edição de hoje.</p>
{chr(10).join(itens)}
  {('<h3 class="tamb">Também no Xeque News</h3>' + chr(10) + chr(10).join(outros)) if outros else ""}
  {('<h3 class="tamb">Dossiês de estudo</h3>' + chr(10) + chr(10).join(f'  <a class="outro" href="{p}/"><img src="{p}/icone-192.png" alt="" width="44" height="44"><span><b>{H.escape(n)}</b> {H.escape(ds)}</span></a>' for p, _, n, ds in DOSSIES)) if DOSSIES else ""}
  <h3 class="tamb">Fontes e compromisso editorial</h3>
  <a class="outro" href="fontes/"><span><b>Sem partido, com fonte</b> Todos os jornais seguem a mesma linha: nenhum vínculo com partido ou governo, fato separado de opinião, os dois lados, cada notícia com fonte, link e data, e erros corrigidos às claras. Veja as fontes de cada jornal.</span></a>
  <div class="caixa">"Cada página impressa aproximava o mundo"</div>
  <p class="nota">Para ter o Xeque News como aplicativo no celular: no Android, abra no Chrome, toque nos três pontinhos e em "Instalar app" ou "Adicionar à tela inicial"; no iPhone, abra no Safari, toque em Compartilhar e em "Adicionar à Tela de Início". Depois da primeira visita, os jornais abrem até sem internet. Textos escritos com a ajuda do Claude, IA da Anthropic; não substituem orientação médica.</p>
</div>
{REGISTRO.replace("{raiz}", "./")}
</body>
</html>
"""

cards = []
for pasta, origem, nome, desc, opts in PUBS:
    manchete, dt = montar(pasta, origem, nome, desc, opts)
    if not opts.get("oculto"):
        cards.append((pasta, nome, desc, manchete, dt, opts.get("destaque", False)))

for args in DOSSIES:
    montar_dossie(*args)

# página "Fontes e compromisso editorial", ligada na barra de cada jornal e na tela inicial
_f = os.path.join(BANCA, "fontes")
os.makedirs(_f, exist_ok=True)
_corpo = FONTES.replace('<div class="wrap">', '</head>\n<body>' + BARRA.replace("{nome}", "Fontes e compromisso") + '<div class="wrap">', 1)
open(os.path.join(_f, "index.html"), "w", encoding="utf-8").write(
    CABECA.format(desc="As fontes de referência dos jornais do Xeque News e o compromisso editorial: sem partido, fato separado de opinião, os dois lados, correção pública.", tinta=TINTA, raiz="../")
    + com_rainha(_corpo + "\n" + COMPROMISSO.replace("<details>", "<details open>")) + REGISTRO.replace("{raiz}", "../") + "</body>\n</html>\n")
print("fontes: atualizado")

open(os.path.join(BANCA, "index.html"), "w", encoding="utf-8").write(tela_inicial(cards))

# caminhos antigos que mudaram de nome: redirecionam e desligam o service worker velho
REDIRECIONA = {"anamnese": "xequemate"}
GUARDA_JSON = {}
for velho, novo in REDIRECIONA.items():
    d = os.path.join(BANCA, velho)
    if os.path.isdir(d):
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
    os.makedirs(d, exist_ok=True)
    if velho in GUARDA_JSON and os.path.exists(os.path.join(ORIGEM, GUARDA_JSON[velho])):
        txt = open(os.path.join(ORIGEM, GUARDA_JSON[velho]), encoding="utf-8").read()
        json.loads(txt)
        open(os.path.join(d, "edicoes.json"), "w", encoding="utf-8").write(txt)
    alvo = "../" + novo if "#" in novo else "../" + novo + "/"
    js = f'location.replace("{alvo}")' if "#" in novo else f'location.replace("{alvo}"+location.search+location.hash)'
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(
        f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Mudou de endereço</title>'
        f'<meta http-equiv="refresh" content="0; url={alvo}"><link rel="canonical" href="{alvo}">'
        f'<script>{js}</script></head>'
        f'<body style="background:{PAPEL};color:{TINTA};font:18px Georgia,serif;padding:24px">'
        f'<p>Este jornal mudou de endereço: <a href="{alvo}" style="color:inherit">abrir</a>.</p></body></html>\n')
    open(os.path.join(d, "sw.js"), "w", encoding="utf-8").write(SW_ANTIGO)

manifest = {
    "name": "Xeque News", "short_name": "Xeque News",
    "description": "Os jornais do dia num só lugar: Jornal de Cada Dia, Do Mundo a Lafaiete, Observatório Diário, Xeque-Mate e Terra Brasilis (Brasil e Minas).",
    "lang": "pt-BR", "id": "/banca/", "start_url": "./", "scope": "./",
    "display": "standalone", "orientation": "portrait",
    "background_color": PAPEL, "theme_color": TINTA,
    "icons": [
        {"src": "icone-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icone-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icone-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
    "shortcuts": [{"name": nome, "url": f"{pasta}/", "icons": [{"src": f"{pasta}/icone-192.png", "sizes": "192x192"}]}
                  for pasta, _, nome, _, opts in PUBS if opts.get("destaque")],
}
open(os.path.join(BANCA, "manifest.webmanifest"), "w", encoding="utf-8").write(
    json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

base = ["./", "index.html", "manifest.webmanifest"] + ICONES
for pasta, _, _, _, opts in PUBS:
    base += [f"{pasta}/", f"{pasta}/index.html", f"{pasta}/edicoes.json", f"{pasta}/icone-192.png"]
    base += [f"{pasta}/{x}" for x in opts.get("extras", {})]
base += ["fontes/", "fontes/index.html"]
for pasta, *_ in DOSSIES:
    base += [f"{pasta}/", f"{pasta}/index.html", f"{pasta}/icone-192.png"]
h = hashlib.sha256()
for rel in base:
    p = os.path.join(BANCA, rel if not rel.endswith("/") else rel + "index.html")
    if os.path.exists(p):
        h.update(open(p, "rb").read())
versao = h.hexdigest()[:10]
open(os.path.join(BANCA, "sw.js"), "w", encoding="utf-8").write(
    SW.format(versao=versao, base=json.dumps(base, ensure_ascii=False)))
print(f"banca: versão {versao}")
