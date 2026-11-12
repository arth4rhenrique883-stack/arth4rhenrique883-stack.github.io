// Roda no celular, dentro do app Zepp: busca os flashcards na internet e entrega ao relógio,
// um baralho por vez (pacotes pequenos, porque o Bluetooth do relógio é lento).
import { BaseSideService } from "@zeppos/zml/base-side";

const URL = "https://arth4rhenrique883-stack.github.io/banca/cartoes.json";
let cache = null;

async function tudo() {
  if (cache) return cache;
  const r = await fetch({ url: URL + "?t=" + Date.now(), method: "GET" });
  const corpo = typeof r.body === "string" ? JSON.parse(r.body) : r.body;
  if (!corpo || !corpo.baralhos) throw new Error("resposta vazia");
  cache = corpo;
  return corpo;
}

AppSideService(
  BaseSideService({
    onInit() {},
    onRequest(req, res) {
      const erro = (e) => res(null, { ok: false, erro: String((e && e.message) || e) });
      if (req.method === "BARALHOS") {
        cache = null;
        tudo()
          .then((c) => res(null, { ok: true, baralhos: c.baralhos.map((b) => ({ id: b.id, nome: b.nome, de: b.de, n: b.cartas.length })) }))
          .catch(erro);
      } else if (req.method === "CARTAS") {
        const id = req.params && req.params.id;
        tudo()
          .then((c) => {
            const b = c.baralhos.filter((x) => x.id === id)[0];
            res(null, b ? { ok: true, cartas: b.cartas } : { ok: false, erro: "baralho não encontrado" });
          })
          .catch(erro);
      }
    },
    onRun() {},
    onDestroy() {},
  })
);
