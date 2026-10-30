// xmR: guarda o app inteiro (páginas, apostilas, dados e imagens dos slides) para funcionar sem internet.
// Gerado por app/offline.py. Ao publicar uma versão nova, troque o número abaixo.
const V = "medaj-v27";
const MIDIA = "medasr-midia";
const CORE = ["./", "bloco1.html", "bloco2.html", "icon-180.png", "icon-192.png", "icon-512.png", "index.html", "manifest.webmanifest", "marca6-180.png", "marca6-192.png", "marca6-512.png"];
const IMGS = [];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(V).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
async function baixarMidia(){
  const c = await caches.open(MIDIA);
  for (const u of IMGS) { try { if (!(await c.match(u))) { const r = await fetch(u); if (r.ok) await c.put(u, r); } } catch (e) {} }
}
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V && k !== MIDIA).map(k => caches.delete(k)))).then(() => self.clients.claim()));
  baixarMidia();
});
self.addEventListener("message", e => { if (e.data === "midia") baixarMidia(); });
self.addEventListener("fetch", e => {
  const r = e.request;
  if (r.method !== "GET") return;
  const u = new URL(r.url);
  // página: rede primeiro (pega a versão nova), cache se estiver sem internet
  if (r.mode === "navigate") {
    e.respondWith(fetch(r).then(res => { const cp = res.clone(); caches.open(V).then(c => c.put(r, cp)); return res; })
      .catch(() => caches.match(r, {ignoreSearch: true}).then(h => h || caches.match(u.pathname.endsWith("/") ? u.pathname + "index.html" : u.pathname, {ignoreSearch: true}))
        .then(h => h || caches.match("index.html"))));
    return;
  }
  // arquivos do app e fontes do Google: cache primeiro (inclui o cache das imagens)
  if (u.origin === location.origin || u.hostname.endsWith("fonts.googleapis.com") || u.hostname.endsWith("fonts.gstatic.com")) {
    e.respondWith(caches.match(r, {ignoreSearch: true}).then(hit => hit || fetch(r).then(res => {
      if (res.ok || res.type === "opaque") { const cp = res.clone(); caches.open(/\.(webp|png|jpe?g|gif|svg)$/i.test(u.pathname) && u.origin === location.origin ? MIDIA : V).then(c => c.put(r, cp)); }
      return res;
    })));
  }
});
