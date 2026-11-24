#!/usr/bin/env python3
"""ckp · design premium (24/11/2026). Idempotente: pode rodar de novo depois de qualquer build.

Uso:  python3 ferramentas/design-ckp.py            (a partir da raiz do repositório Pages)
Faz, em periodos/index.html, p1..p8.html e nos leitores primeiro|sexto|oitavo/index.html:
  1. letra C do nome em verde e K em azul (cores da faculdade, discretas);
  2. bloco <!--ckp-->…<!--/ckp--> antes de </body>: CSS e JS (cliques animados, janela "Sobre o app",
     escolha de ciclo, aura sutil);
  3. no início (index.html): escolha "Ciclo básico" (1º–5º) ou "Ciclo clínico" (6º–8º) antes dos períodos.
Não mexe em sw.js (trocar a versão à parte).
"""
import re, sys, pathlib

RAIZ = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
P = RAIZ / "periodos"
ALVOS = ["index.html"] + [f"p{i}.html" for i in range(1, 9)] + ["primeiro/index.html", "sexto/index.html", "oitavo/index.html"]

CSS = r"""
:root{--ck-verde:#3CC48E;--ck-azul:#4F96EA;--ck-verde-s:rgba(60,196,142,.16);--ck-azul-s:rgba(79,150,234,.16)}
/* nome: C verde, K azul */
.asmed .t .ck-c,.asmed .t .ck-k{font-style:normal}
.asmed .t .ck-c{color:var(--ck-verde)!important;text-shadow:0 0 14px rgba(60,196,142,.35),0 1px 0 #0d2a20}
.asmed .t .ck-k{color:var(--ck-azul)!important;text-shadow:0 0 14px rgba(79,150,234,.35),0 1px 0 #0d1c33}
/* aura discreta ao fundo */
.ck-aura{position:fixed;inset:0;z-index:-1;pointer-events:none;background:radial-gradient(60% 40% at 8% 96%,rgba(60,196,142,.075),transparent 70%),radial-gradient(60% 40% at 94% 6%,rgba(79,150,234,.08),transparent 70%)}
/* linha fina verde→azul sob o nome */
.brand .app-name{position:relative;padding-bottom:9px}
.brand .app-name::after{content:"";position:absolute;left:50%;bottom:0;width:44px;height:2px;margin-left:-22px;border-radius:2px;background:linear-gradient(90deg,var(--ck-verde),var(--ck-azul));opacity:.75}
/* nome e rainha clicáveis */
.xm-canto,.asmed{cursor:pointer;-webkit-tap-highlight-color:transparent}
.xm-canto{transition:opacity .2s,transform .25s ease,box-shadow .2s;border-radius:10px}
.xm-canto:hover,.xm-canto:focus-visible{opacity:1!important}
.xm-canto:active .xm-mini,.asmed:active{transform:scale(.94)}
.xm-canto:focus-visible,.asmed:focus-visible{outline:2px solid var(--ck-azul)!important;outline-offset:4px!important}
/* escolha de ciclo */
.ck-ciclos{display:none;flex-direction:column;gap:12px;width:min(340px,100%);margin:-6px auto 0}
body.ini:not([data-ciclo]) .ck-ciclos{display:flex}
body.ini:not([data-ciclo]) nav.pers,body.ini:not([data-ciclo]) .soon{display:none!important}
.ck-card{position:relative;display:grid;grid-template-columns:1fr auto;grid-template-areas:"t s" "d d";align-items:center;gap:4px 12px;text-align:left;padding:18px 18px 16px;border-radius:16px;border:1px solid #1d2326;background:linear-gradient(180deg,#0c0f11,#080a0b);color:var(--fg);cursor:pointer;overflow:hidden;
 box-shadow:0 10px 26px -16px rgba(0,0,0,.9);transition:transform .2s cubic-bezier(.2,.7,.2,1),border-color .2s,box-shadow .25s;-webkit-tap-highlight-color:transparent;touch-action:manipulation}
.ck-card::before{content:"";position:absolute;left:0;top:14px;bottom:14px;width:3px;border-radius:0 3px 3px 0;background:var(--cc)}
.ck-card[data-ciclo=basico]{--cc:var(--ck-verde);--cs:var(--ck-verde-s)}
.ck-card[data-ciclo=clinico]{--cc:var(--ck-azul);--cs:var(--ck-azul-s)}
.ck-card .ck-t{grid-area:t;font:700 17px/1.2 Lato,system-ui,sans-serif;letter-spacing:.02em;color:#f1f1f1}
.ck-card .ck-s{grid-area:s;font:500 11px/1 Lato,system-ui,sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--cc);opacity:.95;white-space:nowrap}
.ck-card .ck-d{grid-area:d;display:flex;align-items:center;gap:6px;margin-top:8px}
.ck-card .ck-d i{width:9px;height:9px;border-radius:50%;background:var(--c);box-shadow:0 0 0 3px color-mix(in srgb,var(--c) 14%,transparent)}
.ck-card .ck-d span{margin-left:auto;font:400 11.5px/1.3 Lato,system-ui,sans-serif;color:var(--muted)}
@media (hover:hover){.ck-card:hover{transform:translateY(-2px);border-color:color-mix(in srgb,var(--cc) 55%,#1d2326);box-shadow:0 14px 30px -16px var(--cc)}}
.ck-card:active{transform:scale(.98)}
.ck-card:focus-visible{outline:2px solid var(--cc)!important}
.ck-volta{display:none;align-items:center;gap:6px;margin:-8px auto 0;min-height:40px;padding:0 16px 0 12px;border-radius:999px;border:1px solid #23292c;background:#0a0c0d;color:var(--muted);font:700 12px Lato,system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;cursor:pointer;transition:transform .15s,border-color .2s,color .2s}
body.ini[data-ciclo] .ck-volta{display:flex}
.ck-volta:hover{color:var(--fg);border-color:var(--ck-azul)}.ck-volta:active{transform:scale(.96)}
body[data-ciclo=basico] nav.pers a:is([data-per=p6],[data-per=p7],[data-per=p8]){display:none}
body[data-ciclo=clinico] nav.pers a:is([data-per=p1],[data-per=p2],[data-per=p3],[data-per=p4],[data-per=p5]){display:none}
body[data-ciclo=basico] .ck-volta{border-color:color-mix(in srgb,var(--ck-verde) 40%,#23292c)}
body[data-ciclo=clinico] .ck-volta{border-color:color-mix(in srgb,var(--ck-azul) 40%,#23292c)}
/* nas páginas de período: só os períodos do mesmo ciclo + atalho para trocar de ciclo */
nav.pers.xm-abre a.ck-fora{display:none!important}
.ck-outro{display:none;align-items:center;justify-content:center;gap:6px;width:min(300px,100%);margin:4px auto 0;min-height:42px;border-radius:12px;border:1px dashed #2a3338;color:var(--muted);text-decoration:none;font:700 11.5px Lato,system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;transition:border-color .2s,color .2s,transform .15s}
nav.pers.xm-abre + .ck-outro{display:flex!important}
.ck-outro:hover{color:var(--fg);border-color:var(--ck-verde)}.ck-outro:active{transform:scale(.97)}
html[data-tema=claro] .ck-aura{opacity:.4}
.ck-outro,.ck-volta,.ck-ok,.ck-card :is(.ck-t,.ck-s,.ck-d span),.ck-box :is(.ck-sub,footer b,footer small,li b){font-family:Lato,system-ui,sans-serif!important}
/* entrada suave */
@media (prefers-reduced-motion:no-preference){
.ck-card,body.ini nav.pers a{animation:ck-in .5s cubic-bezier(.2,.7,.2,1) both}
.ck-card:nth-child(2){animation-delay:.08s}
body.ini nav.pers a:nth-child(2){animation-delay:.04s}body.ini nav.pers a:nth-child(3){animation-delay:.08s}body.ini nav.pers a:nth-child(4){animation-delay:.12s}body.ini nav.pers a:nth-child(5){animation-delay:.16s}body.ini nav.pers a:nth-child(n+6){animation-delay:.2s}
@keyframes ck-in{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.ck-rip{position:fixed;z-index:10001;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;pointer-events:none;border:1.5px solid rgba(255,255,255,.55);background:rgba(255,255,255,.08);animation:ck-rip .55s cubic-bezier(.2,.6,.2,1) forwards}
@keyframes ck-rip{from{transform:scale(.4);opacity:.9}to{transform:scale(4.2);opacity:0}}
}
/* janela "Sobre o app" */
.ck-bk{position:fixed;inset:0;z-index:10000;background:rgba(0,0,0,.74);display:none;align-items:center;justify-content:center;padding:14px;-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px)}
.ck-bk.on{display:flex}
.ck-box{position:relative;width:min(560px,100%);max-height:92vh;overflow:auto;overscroll-behavior:contain;background:#0b0d0e;color:#e6e6e6;border:1px solid #232a2d;border-radius:18px;padding:0 0 18px;box-shadow:0 30px 70px -20px #000,0 0 0 1px rgba(255,255,255,.02) inset}
.ck-box::before{content:"";display:block;height:3px;background:linear-gradient(90deg,var(--ck-verde),var(--ck-azul))}
@media (prefers-reduced-motion:no-preference){.ck-bk.on{animation:ck-fade .2s ease}.ck-bk.on .ck-box{animation:ck-pop .32s cubic-bezier(.2,.8,.2,1)}
@keyframes ck-fade{from{opacity:0}}@keyframes ck-pop{from{opacity:0;transform:translateY(14px) scale(.97)}}}
.ck-box header{padding:20px 22px 6px;text-align:center}
.ck-box h2{margin:0;font:900 26px/1.1 Lato,system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:#f2f2f2}
.ck-box h2 .c,.ck-box h2 .k{font-style:normal!important}.ck-box h2 .c{color:var(--ck-verde)!important}.ck-box h2 .k{color:var(--ck-azul)!important}
.ck-box .ck-sub{margin:6px 0 0;font:500 11px Lato,system-ui,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:var(--muted)}
.ck-box .ck-x{position:absolute;top:10px;right:10px;width:38px;height:38px;border-radius:50%;border:1px solid #2a3135;background:#101315;color:#cfcfcf;font:20px/1 Lato,system-ui,sans-serif;cursor:pointer;transition:transform .15s,border-color .2s}
.ck-box .ck-x:hover{border-color:var(--ck-azul)}.ck-box .ck-x:active{transform:scale(.9)}
.ck-box section{padding:12px 22px 0}
.ck-box h3{margin:0 0 6px;font:700 12px/1.2 Lato,system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--ck-verde)!important}
.ck-box section:nth-of-type(even) h3{color:var(--ck-azul)!important}
.ck-box p{margin:0 0 6px;font:400 14px/1.6 Merriweather,Georgia,serif;color:#c6c6c6}
.ck-box ul{margin:0;padding:0;list-style:none}
.ck-box li{position:relative;padding:3px 0 3px 16px;font:400 13.5px/1.55 Merriweather,Georgia,serif;color:#c6c6c6}
.ck-box li::before{content:"";position:absolute;left:2px;top:.85em;width:6px;height:6px;border-radius:50%;background:linear-gradient(135deg,var(--ck-verde),var(--ck-azul))}
.ck-box li b{color:#f0f0f0;font-family:Lato,system-ui,sans-serif;font-weight:700}
.ck-box footer{margin:16px 22px 0;padding:14px 16px;border-radius:12px;background:linear-gradient(135deg,var(--ck-verde-s),var(--ck-azul-s));border:1px solid #232a2d;font:400 13.5px/1.55 Merriweather,Georgia,serif;color:#e6e6e6;text-align:center}
.ck-box footer b{font-family:Lato,system-ui,sans-serif}
.ck-box footer small{display:block;margin-top:6px;color:var(--muted);font:400 11.5px/1.5 Lato,system-ui,sans-serif}
.ck-ok{display:block;margin:14px auto 0;min-height:44px;padding:0 30px;border-radius:999px;border:1px solid #FFBE0B;background:#030303;color:#E6E6EA;font:700 13px Lato,system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;cursor:pointer;transition:transform .15s,background .2s}
.ck-ok:hover{background:rgba(255,190,11,.16)}.ck-ok:active{transform:scale(.96)}
html.ck-trava,html.ck-trava body{overflow:hidden}
@media print{.ck-bk,.ck-aura,.ck-rip{display:none!important}}
"""

