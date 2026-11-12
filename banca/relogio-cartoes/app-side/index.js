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
            if (!b) return res(null, { ok: false, erro: "baralho não encontrado" });
            // Baralhos grandes (8º período): manda 40 por vez, primeiro as que o relógio ainda não marcou
            // como sabidas, para a transferência por Bluetooth ser rápida.
            const sabe = (req.params && req.params.sabe) || [];
            let cartas = b.cartas;
            if (cartas.length > 40) {
              const falta = cartas.filter((x) => sabe.indexOf(x.k) < 0);
              const base = falta.length >= 40 ? falta : falta.concat(cartas.filter((x) => sabe.indexOf(x.k) >= 0));
              cartas = base.map((x) => [Math.random(), x]).sort((p, q) => p[0] - q[0]).slice(0, 40).map((p) => p[1]);
            }
            res(null, { ok: true, cartas, total: b.cartas.length });
          })
          .catch(erro);
      }
    },
    onRun() {},
    onDestroy() {},
  })
);
