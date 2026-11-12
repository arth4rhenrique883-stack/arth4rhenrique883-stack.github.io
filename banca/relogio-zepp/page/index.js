// Capa: o nome da casa, a data e a manchete de cada jornal. Tocar no nome do jornal abre o resumo.
import { push } from "@zos/router";
import { BasePage } from "@zeppos/zml/base-page";
import { Folha, ANTON, ITALICA, SUAVE, ler, guardar } from "../comum/papel";

let folha = null;

function capa(dados, aviso, tentar) {
  if (folha) folha.apagar();
  const f = (folha = Folha());
  const d0 = dados && dados.jornais && dados.jornais[0] ? dados.jornais[0].quando : "";
  f.cabeca("Xeque News", "Ano I ✱ " + (d0 ? "Edição de " + d0 : "Edição do dia"));
  if (!dados || !dados.jornais || !dados.jornais.length) {
    f.texto(aviso || "Buscando as edições do dia pelo celular…", { tam: 30, centro: true, cor: SUAVE });
    if (tentar) f.botao("TENTAR DE NOVO", tentar);
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
  if (tentar) f.botao("ATUALIZAR", tentar);
  f.pintar();
}

function agora() {
  const d = new Date();
  return String(d.getHours()).padStart(2, "0") + "h" + String(d.getMinutes()).padStart(2, "0");
}

Page(
  BasePage({
    build() {
      this.atualizar();
    },
    // Busca o resumo do dia pelo celular. Mostra sempre, no pé da capa, se atualizou ou por que não.
    atualizar() {
      const guardado = ler("xeque-relogio");
      capa(guardado, "Buscando a edição do dia pelo celular…", () => this.atualizar());
      this.request({ method: "RELOGIO" })
        .then((r) => {
          if (r && r.ok && r.dados) {
            guardar("xeque-relogio", r.dados);
            capa(r.dados, "Atualizado às " + agora() + ".", () => this.atualizar());
          } else {
            const erro = (r && r.erro) || "resposta vazia";
            capa(guardado, "O celular não conseguiu baixar a edição (" + erro + "). Confira a internet do celular.", () => this.atualizar());
          }
        })
        .catch((e) => {
          capa(guardado, "Sem resposta do celular (" + String((e && e.message) || e || "tempo esgotado") + "). Abra o app Zepp no telefone, com o Bluetooth ligado.", () => this.atualizar());
        });
    },
    onDestroy() {
      folha = null;
    },
  })
);