JS = r"""
(function(){
var R=document.documentElement,B=document.body;
function $(s,c){return (c||document).querySelector(s)}
/* aura */
if(!$(".ck-aura")){var a=document.createElement("div");a.className="ck-aura";a.setAttribute("aria-hidden","true");B.appendChild(a)}
/* ondinha no toque/clique */
if(!matchMedia("(prefers-reduced-motion:reduce)").matches){
addEventListener("pointerdown",function(e){var t=e.target;if(!t.closest||!t.closest("button,a,[role=button],[role=tab],[role=switch],.chip,.grade,.ck-card,summary"))return;
 var r=document.createElement("span");r.className="ck-rip";r.style.left=e.clientX+"px";r.style.top=e.clientY+"px";B.appendChild(r);
 setTimeout(function(){r.remove()},600)},{passive:true,capture:true});}
/* janela Sobre o app */
var TXT={
 sub:"ckp · app dos períodos",
 blocos:[
 ["O que é","Aplicativo de estudo para o 1º ao 8º período de Medicina. A base são os slides das aulas, reescritos como apostila em texto de livro-texto, com complementos de fontes atuais sempre separados do conteúdo do professor."],
 ["Como funciona",["<b>1.</b> Toque em Iniciar, escolha o ciclo (básico, 1º ao 5º; clínico, 6º ao 8º) e depois o período.","<b>2.</b> Em cada período há duas abas: <b>Apostilas</b> e <b>Flashcards</b>.","<b>3.</b> As aulas são organizadas por prova (<b>A1</b> e <b>A2</b>) e, onde existir, por <b>TO</b> (técnica operatória).","<b>4.</b> Pelo nome ou pela rainha no canto você volta a esta janela."]],
 ["Apostilas",["Cada aula vira páginas curtas, com <b>sumário</b>, resumo e a seção <b>“O que aprendemos”</b>.","<b>Fontes e artigos</b> com link no fim da aula; atualizações e divergências com diretrizes aparecem em quadros destacados.","<b>Slide ao lado</b>: nos períodos em que os slides são exibidos (6º e 8º), mostra o slide de origem de cada trecho.","Tamanho da letra (<b>A−</b> e <b>A+</b>), serifa ligada ou desligada e <b>Marcar a aula como lida</b>.","<b>Revisão rápida</b> da aula e botão <b>Continuar</b> para retomar de onde parou."]],
 ["Questões comentadas",["Perguntas dentro da aula, com <b>Mostrar resposta</b> e comentário da correta e das erradas.","Questões baseadas em provas antigas levam o selo <b>já caiu</b>."]],
 ["Flashcards",["Baralhos por assunto, prova (A1, A2, TO) ou todos de uma vez.","Avalie cada cartão como <b>Errei, Difícil, Bom ou Fácil</b>; o app programa as revisões.","Painel com <b>sequência</b> de dias estudados e aulas <b>lidas</b>."]],
 ["Seus destaques",["<b>Grife</b> trechos da apostila, adicione notas e use o botão <b>Destaques</b> para ver tudo.","Cada destaque pode virar cartão de revisão."]],
 ["No dia a dia",["<b>Tema claro e escuro</b> (sol/lua no canto) e <b>Cores quentes</b> para o claro virar papel creme.","<b>Imprimir</b> (Ctrl+P) gera a aula inteira em A4.","Suporte a <b>caneta</b> em tablet: a palma da mão é ignorada enquanto você escreve.","Funciona <b>sem internet</b> depois de aberto uma vez no aparelho."]],
 ["Conta (opcional)","O progresso fica salvo neste aparelho. Se quiser, entre pelo ícone de conta para sincronizar entre celular, tablet e computador. Sem conta, tudo continua funcionando."]
 ]};
function monta(){
 var bk=document.createElement("div");bk.className="ck-bk";bk.setAttribute("role","dialog");bk.setAttribute("aria-modal","true");bk.setAttribute("aria-labelledby","ck-ttl");
 var h='<div class="ck-box"><button type="button" class="ck-x" aria-label="Fechar">×</button><header><h2 id="ck-ttl"><span class="c">C</span>aro-<span class="k">K</span>ann Med</h2><p class="ck-sub">'+TXT.sub+'</p></header>';
 TXT.blocos.forEach(function(b){h+="<section><h3>"+b[0]+"</h3>"+(typeof b[1]==="string"?"<p>"+b[1]+"</p>":"<ul>"+b[1].map(function(x){return "<li>"+x+"</li>"}).join("")+"</ul>")+"</section>"});
 h+='<footer>Desenvolvido por um <b>acadêmico da FCMS-JF Suprema</b> (Faculdade de Ciências Médicas e da Saúde de Juiz de Fora), para estudar melhor com os colegas.<small>Material de apoio ao estudo. Não substitui as aulas, os livros-texto nem as diretrizes vigentes. Versão de teste (BETA).</small></footer><button type="button" class="ck-ok">Entendi</button></div>';
 bk.innerHTML=h;B.appendChild(bk);return bk}
var bk=null,voltaA=null;
function abre(){if(!bk)bk=monta();voltaA=document.activeElement;bk.classList.add("on");R.classList.add("ck-trava");var x=$(".ck-x",bk);x&&x.focus();bk.scrollTop=0;$(".ck-box",bk).scrollTop=0}
function fecha(){if(!bk)return;bk.classList.remove("on");R.classList.remove("ck-trava");try{voltaA&&voltaA.focus&&voltaA.focus()}catch(e){}}
addEventListener("click",function(e){var t=e.target;if(!t.closest)return;
 if(bk&&bk.classList.contains("on")){if(t===bk||t.closest(".ck-x,.ck-ok"))fecha();return}
 var g=t.closest(".xm-canto,.asmed");if(g){e.preventDefault();e.stopPropagation();abre()}},true);
addEventListener("keydown",function(e){
 if(bk&&bk.classList.contains("on")){if(e.key==="Escape"){fecha();return}
  if(e.key==="Tab"){var f=[].slice.call(bk.querySelectorAll("button")),i=f.indexOf(document.activeElement);if(e.shiftKey&&i<=0){e.preventDefault();f[f.length-1].focus()}else if(!e.shiftKey&&i===f.length-1){e.preventDefault();f[0].focus()}}return}
 if((e.key==="Enter"||e.key===" ")&&e.target.matches&&e.target.matches(".xm-canto,.asmed")){e.preventDefault();abre()}});
document.querySelectorAll(".xm-canto,.asmed").forEach(function(g){g.setAttribute("role","button");g.tabIndex=0;g.setAttribute("aria-label","Sobre o Caro-Kann Med: como funciona e o que o app tem")});
/* escolha de ciclo (início) */
var cic=$(".ck-ciclos");
if(cic){
 var H=["#ciclos","#basico","#clinico"];
 function aplica(){var h=location.hash,i=H.indexOf(h);
  if(i<0){B.removeAttribute("data-ciclo");return}
  B.classList.add("ini");if(i===0)B.removeAttribute("data-ciclo");else B.dataset.ciclo=i===1?"basico":"clinico";}
 function vai(h){if(location.hash!==h)history.pushState(null,"",h);aplica()}
 cic.addEventListener("click",function(e){var c=e.target.closest(".ck-card");if(c)vai("#"+c.dataset.ciclo)});
 var v=$(".ck-volta");v&&v.addEventListener("click",function(){vai("#ciclos")});
 var ib=$(".ini-bt");ib&&ib.addEventListener("click",function(){vai("#ciclos")});
 addEventListener("hashchange",function(){if(location.hash===""||H.indexOf(location.hash)>=0){if(location.hash==="")B.classList.remove("ini");aplica()}});
 addEventListener("pageshow",aplica);aplica();
}
/* páginas de período: só o mesmo ciclo na lista + atalho "Trocar de ciclo" */
var nav=$("nav.pers"),m=/\/p([1-8])\.html$/.exec(location.pathname);
if(nav&&m){var n=+m[1],b=n<=5;
 nav.querySelectorAll("a[data-per]").forEach(function(a){var k=+a.dataset.per.slice(1);if((k<=5)!==b)a.classList.add("ck-fora")});
 if(!$(".ck-outro")){var l=document.createElement("a");l.className="ck-outro";l.href="index.html#ciclos";l.textContent="Trocar de ciclo";nav.after(l)}}
})();
"""

