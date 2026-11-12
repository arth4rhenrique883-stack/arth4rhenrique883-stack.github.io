// Capa: o nome da casa, a data e a manchete de cada jornal. Tocar no nome do jornal abre o resumo.
import { push } from "@zos/router";
import { BasePage } from "@zeppos/zml/base-page";
import { Folha, ANTON, ITALICA, SUAVE, ler, guardar } from "../comum/papel";

let folha = null;

function capa(dados, aviso) {
  if (folha) folha.apagar();
  const f = (folha = Folha());
  const d0 = dados && dados.jornais && dados.jornais[0] ? dados.jornais[0].quando : "";
  f.cabeca("Xeque News", "Ano I ✱ " + (d0 ? "Edição de " + d0 : "Edição do dia"));
  if (!dados || !dados.jornais || !dados.jornais.length) {
    f.texto(aviso || "Buscando as edições do dia pelo celular…", { tam: 30, centro: true, cor: SUAVE });
    f.pintar();
    return;
  }
  const letras = "ABCDEFGH";
  dados.jornais.forEach((j, k) => {
    f.texto("Caderno " + letras[k] + " · " + j.jornal, { tam: 22, centro: true, cor: SUAVE, fonte: ITALICA, depois: 4 });
    f.botao(String(j.aba || j.jornal).toUpperCase(), () => push({ url: "page/ler", params: j.id }));
    f.texto(j.manchete, { tam: 34, fonte: ANTON, depois: 4 });
    if (j.quando) f.texto("Edição de " + j.quando, { tam: 22, cor: SUAVE, fonte: ITALICA, depois: 8 });
    f.estrelas();
  });
  f.texto(aviso || "O jornal inteiro está no celular.", { tam: 22, centro: true, cor: SUAVE });
  f.pintar();
}

Page(
  BasePage({
    build() {
      const guardado = ler("xeque-relogio");
      capa(guardado);
      this.request({ method: "RELOGIO" })
        .then((r) => {
          if (r && r.ok && r.dados) {
            const mudou = JSON.stringify(r.dados) !== JSON.stringify(guardado);
            guardar("xeque-relogio", r.dados);
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
