// Um jornal: chapéu, manchete, resumo da capa e as chamadas do dia, numa folha rolável.
import { Folha, ANTON, GOTICA, ITALICA, SUAVE, LARGURA, ler } from "../comum/papel";

let qual = "";

Page({
  onInit(p) {
    qual = String(p || "");
  },
  build() {
    const dados = ler("xeque-relogio");
    const j = dados && dados.jornais ? dados.jornais.filter((x) => x.id === qual)[0] : null;
    const f = Folha();
    if (!j) {
      f.texto("Edição não encontrada. Volte e abra de novo.", { tam: 30, centro: true });
      f.pintar();
      return;
    }
    f.cabeca(j.jornal, "Nº " + j.numero + " ✱ " + j.quando);
    if (j.chapeu) f.texto(String(j.chapeu).toUpperCase(), { tam: 22, centro: true, cor: SUAVE, depois: 4 });
    f.texto(j.manchete, { tam: 46, fonte: ANTON, centro: true, depois: 12 });
    f.filete(false, Math.floor(LARGURA / 3));
    f.texto(j.resumo, { tam: 30, fonte: ITALICA, depois: 16 });
    f.filete(true);
    (j.itens || []).forEach((it) => {
      if (it.r) f.texto(String(it.r).toUpperCase(), { tam: 20, cor: SUAVE, depois: 2 });
      f.texto(it.t, { tam: 30, depois: 10 });
      f.filete(false);
    });
    f.estrelas();
    // Seções genéricas: o relógio desenha o que vier no resumo do dia, então seções novas
    // chegam pela internet sem reinstalar o app.
    (j.secoes || []).forEach((sec) => {
      f.texto(String(sec.titulo || ""), { tam: 44, fonte: GOTICA, centro: true, depois: 0 });
      f.filete(false, Math.floor(LARGURA / 3));
      (sec.linhas || []).forEach((l) => {
        if (l.r) f.texto(String(l.r).toUpperCase(), { tam: 20, cor: SUAVE, depois: 0 });
        if (l.g) f.texto(l.g, { tam: 40, fonte: ANTON, depois: 0 });
        if (l.t) f.texto(l.t, { tam: l.g ? 22 : 28, cor: l.g ? SUAVE : undefined, fonte: l.g ? ITALICA : undefined, depois: 8 });
      });
      f.filete(true);
    });
    f.espaco(6);
    f.texto("O jornal inteiro, com as fontes, está no celular.", { tam: 22, centro: true, cor: SUAVE });
    f.texto("Xeque News", { tam: 40, fonte: GOTICA, centro: true });
    f.pintar();
  },
});
