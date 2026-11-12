// Capa: o nome da casa, a data e a manchete de cada jornal. Tocar no nome do jornal abre o resumo.
import { push } from "@zos/router";
import { BasePage } from "@zeppos/zml/base-page";
import { Folha, ANTON, SUAVE, ler, guardar } from "../comum/papel";

let folha = null;

function capa(dados, aviso) {
  if (folha) folha.apagar();
  const f = (folha = Folha());
  f.texto("XEQUE NEWS", { tam: 58, fonte: ANTON, centro: true, depois: 6 });
  f.filete(true);
  if (!dados || !dados.jornais || !dados.jornais.length) {
    f.texto(aviso || "Buscando as edições do dia pelo celular…", { tam: 30, centro: true, cor: SUAVE });
    f.pintar();
    return;
  }
  const d = dados.jornais[0].quando;
  f.texto((d ? "Edição de " + d : "Edição do dia").toUpperCase(), { tam: 22, centro: true, cor: SUAVE, depois: 14 });
  dados.jornais.forEach((j) => {
    f.botao(String(j.aba || j.jornal).toUpperCase(), () => push({ url: "page/ler", params: j.id }));
    f.texto(j.manchete, { tam: 30, depois: 4 });
    f.texto(j.jornal + (j.quando ? " · " + j.quando : ""), { tam: 22, cor: SUAVE, depois: 22 });
  });
  f.filete(false);
  f.texto(aviso || "O jornal inteiro está no celular.", { tam: 22, centro: true, cor: SUAVE });
  f.pintar();
}

Page(
  BasePage({
    build() {
      const guardado = ler();
      capa(guardado);
      this.request({ method: "RELOGIO" })
        .then((r) => {
          if (r && r.ok && r.dados) {
            const mudou = JSON.stringify(r.dados) !== JSON.stringify(guardado);
            guardar(r.dados);
            if (mudou) capa(r.dados);
          } else if (!guardado) {
            capa(null, "Não consegui buscar as edições. Confira a internet do celular e abra de novo.");
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