CICLOS = """<section class="ck-ciclos" aria-label="Escolher o ciclo"><button type="button" class="ck-card" data-ciclo="basico"><span class="ck-t">Ciclo básico</span><span class="ck-s">1º ao 5º</span><span class="ck-d"><i style="--c:hsl(14 42% 60%)"></i><i style="--c:hsl(318 34% 62%)"></i><i style="--c:hsl(38 46% 58%)"></i><i style="--c:hsl(128 30% 56%)"></i><i style="--c:hsl(218 42% 64%)"></i><span>5 períodos</span></span></button><button type="button" class="ck-card" data-ciclo="clinico"><span class="ck-t">Ciclo clínico</span><span class="ck-s">6º ao 8º</span><span class="ck-d"><i style="--c:hsl(346 40% 58%)"></i><i style="--c:hsl(187 42% 52%)"></i><i style="--c:hsl(262 40% 66%)"></i><span>3 períodos</span></span></button></section><button type="button" class="ck-volta" aria-label="Voltar para a escolha do ciclo">‹ Ciclos</button>"""


def patch(f):
    t = f.read_text(encoding="utf-8")
    o = t
    # 1. nome
    t = t.replace('<span class="t">Caro-Kann <b>Med</b></span>',
                  '<span class="t"><span class="ck-c">C</span>aro-<span class="ck-k">K</span>ann <b>Med</b></span>')
    # 2. bloco CSS/JS
    t = re.sub(r"<!--ckp-->.*?<!--/ckp-->\s*", "", t, flags=re.S)
    bloco = "<!--ckp--><style data-ckp>" + CSS + "</style><script data-ckp>" + JS + "</script><!--/ckp-->\n"
    assert "</body>" in t, f
    t = t.replace("</body>", bloco + "</body>", 1)
    # 3. ciclos (só no início)
    if f.name == "index.html" and f.parent == P:
        t = re.sub(r"<!--ck:ciclos-->.*?<!--/ck:ciclos-->", "", t, flags=re.S)
        assert "<!--per:nav-->" in t
        t = t.replace("<!--per:nav-->", "<!--ck:ciclos-->" + CICLOS + "<!--/ck:ciclos--><!--per:nav-->", 1)
        # texto que prometia abrir direto no período guardado (não acontece)
        t = t.replace("Escolha o período. O app guarda a escolha neste aparelho e abre direto nele.",
                      "Escolha o período. Seu progresso fica salvo neste aparelho.")
    if t != o:
        f.write_text(t, encoding="utf-8")
    return t != o


for a in ALVOS:
    f = P / a
    if f.exists():
        print(("alterado " if patch(f) else "igual     ") + a)
    else:
        print("ausente   " + a)
