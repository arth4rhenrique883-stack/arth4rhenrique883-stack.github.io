/* Service worker da Banca: O Carijó. Versão gerada automaticamente. */
const V = "f8a4a3045a";
const CACHE = "banca-lafaiete-" + V;
const BASE = ["./", "index.html", "edicoes.json", "manifest.webmanifest",
  "icone-180.png", "icone-192.png", "icone-512.png", "icone-maskable-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(
    ks.filter(k => k.startsWith("banca-lafaiete-") && k !== CACHE).map(k => caches.delete(k))
  )).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  // Fontes do Google: guarda a primeira vez e reaproveita (funciona sem internet).
  if (url.hostname.endsWith("fonts.googleapis.com") || url.hostname.endsWith("fonts.gstatic.com")) {
    e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => {
      const c = res.clone(); caches.open(CACHE).then(k => k.put(req, c)); return res;
    })));
    return;
  }
  if (url.origin !== location.origin) return;
  // Página e edições: tenta a internet primeiro (edição do dia); sem rede, usa a cópia guardada.
  e.respondWith(fetch(req, {cache: "no-store"}).then(res => {
    if (res.ok) { const c = res.clone(); caches.open(CACHE).then(k => k.put(req, c)); }
    return res;
  }).catch(() => caches.match(req, {ignoreSearch: true}).then(r => r || caches.match("index.html"))));
});
