// Desenho de jornal impresso no pulso: papel bege, tinta marrom, filetes duplos, manchete em Anton.
import * as hmUI from "@zos/ui";
import { px } from "@zos/utils";
import { getDeviceInfo } from "@zos/device";
import { LocalStorage } from "@zos/storage";

export const { width: L, height: A } = getDeviceInfo();
export const PAPEL = 0xece3d4;
export const TINTA = 0x111111;
export const SUAVE = 0x47413b;
export const DESTAQUE = 0xa51d1d; // vermelho de manchete, para chamar atenção
export const ANTON = "fonts/Anton.ttf";
export const GOTICA = "fonts/Gotica.ttf"; // UnifrakturMaguntia: o cabeçalho dos jornais antigos
export const SERIFA = "fonts/Serifa.ttf"; // Old Standard TT: letra de texto da imprensa do século XIX
export const ITALICA = "fonts/SerifaItalica.ttf";
export const MARGEM = px(58); // tela redonda: folga dos lados
export const LARGURA = L - 2 * MARGEM;

const guarda = new LocalStorage();
export function ler(CHAVE) {
  try {
    const t = guarda.getItem(CHAVE, "");
    return t ? JSON.parse(t) : null;
  } catch (e) {
    return null;
  }
}
export function guardar(CHAVE, d) {
  try {
    guarda.setItem(CHAVE, JSON.stringify(d));
  } catch (e) {}
}

// Monta uma folha rolável: primeiro mede tudo, depois pinta o papel do tamanho certo e os textos por cima.
export function Folha() {
  const pecas = [];
  let y = px(64);
  const feitos = [];
  return {
    espaco(h) {
      y += px(h);
    },
    texto(t, o = {}) {
      if (!t) return;
      const tam = px(o.tam || 30);
      const w = o.w || LARGURA;
      const fonte = o.fonte === null ? null : o.fonte || SERIFA; // sem indicação: serifa de jornal
      let h = tam * 1.3;
      try {
        // mede com a largura um pouco menor: a serifa é mais larga que a letra do sistema
        const m = hmUI.getTextLayout(String(t), { text_size: tam, text_width: Math.floor(w * (fonte ? 0.86 : 1)), wrap: true });
        if (m && m.height) h = m.height;
      } catch (e) {
        h = Math.ceil((String(t).length * tam * 0.52) / w) * tam * 1.3;
      }
      h = Math.ceil(h + tam * 0.35);
      const p = {
        x: (L - w) / 2, y, w, h,
        text: String(t), text_size: tam, color: o.cor || TINTA,
        align_h: o.centro ? hmUI.align.CENTER_H : hmUI.align.LEFT,
        align_v: hmUI.align.TOP,
        text_style: hmUI.text_style.WRAP,
      };
      if (fonte) p.font = fonte;
      pecas.push([hmUI.widget.TEXT, p]);
      y += h + px(o.depois == null ? 8 : o.depois);
    },
    filete(duplo, w) {
      const lw = w || LARGURA;
      const x = (L - lw) / 2;
      pecas.push([hmUI.widget.FILL_RECT, { x, y, w: lw, h: px(duplo ? 5 : 2), color: TINTA }]);
      y += px(duplo ? 5 : 2);
      if (duplo) {
        y += px(4);
        pecas.push([hmUI.widget.FILL_RECT, { x, y, w: lw, h: px(2), color: TINTA }]);
        y += px(2);
      }
      y += px(12);
    },
    // Cabeçalho de jornal de banca: nome em letra gótica, filete duplo e a linha da edição.
    cabeca(nome, linha) {
      this.texto(nome, { tam: 60, fonte: GOTICA, centro: true, depois: 0 });
      this.filete(true);
      if (linha) this.texto(String(linha).toUpperCase(), { tam: 20, centro: true, cor: DESTAQUE, depois: 0 });
      this.filete(false);
    },
    estrelas() {
      this.texto("✱   ✱   ✱", { tam: 22, centro: true, cor: DESTAQUE, fonte: null, depois: 10 });
    },
    botao(t, aoTocar) {
      const h = px(76);
      pecas.push([hmUI.widget.BUTTON, {
        x: MARGEM, y, w: LARGURA, h, radius: px(4),
        text: t, text_size: px(40), color: PAPEL,
        normal_color: TINTA, press_color: SUAVE, click_func: aoTocar,
      }]);
      y += h + px(10);
    },
    pintar() {
      const total = Math.max(A, y + px(110));
      feitos.push(hmUI.createWidget(hmUI.widget.FILL_RECT, { x: 0, y: 0, w: L, h: total, color: PAPEL }));
      pecas.forEach(([tipo, p]) => feitos.push(hmUI.createWidget(tipo, p)));
    },
    apagar() {
      feitos.forEach((w) => { try { hmUI.deleteWidget(w); } catch (e) {} });
      feitos.length = 0;
    },
  };
}
