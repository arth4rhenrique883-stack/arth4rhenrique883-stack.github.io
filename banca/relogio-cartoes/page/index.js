// Capa: os baralhos do dia. Tocar num baralho abre as cartas.
import { push } from "@zos/router";
import { BasePage } from "@zeppos/zml/base-page";
import { Folha, ANTON, SUAVE, ler, guardar } from "../comum/papel";

let folha = null;

function capa(lista, aviso) {
  if (folha) folha.apagar();
  const f = (folha = Folha());
  f.texto("XEQUE CARDS", { tam: 56, fonte: ANTON, centro: true, depois: 6 });
  f.filete(true);
  if (!lista || !lista.length) {
    f.texto(aviso || "Buscando os flashcards pelo celular…", { tam: 30, centro: true, cor: SUAVE });
    f.pintar();
    return;
  }
  f.texto("ESCOLHA O BARALHO", { tam: 22, centro: true, cor: SUAVE, depois: 14 });
  lista.forEach((b) => {
    const sabidas = (ler("sabe-" + b.id) || []).length;
    f.botao(String(b.nome).toUpperCase(), () => push({ url: "page/carta", params: b.id }));
    f.texto(b.n + " cartas · " + Math.min(sabidas, b.n) + " sabidas", { tam: 24, centro: true, depois: 2 });
    f.texto(b.de, { tam: 22, centro: true, cor: SUAVE, depois: 20 });
  });
  f.filete(false);
  f.texto(aviso || "Perguntas e termos tirados dos jornais do Xeque News.", { tam: 22, centro: true, cor: SUAVE });
  f.pintar();
}

Page(
  BasePage({
    build() {
      const guardado = ler("baralhos");
      capa(guardado);
      this.request({ method: "BARALHOS" })
        .then((r) => {
          if (r && r.ok && r.baralhos) {
            guardar("baralhos", r.baralhos);
            if (JSON.stringify(r.baralhos) !== JSON.stringify(guardado)) capa(r.baralhos);
          } else if (!guardado) {
            capa(null, "Não consegui buscar os flashcards. Confira a internet do celular e abra de novo.");
          }
        })
        .catch(() => {
          if (!guardado) capa(null, "Sem ligação com o celular. Abra o app Zepp no telefone e tente de novo.");
        });
    },
    onDestroy() {
      folha = null;
    },
  })
);
