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
    f.espaco(6);
    f.texto("O jornal inteiro, com as fontes, está no celular.", { tam: 22, centro: true, cor: SUAVE });
    f.texto("XEQUE NEWS", { tam: 30, fonte: ANTON, centro: true });
    f.pintar();
  },
});
