// Um baralho: mostra a frente da carta; "Ver resposta" vira; "Sabia" ou "Não sabia" passa à próxima.
// As cartas que você ainda não sabe vêm primeiro. O que você marcou fica guardado no relógio.
import { scrollTo } from "@zos/page";
import { BasePage } from "@zeppos/zml/base-page";
import { Folha, ANTON, GOTICA, ITALICA, SUAVE, ler, guardar } from "../comum/papel";

let id = "";
let folha = null;
let fila = [];
let pos = 0;
let sabidas = [];
let nome = "";

function topo() {
  try { scrollTo({ y: 0 }); } catch (e) {}
}

function folhaNova() {
  if (folha) folha.apagar();
  folha = Folha();
  folha.texto(nome, { tam: 40, fonte: GOTICA, centro: true, depois: 0 });
  return folha;
}

function aviso(t) {
  const f = folhaNova();
  f.filete(true);
  f.texto(t, { tam: 30, centro: true, cor: SUAVE });
  f.pintar();
  topo();
}

function embaralha(a) {
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    const t = a[i]; a[i] = a[j]; a[j] = t;
  }
  return a;
}

function comecar(cartas) {
  sabidas = ler("sabe-" + id) || [];
  let falta = cartas.filter((c) => sabidas.indexOf(c.k) < 0);
  if (!falta.length) falta = cartas.slice(); // sabia todas desta remessa: revê assim mesmo
  fila = embaralha(falta);
  pos = 0;
  frente();
}

function frente() {
  if (pos >= fila.length) return fim();
  const c = fila[pos];
  const f = folhaNova();
  f.texto("CARTA " + (pos + 1) + " DE " + fila.length, { tam: 20, centro: true, cor: SUAVE, depois: 8 });
  f.filete(true);
  f.texto(c.f, { tam: 34, depois: 18 });
  f.estrelas();
  f.botao("VER RESPOSTA", () => verso());
  f.pintar();
  topo();
}

function verso() {
  const c = fila[pos];
  const f = folhaNova();
  f.texto(c.f, { tam: 24, cor: SUAVE, fonte: ITALICA, depois: 10 });
  f.filete(true);
  f.texto(c.v, { tam: 32, depois: 18 });
  f.botao("SABIA", () => {
    if (sabidas.indexOf(c.k) < 0) sabidas.push(c.k);
    guardar("sabe-" + id, sabidas);
    pos++; frente();
  });
  f.botao("NÃO SABIA", () => { pos++; frente(); });
  f.pintar();
  topo();
}

function fim() {
  const f = folhaNova();
  f.filete(true);
  f.texto("FIM DA RODADA", { tam: 44, fonte: ANTON, centro: true, depois: 10 });
  f.texto("Você já marcou " + sabidas.length + " cartas como sabidas neste baralho. Abra de novo para receber outras.", { tam: 30, centro: true, depois: 16 });
  f.botao("OUTRA RODADA", () => comecar(ler("cartas-" + id) || []));
  f.pintar();
  topo();
}

Page(
  BasePage({
    onInit(p) {
      id = String(p || "");
      const b = (ler("baralhos") || []).filter((x) => x.id === id)[0];
      nome = b ? b.nome : "Flashcards";
    },
    build() {
      const guardadas = ler("cartas-" + id);
      if (guardadas && guardadas.length) comecar(guardadas);
      else aviso("Buscando as cartas pelo celular…");
      this.request({ method: "CARTAS", params: { id, sabe: ler("sabe-" + id) || [] } })
        .then((r) => {
          if (r && r.ok && r.cartas && r.cartas.length) {
            // guarda sempre a remessa nova: a próxima rodada já usa cartas novas
            guardar("cartas-" + id, r.cartas);
            if (!guardadas || !guardadas.length) comecar(r.cartas);
          } else if (!guardadas) {
            aviso("Não consegui buscar as cartas. Confira a internet do celular e abra de novo.");
          }
        })
        .catch(() => {
          if (!guardadas) aviso("Sem ligação com o celular. Abra o app Zepp no telefone e tente de novo.");
        });
    },
    onDestroy() {
      folha = null;
    },
  })
);
