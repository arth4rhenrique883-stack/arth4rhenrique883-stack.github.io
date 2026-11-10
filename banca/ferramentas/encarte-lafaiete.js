/* Encarte "Conselheiro Lafaiete": acrescenta ao jornal o caderno da cidade, lido do
   O Carijó (../lafaiete/edicoes.json). Montado pelo montar.py; MODO = "jornal" ou "obs". */
(function () {
  var MODO = "{modo}";
  var alvo = document.getElementById(MODO === "obs" ? "edition" : "conteudo");
  if (!alvo) return;
  var dados = null;
  function x(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]; }); }
  function curta(iso) { var p = String(iso || "").split("-"); return p.length === 3 ? p[2] + "/" + p[1] : ""; }
  function dataDaPagina() {
    var el = document.getElementById(MODO === "obs" ? "issue-date" : "dataCurta");
    var m = el ? el.textContent.match(/(\d{2})\/(\d{2})\/(\d{4})/) : null;
    return m ? m[3] + "-" + m[2] + "-" + m[1] : "";
  }
  function escolhe(iso) {
    var eds = ((dados && dados.edicoes) || []).slice().sort(function (a, b) { return String(b.data).localeCompare(String(a.data)); });
    if (!eds.length) return null;
    if (!iso) return eds[0];
    for (var i = 0; i < eds.length; i++) if (String(eds[i].data) <= iso) return eds[i];
    // Carijó só mais novo: usa o mais antigo se a diferença for de até 2 dias; senão, sem encarte
    var ult = eds[eds.length - 1], dif = (Date.parse(ult.data) - Date.parse(iso)) / 864e5;
    return dif <= 2 ? ult : null;
  }
  function links(fs, jornal) {
    if (!fs || !fs.length) return "";
    var a = fs.map(function (f) { return '<a href="' + x(f.url) + '" target="_blank" rel="noopener">' + x(f.nome) + "</a>"; }).join("");
    return jornal ? '<div class="fontes"><span>Fonte:</span>' + a + "</div>" : '<span class="srcs">' + a + "</span>";
  }
  function htmlJornal(e) {
    var h = '<section class="caderno encarte-lafaiete" id="lafaiete" aria-label="Conselheiro Lafaiete">'
      + '<hr class="duplo"><div class="secao-cab"><h2>Conselheiro Lafaiete</h2><p>A nossa cidade, com as notícias do jornal O Carijó de ' + x(curta(e.data)) + ". " + x((e.capa || {}).titulo) + "</p></div><hr class=\"duplo inv\">"
      + '<div class="colunas">';
    (e.cadernos || []).forEach(function (cd) {
      h += '<h3 class="frente">' + x(cd.titulo) + "</h3>";
      if (cd.aviso) h += '<div class="aviso">' + x(cd.aviso) + "</div>";
      (cd.itens || []).forEach(function (it) {
        h += '<article class="item"><h3 class="titulo-caps">' + x(it.titulo) + "</h3>" + (it.selo ? '<span class="selo ' + x(it.selo) + '">' + x(it.selo) + "</span>" : "")
          + '<p class="it">' + x(it.texto) + "</p>" + links(it.fontes, true) + "</article>";
      });
      if (cd.caixa) h += '<aside class="caixa"><h4>' + x(cd.caixa.titulo) + '</h4><p class="it">' + x(cd.caixa.texto) + "</p></aside>";
    });
    var t = e.tempo;
    if (t) h += '<aside class="caixa"><h4>O tempo em Lafaiete</h4><p class="it">' + x(t.texto) + '</p><ul class="dicas">'
      + (t.dias || []).map(function (d) { return "<li>" + x(d.dia) + ": " + x(d.min) + "° a " + x(d.max) + "°, " + x(d.ceu) + "</li>"; }).join("") + "</ul>" + links(t.fontes, true) + "</aside>";
    return h + "</div></section>";
  }
  function htmlObs(e) {
    var h = '<section class="caderno encarte-lafaiete" id="lafaiete" aria-label="Conselheiro Lafaiete">'
      + '<hr class="dbl"><div class="cad-head"><div class="cad-tag">Conselheiro Lafaiete</div><h2>A nossa cidade</h2><p>Do jornal O Carijó, edição de ' + x(curta(e.data)) + ": " + x((e.capa || {}).titulo) + "</p></div>"
      + '<div class="fronts">';
    (e.cadernos || []).forEach(function (cd) {
      h += '<div class="front-col"><h3>' + x(cd.titulo) + "</h3>";
      (cd.itens || []).forEach(function (it) {
        h += '<article class="item"><h4>' + x(it.titulo) + "</h4><p>" + x(it.texto) + '</p><div class="foot">'
          + (it.selo ? '<span class="conf">' + x(it.selo) + "</span>" : "") + links(it.fontes, false) + "</div></article>";
      });
      h += "</div>";
    });
    h += "</div>";
    var t = e.tempo;
    if (t) h += '<aside class="box"><p class="bt">O tempo em Lafaiete</p><dl>'
      + (t.dias || []).map(function (d) { return "<dt>" + x(d.dia) + "</dt><dd>" + x(d.min) + "° a " + x(d.max) + "°, " + x(d.ceu) + "</dd>"; }).join("")
      + "</dl></aside>";
    return h + "</section>";
  }
  var ocupado = false;
  function insere() {
    if (!dados || ocupado || alvo.querySelector(".encarte-lafaiete")) return;
    var e = escolhe(dataDaPagina());
    if (!e) return;
    ocupado = true;
    var html = MODO === "obs" ? htmlObs(e) : htmlJornal(e);
    var ref = alvo.querySelector(MODO === "obs" ? "section.trio" : "section.fim");
    if (ref && ref.previousElementSibling && /\b(dbl|duplo)\b/.test(ref.previousElementSibling.className)) ref = ref.previousElementSibling;
    if (ref) ref.insertAdjacentHTML("beforebegin", html); else alvo.insertAdjacentHTML("beforeend", html);
    var toc = document.getElementById("toc");
    if (MODO === "obs" && toc && !toc.hidden && !toc.querySelector('a[href="#lafaiete"]')) toc.insertAdjacentHTML("beforeend", '<a href="#lafaiete">Lafaiete</a>');
    ocupado = false;
  }
  new MutationObserver(insere).observe(alvo, {childList: true});
  fetch("../lafaiete/edicoes.json", {cache: "no-store"}).then(function (r) { return r.json(); })
    .then(function (d) { dados = d; insere(); }).catch(function () {});
})();
