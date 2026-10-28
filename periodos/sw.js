// medaj. períodos: guarda o app e as fontes para abrir sem internet.
// Ao publicar uma versão nova do index.html, troque o número abaixo.
const V = "periodos-v12";
const CORE = ["./", "index.html", "p6.html", "p7.html", "p8.html", "manifest.webmanifest", "chama2-192.png", "chama2-512.png", "chama2-180.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(V).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const r = e.request;
  if (r.method !== "GET") return;
  const u = new URL(r.url);
  // página: rede primeiro (pega versão nova), cache se estiver sem internet
  if (r.mode === "navigate") {
    e.respondWith(fetch(r).then(res => { const cp = res.clone(); caches.open(V).then(c => c.put(r, cp)); return res; })
      .catch(() => caches.match(r, {ignoreSearch: true}).then(h => h || caches.match(/\/p[678]\.html$/.test(u.pathname) ? u.pathname.split("/").pop() : "index.html"))));
    return;
  }
  // fontes do Google e arquivos do app: cache primeiro
  if (u.origin === location.origin || u.hostname.endsWith("fonts.googleapis.com") || u.hostname.endsWith("fonts.gstatic.com")) {
    e.respondWith(caches.match(r).then(hit => hit || fetch(r).then(res => {
      if (res.ok || res.type === "opaque") { const cp = res.clone(); caches.open(V).then(c => c.put(r, cp)); }
      return res;
    })));
  }
});
