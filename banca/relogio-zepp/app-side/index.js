// Roda no celular, dentro do app Zepp: busca o resumo do dia na internet e entrega ao relógio.
import { BaseSideService } from "@zeppos/zml/base-side";

const URL = "https://arth4rhenrique883-stack.github.io/banca/relogio.json";

async function buscar(res) {
  try {
    const r = await fetch({ url: URL + "?t=" + Date.now(), method: "GET", headers: { "Cache-Control": "no-cache" } });
    if (r && r.status && r.status !== 200) throw new Error("HTTP " + r.status);
    const corpo = typeof r.body === "string" ? JSON.parse(r.body) : r.body;
    if (!corpo || !corpo.jornais) throw new Error("resposta vazia");
    res(null, { ok: true, dados: corpo });
  } catch (e) {
    res(null, { ok: false, erro: String((e && e.message) || e) });
  }
}

AppSideService(
  BaseSideService({
    onInit() {},
    onRequest(req, res) {
      if (req.method === "RELOGIO") buscar(res);
    },
    onRun() {},
    onDestroy() {},
  })
);
