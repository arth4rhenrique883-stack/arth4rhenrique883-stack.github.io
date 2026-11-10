/* Service worker único da Banca. Versão gerada automaticamente pelo montar.py. */
const V = "29e74748eb";
const CACHE = "banca-" + V;
const BASE = ["./", "index.html", "manifest.webmanifest", "icone-180.png", "icone-192.png", "icone-512.png", "icone-maskable-512.png", "jornal/", "jornal/index.html", "jornal/edicoes.json", "jornal/icone-192.png", "mundo-lafaiete/", "mundo-lafaiete/index.html", "mundo-lafaiete/edicoes.json", "mundo-lafaiete/icone-192.png", "observatorio/", "observatorio/index.html", "observatorio/edicoes.json", "observatorio/icone-192.png", "observatorio/brasil.json", "xequemate/", "xequemate/index.html", "xequemate/edicoes.json", "xequemate/icone-192.png", "brasil/", "brasil/index.html", "brasil/edicoes.json", "brasil/icone-192.png", "lafaiete/", "lafaiete/index.html", "lafaiete/edicoes.json", "lafaiete/icone-192.png", "fontes/", "fontes/index.html", "caso-master/", "caso-master/index.html", "caso-master/icone-192.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(
    ks.filter(k => k.startsWith("banca-") && k !== CACHE).map(k => caches.delete(k))
  )).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  // Fontes do Google: guarda na primeira vez e reaproveita (funciona sem internet).
  if (url.hostname.endsWith("fonts.googleapis.com") || url.hostname.endsWith("fonts.gstatic.com")) {
    e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => {
      const c = res.clone(); caches.open(CACHE).then(k => k.put(req, c)); return res;
    })));
    return;
  }
  if (url.origin !== location.origin) return;
  // Páginas e edições: internet primeiro (edição do dia); sem rede, a cópia guardada.
  e.respondWith(fetch(req, {cache: "no-store"}).then(res => {
    if (res.ok) { const c = res.clone(); caches.open(CACHE).then(k => k.put(req, c)); }
    return res;
  }).catch(() => caches.match(req, {ignoreSearch: true}).then(r => r || caches.match("./"))));
});
