// Um jornal: chapéu, manchete, resumo da capa e as chamadas do dia, numa folha rolável.
import { Folha, ANTON, SUAVE, ler } from "../comum/papel";

let qual = "";

Page({
  onInit(p) {
    qual = String(p || "");
  },
  build() {
    const dados = ler();
    const j = dados && dados.jornais ? dados.jornais.filter((x) => x.id === qual)[0] : null;
    const f = Folha();
    if (!j) {
      f.texto("Edição não encontrada. Volte e abra de novo.", { tam: 30, centro: true });
      f.pintar();
      return;
    }
    f.texto(String(j.jornal).toUpperCase(), { tam: 26, centro: true, depois: 4 });
    f.texto(("Nº " + j.numero + " · " + j.quando).toUpperCase(), { tam: 20, centro: true, cor: SUAVE, depois: 10 });
    f.filete(true);
    if (j.chapeu) f.texto(String(j.chapeu).toUpperCase(), { tam: 22, cor: SUAVE, depois: 4 });
    f.texto(j.manchete, { tam: 44, fonte: ANTON, depois: 12 });
    f.texto(j.resumo, { tam: 30, depois: 16 });
    f.filete(true);
    (j.itens || []).forEach((it) => {
      if (it.r) f.texto(String(it.r).toUpperCase(), { tam: 20, cor: SUAVE, depois: 2 });
      f.texto(it.t, { tam: 30, depois: 10 });
      f.filete(false);
    });
    if (j.numeros && j.numeros.length) {
      f.texto("OS NÚMEROS", { tam: 34, fonte: ANTON, centro: true, depois: 6 });
      j.numeros.forEach((n) => {
        f.texto(String(n.r).toUpperCase(), { tam: 20, cor: SUAVE, depois: 0 });
        f.texto(n.v, { tam: 40, fonte: ANTON, depois: 0 });
        if (n.n) f.texto(n.n, { tam: 22, cor: SUAVE, depois: 8 });
      });
      f.filete(true);
    }
    if (j.agenda && j.agenda.length) {
      f.texto("AGENDA", { tam: 34, fonte: ANTON, centro: true, depois: 6 });
      j.agenda.forEach((g) => {
        f.texto(String(g.q).toUpperCase(), { tam: 20, cor: SUAVE, depois: 0 });
        f.texto(g.o, { tam: 26, depois: 8 });
      });
      f.filete(true);
    }
    if (j.pensar) {
      f.texto("PARA PENSAR", { tam: 34, fonte: ANTON, centro: true, depois: 6 });
      f.texto(j.pensar, { tam: 28, depois: 10 });
      f.filete(true);
    }
    f.espaco(6);
    f.texto("O jornal inteiro, com as fontes, está no celular.", { tam: 22, centro: true, cor: SUAVE });
    f.texto("XEQUE NEWS", { tam: 30, fonte: ANTON, centro: true });
    f.pintar();
  },
});
