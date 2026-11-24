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
import re, sys, json, pathlib

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
.tr-row>span,.tr-meta span,.tr-stats :is(b,span),.tr-cob,.tr-head h2,.tr-res .big,.ck-outro,.ck-volta,.ck-ok,.ck-card :is(.ck-t,.ck-s,.ck-d span),.ck-box :is(.ck-sub,footer b,footer small,li b){font-family:Lato,system-ui,sans-serif!important}
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
.ck-box footer{display:block!important;margin:16px 22px 0;padding:14px 16px;border-radius:12px;background:linear-gradient(135deg,var(--ck-verde-s),var(--ck-azul-s));border:1px solid #232a2d;font:400 13.5px/1.55 Merriweather,Georgia,serif;color:#e6e6e6;text-align:center}
.ck-box footer b{font-family:Lato,system-ui,sans-serif;display:inline!important}
.ck-box footer small{display:block;margin-top:6px;color:var(--muted);font:400 11.5px/1.5 Lato,system-ui,sans-serif}
.ck-acoes{display:flex;justify-content:center;align-items:center;gap:10px;margin-top:14px;flex-wrap:wrap}.ck-acoes .ck-ok{margin:0}.ck-ct{min-height:44px;padding:0 22px;border-radius:999px;border:1px solid #2a3338;background:transparent;color:var(--muted);font:700 13px Lato,system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;cursor:pointer;transition:transform .15s,border-color .2s,color .2s}.ck-ct:hover{color:var(--fg);border-color:var(--ck-azul)}.ck-ct:active{transform:scale(.96)}
.ck-rodape{display:flex;justify-content:center;margin-top:-6px}.ck-rodape .ck-ct{min-height:38px;border-color:transparent;letter-spacing:.1em;font-size:12px}
.ck-toast{position:fixed;left:50%;bottom:calc(env(safe-area-inset-bottom,0px) + 24px);transform:translate(-50%,12px);z-index:10002;max-width:min(92vw,360px);padding:12px 18px;border-radius:12px;border:1px solid #2a3338;background:#0e1214;color:#eee;font:600 13px/1.4 Lato,system-ui,sans-serif;text-align:center;opacity:0;pointer-events:none;transition:opacity .25s,transform .25s}.ck-toast.on{opacity:1;transform:translate(-50%,0)}
.ck-ok{display:block;margin:14px auto 0;min-height:44px;padding:0 30px;border-radius:999px;border:1px solid #FFBE0B;background:#030303;color:#E6E6EA;font:700 13px Lato,system-ui,sans-serif;letter-spacing:.12em;text-transform:uppercase;cursor:pointer;transition:transform .15s,background .2s}
.ck-ok:hover{background:rgba(255,190,11,.16)}.ck-ok:active{transform:scale(.96)}
html.ck-trava,html.ck-trava body{overflow:hidden}
@media print{.ck-bk,.ck-aura,.ck-rip{display:none!important}}
"""

CSS2 = r"""
/* só a rainha pulsa; o nome fica parado e só muda de cor, bem de leve */
@media (prefers-reduced-motion:no-preference){
.asmed{animation:none!important;will-change:auto!important}
.xm-mini,.asmed .qw{animation:ck-pulso 2.4s ease-in-out infinite!important;will-change:transform;transform-origin:50% 55%}
@keyframes ck-pulso{0%,39%{transform:scale(1)}43%{transform:scale(1.14)}49%,100%{transform:scale(1)}}}
/* nome maior e com letras que alternam verde/azul */
html .brand .word .asmed{font-size:clamp(21px,6.3vw,28px)}
.asmed .t .ck-l{transition:color 1s ease,text-shadow 1s ease}
.asmed .t .ck-l.g{color:var(--ck-verde)!important;text-shadow:0 0 14px rgba(60,196,142,.2)}
.asmed .t .ck-l.b{color:var(--ck-azul)!important;text-shadow:0 0 14px rgba(79,150,234,.2)}
/* acabamento geral */
::selection{background:rgba(79,150,234,.32);color:inherit}
html{scroll-behavior:smooth;scrollbar-color:#2a3338 transparent}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{-webkit-tap-highlight-color:transparent;text-rendering:optimizeLegibility}
:focus-visible{outline-color:var(--ck-azul)!important}
nav.tabs a,.chip,button,a.back,.grade{touch-action:manipulation}
nav.tabs a{position:relative;transition:color .2s,border-color .2s,background .2s,transform .15s}
nav.tabs a:active{transform:scale(.96)}
nav.tabs a[aria-current]::after{content:"";position:absolute;left:22%;right:22%;bottom:3px;height:2px;border-radius:2px;background:linear-gradient(90deg,var(--ck-verde),var(--ck-azul))}
@media (prefers-reduced-motion:no-preference){nav.tabs a[aria-current]::after{animation:ck-tab .35s cubic-bezier(.2,.8,.2,1) both}@keyframes ck-tab{from{transform:scaleX(0)}}}
.stat,.card,.item,.mat,.bitem,.ap-card{transition:border-color .2s,box-shadow .25s,transform .2s}
.ck-outro{font-family:Lato,system-ui,sans-serif}
/* questões para treinar */
#v-treinar{gap:14px}
.tr-head{display:flex;flex-direction:column;gap:6px;padding:4px 2px 0}
.tr-head h2{margin:0;font:900 20px/1.2 Lato,system-ui,sans-serif;letter-spacing:.04em;color:#f2f2f2}
.tr-head p{margin:0;font:400 13px/1.55 Merriweather,Georgia,serif;color:var(--muted)}
.tr-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.tr-stats div{padding:10px 8px;border:1px solid #1d2326;border-radius:12px;background:#0a0c0d;text-align:center}
.tr-stats b{display:block;font:900 20px/1.1 Lato,system-ui,sans-serif;color:#f1f1f1;font-variant-numeric:tabular-nums}
.tr-stats span{display:block;margin-top:3px;font:500 10.5px/1.2 Lato,system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.tr-stats div:nth-child(1) b{color:var(--ck-azul)}.tr-stats div:nth-child(3) b{color:var(--ck-verde)}
.tr-fil{display:flex;flex-direction:column;gap:8px}
.tr-row{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.tr-row>span{flex:0 0 100%;font:700 10.5px/1 Lato,system-ui,sans-serif;letter-spacing:.14em;text-transform:uppercase;color:var(--dim)}
.tr-chip{min-height:36px;padding:0 13px;border-radius:999px;border:1px solid #232a2d;background:#0a0c0d;color:var(--muted);font:600 12.5px Lato,system-ui,sans-serif;cursor:pointer;transition:border-color .2s,color .2s,background .2s,transform .12s}
.tr-chip:hover{color:var(--fg);border-color:#3a464b}.tr-chip:active{transform:scale(.95)}
.tr-chip[aria-pressed=true]{color:#fff;border-color:var(--ck-azul);background:var(--ck-azul-s)}
.tr-go{display:flex;align-items:center;justify-content:center;gap:8px;min-height:50px;border-radius:14px;border:1px solid var(--ck-verde);background:linear-gradient(135deg,var(--ck-verde-s),var(--ck-azul-s));color:#f4f4f4;font:700 14px Lato,system-ui,sans-serif;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;transition:transform .15s,box-shadow .25s,opacity .2s}
.tr-go:hover{box-shadow:0 10px 26px -14px var(--ck-verde)}.tr-go:active{transform:scale(.98)}.tr-go[disabled]{opacity:.4;cursor:not-allowed;box-shadow:none}
.tr-cob{margin:0;font:400 12px/1.5 Lato,system-ui,sans-serif;color:var(--dim);text-align:center}
.tr-vazio{padding:22px 16px;border:1px dashed #2a3338;border-radius:14px;text-align:center;font:400 13.5px/1.6 Merriweather,Georgia,serif;color:var(--muted)}
.tr-top{display:flex;align-items:center;gap:12px}
.tr-top .n{font:700 12px Lato,system-ui,sans-serif;letter-spacing:.08em;color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}
.tr-bar{flex:1;height:5px;border-radius:5px;background:#161b1d;overflow:hidden}
.tr-bar i{display:block;height:100%;width:0;border-radius:5px;background:linear-gradient(90deg,var(--ck-verde),var(--ck-azul));transition:width .4s cubic-bezier(.2,.7,.2,1)}
.tr-sair{min-height:34px;padding:0 12px;border-radius:999px;border:1px solid #232a2d;background:transparent;color:var(--muted);font:600 12px Lato,system-ui,sans-serif;cursor:pointer}
.tr-card{padding:18px 16px;border:1px solid #1d2326;border-radius:16px;background:linear-gradient(180deg,#0c0f11,#080a0b);display:flex;flex-direction:column;gap:12px;box-shadow:0 12px 30px -18px #000}
.tr-meta{display:flex;flex-wrap:wrap;align-items:center;gap:8px;font:600 11px Lato,system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.tr-tag{padding:3px 9px;border-radius:999px;border:1px solid #FFBE0B;color:#FFBE0B;font-weight:700}
.tr-tag.t2{border-color:var(--ck-azul);color:var(--ck-azul)}
.tr-q{margin:0;font:400 15.5px/1.7 Merriweather,Georgia,serif;color:#ececec}
.tr-ask{margin:0;font:700 15px/1.6 Merriweather,Georgia,serif;color:#f6f6f6}
.tr-show{min-height:46px;border-radius:12px;border:1px solid #2a3338;background:#0f1315;color:#e6e6e6;font:700 13px Lato,system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;cursor:pointer;transition:border-color .2s,transform .12s}
.tr-show:hover{border-color:var(--ck-azul)}.tr-show:active{transform:scale(.98)}
.tr-ans{padding:12px 14px;border-left:3px solid var(--ck-azul);border-radius:0 12px 12px 0;background:rgba(79,150,234,.07)}
.tr-ans p{margin:0 0 8px;font:400 14px/1.7 Merriweather,Georgia,serif;color:#d6d6d6}.tr-ans p:last-child{margin:0}
.tr-rate{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.tr-rate button{min-height:50px;border-radius:12px;border:1px solid #2a3338;background:#0f1315;color:#f0f0f0;font:700 14px Lato,system-ui,sans-serif;letter-spacing:.06em;cursor:pointer;transition:transform .12s,border-color .2s,background .2s}
.tr-rate button:active{transform:scale(.97)}
.tr-rate .ok{border-color:var(--ck-verde)}.tr-rate .ok:hover{background:var(--ck-verde-s)}
.tr-rate .no{border-color:#c2414a}.tr-rate .no:hover{background:rgba(194,65,74,.15)}
.tr-res{text-align:center;display:flex;flex-direction:column;align-items:center;gap:10px;padding:22px 16px}
.tr-res .big{font:900 44px/1 Lato,system-ui,sans-serif;background:linear-gradient(90deg,var(--ck-verde),var(--ck-azul));-webkit-background-clip:text;background-clip:text;color:transparent!important}
.tr-res p{margin:0;font:400 13.5px/1.6 Merriweather,Georgia,serif;color:var(--muted)}
.tr-erros{width:100%;text-align:left;margin:4px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:6px}
.tr-erros li{padding:9px 12px;border:1px solid #2a2024;border-radius:10px;background:rgba(194,65,74,.07);font:400 12.5px/1.5 Merriweather,Georgia,serif;color:#cfcfcf}
.tr-btns{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;width:100%}
.tr-btns .tr-go{flex:1 1 150px}
@media (prefers-reduced-motion:no-preference){.tr-card,.tr-res{animation:ck-in .35s cubic-bezier(.2,.7,.2,1) both}}
@media (max-width:520px){.tr-lg{display:none}}
nav.tabs{flex-wrap:nowrap}nav.tabs a{white-space:nowrap}
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
/* contato: troque o e-mail aqui quando existir (vazio = "em breve") */
var CK_EMAIL="carokannmed@gmail.com";
function aviso(m){var t=$(".ck-toast")||B.appendChild(Object.assign(document.createElement("div"),{className:"ck-toast",role:"status"}));t.textContent=m;t.classList.add("on");clearTimeout(aviso.t);aviso.t=setTimeout(function(){t.classList.remove("on")},3200)}
function contato(){if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(CK_EMAIL)){aviso("E-mail de contato em breve.");return}
 var per=(location.pathname.match(/p([1-8])\.html$/)||[])[1];
 location.href="mailto:"+CK_EMAIL+"?subject="+encodeURIComponent("Caro-Kann Med · contato")+"&body="+encodeURIComponent("Escreva sua dúvida, sugestão ou reclamação aqui.\n\n---\nApp: Caro-Kann Med (ckp)"+(per?" · "+per+"º período":"")+"\n"+navigator.userAgent)}
addEventListener("click",function(e){var c=e.target.closest&&e.target.closest("[data-contato]");if(c){e.preventDefault();contato()}});
/* janela Sobre o app */
var TXT={
 sub:"ckp · app dos períodos",
 blocos:[
 ["O que é","Aplicativo de estudo para o 1º ao 8º período de Medicina, baseado em resumos de alunos e na análise de relatos de provas antigas 👀."],
 ["O que tem",["<b>Apostilas</b>: aulas com sumário, resumo, “O que aprendemos” e fontes com link.","<b>Flashcards</b>: baralhos por assunto; avalie como Errei, Difícil, Bom ou Fácil e o app programa as revisões.","<b>Questões para treinar</b>: casos e perguntas no modelo das provas antigas, com resposta comentada e seu desempenho salvo.","<b>Destaques</b>: grife trechos, anote e transforme em cartão de revisão.","<b>Temas</b> claro e escuro, <b>impressão</b> (Ctrl+P) e uso <b>sem internet</b> depois de aberto uma vez."]]
 ]};
function monta(){
 var bk=document.createElement("div");bk.className="ck-bk";bk.setAttribute("role","dialog");bk.setAttribute("aria-modal","true");bk.setAttribute("aria-labelledby","ck-ttl");
 var h='<div class="ck-box"><button type="button" class="ck-x" aria-label="Fechar">×</button><header><h2 id="ck-ttl"><span class="c">C</span>aro-<span class="k">K</span>ann Med</h2><p class="ck-sub">'+TXT.sub+'</p></header>';
 TXT.blocos.forEach(function(b){h+="<section><h3>"+b[0]+"</h3>"+(typeof b[1]==="string"?"<p>"+b[1]+"</p>":"<ul>"+b[1].map(function(x){return "<li>"+x+"</li>"}).join("")+"</ul>")+"</section>"});
 h+='<footer>Desenvolvido por um <b>acadêmico da FCMS-JF Suprema</b>.<small>Material de apoio ao estudo; não substitui aulas, livros-texto nem diretrizes. Versão de teste (BETA).</small></footer><div class="ck-acoes"><button type="button" class="ck-ct" data-contato>Contato</button><button type="button" class="ck-ok">Entendi</button></div></div>';
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
if(cic){var so=$(".soon");if(!$(".ck-rodape")){var rp=document.createElement("div");rp.className="ck-rodape";rp.innerHTML='<button type="button" class="ck-ct" data-contato>Contato</button>';(so||cic).after(rp)}
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

JS2 = r"""
/* nome: letras trocando entre verde e azul até o nome inteiro ficar verde ou azul, e recomeça */
(function(){
var ts=document.querySelectorAll(".asmed .t");if(!ts.length)return;
var SEQ=[[0,"C"],[1,"a"],[2,"r"],[3,"o"],[4,"-"],[5,"K"],[6,"a"],[7,"n"],[8,"n"]];
ts.forEach(function(t){if(t.dataset.ckl)return;t.dataset.ckl="1";
 var h="";"Caro-Kann".split("").forEach(function(c,i){h+='<span class="ck-l'+(i===0?" g":i===5?" b":"")+'">'+c+"</span>"});
 h+=" <b>"+"Med".split("").map(function(c){return '<span class="ck-l">'+c+"</span>"}).join("")+"</b>";t.innerHTML=h});
if(matchMedia("(prefers-reduced-motion:reduce)").matches)return;
var G=[].slice.call(document.querySelectorAll(".asmed .t")).map(function(t){return [].slice.call(t.querySelectorAll(".ck-l"))});
var N=12,v=0;
function set(i,c){G.forEach(function(g){var e=g[i];e.classList.remove("g","b");if(c)e.classList.add(c)})}
function rnd(n){return Math.floor(Math.random()*n)}
function repouso(){for(var i=0;i<N;i++)set(i,i===0?"g":i===5?"b":"")}
function cor(i){var e=G[0][i];return e.classList.contains("g")?"g":e.classList.contains("b")?"b":""}
function espera(f,ms){setTimeout(function(){if(document.hidden){espera(f,1500);return}f()},ms)}
function mistura(k){if(k>=16){converge(v%2?"b":"g");return}
 for(var j=0;j<2;j++)set(rnd(N),Math.random()<.5?"g":"b");espera(function(){mistura(k+1)},650)}
function converge(w){var f=[];for(var i=0;i<N;i++)if(cor(i)!==w)f.push(i);
 if(!f.length){espera(function(){repouso();v++;espera(ciclo,3200)},3000);return}
 set(f[rnd(f.length)],w);espera(function(){converge(w)},520)}
function ciclo(){mistura(0)}
repouso();espera(ciclo,3200);
})();

/* questões para treinar */
(function(){
var tabs=document.querySelector("nav.tabs"),vc=document.getElementById("v-cards");
if(!tabs||!vc||typeof PER==="undefined")return;
var ARQ=__ARQ__;
var a=document.createElement("a");a.href="#treinar";a.dataset.view="treinar";a.innerHTML="Questões<span class=\"tr-lg\"> para treinar</span>";a.setAttribute("aria-label","Questões para treinar");tabs.appendChild(a);
var V=document.createElement("div");V.className="view";V.id="v-treinar";V.hidden=true;V.setAttribute("aria-label","Questões para treinar");vc.after(V);
var KEY="medaj-"+PER.id+"-treino",H={};try{H=JSON.parse(localStorage.getItem(KEY)||"{}")}catch(e){}
function grava(){try{localStorage.setItem(KEY,JSON.stringify(H))}catch(e){}}
var ITENS=null,CARREGA=null,F={g:"",d:"",t:""},S=null;
function esc(x){return String(x==null?"":x)}
function strip(x){return String(x||"").replace(/<[^>]+>/g," ").replace(/\s+/g," ").trim()}
function carrega(){if(ITENS)return Promise.resolve();if(CARREGA)return CARREGA;
 CARREGA=Promise.all(ARQ.map(function(u){return new Promise(function(ok){var s=document.createElement("script");s.src=u;s.onload=ok;s.onerror=ok;document.head.appendChild(s)})})).then(coleta);return CARREGA}
function coleta(){var meta={};(PER.aulas||[]).forEach(function(x){meta[x.id]=x});var out=[],DS=window.__DS||{};
 Object.keys(DS).forEach(function(k){var d=DS[k];if(!d||!d.sections)return;
  d.sections.forEach(function(sec){var m=meta[sec.id]||{};
   var disc=m.disc||sec.esp||strip(sec.title).split("·")[0].replace(/^\d+\.\s*/,"").trim();
   var gr=(m.mat==="Técnica operatória")?"":(m.av||sec.av||"");
   var ja=/^pa\d/.test(sec.id);
   (sec.blocks||[]).forEach(function(b,bi){
    if(b.t==="prova")out.push({id:sec.id+":"+bi,k:"p",g:gr,d:disc,aula:strip(sec.title),ja:true,src:b.src,q:b.stem,ask:b.ask,a:(b.reveal||[]).map(function(x){return "<p>"+x+"</p>"}).join("")});
    else if(b.t==="q")(b.v||[]).forEach(function(q,ii){out.push({id:sec.id+":"+bi+":"+ii,k:"q",g:gr,d:disc,aula:strip(sec.title),ja:ja,q:q.q,a:"<p>"+q.a+"</p>"})});
    else if(b.t==="lance")out.push({id:sec.id+":"+bi,k:"q",g:gr,d:disc,aula:strip(sec.title),ja:ja,q:b.q,a:"<p>"+b.a+"</p>"})})})});
 ITENS=out}
function pool(){return (ITENS||[]).filter(function(i){return (!F.g||i.g===F.g)&&(!F.d||i.d===F.d)&&(!F.t||(F.t==="p"?i.k==="p":i.k==="q"))})}
function opts(campo,filtrarPor){var m={};(ITENS||[]).forEach(function(i){if(i[campo])m[i[campo]]=(m[i[campo]]||0)+1});return Object.keys(m).sort()}
function chips(rot,campo,lista,fmt){return '<div class="tr-row"><span>'+rot+'</span><button type="button" class="tr-chip" data-f="'+campo+'" data-v="" aria-pressed="'+(F[campo]===""?"true":"false")+'">Todas</button>'+lista.map(function(x){return '<button type="button" class="tr-chip" data-f="'+campo+'" data-v="'+x[0]+'" aria-pressed="'+(F[campo]===x[0]?"true":"false")+'">'+x[1]+'</button>'}).join("")+"</div>"}
function resumo(){var v=0,ac=0,tot=ITENS.length;ITENS.forEach(function(i){var h=H[i.id];if(h){v++;if(h[0])ac++}});return {tot:tot,v:v,ac:ac}}
function home(){
 if(!ITENS){V.innerHTML='<p class="tr-vazio">Carregando as questões…</p>';return}
 if(!ITENS.length){V.innerHTML='<div class="tr-head"><h2>Questões para treinar</h2></div><p class="tr-vazio">Este período ainda não tem questões. Elas aparecem aqui assim que as apostilas chegarem.</p>';return}
 var r=resumo(),pl=pool(),np=ITENS.filter(function(i){return i.k==="p"}).length;
 var gs=opts("g").map(function(x){return [x,x]}),ds=opts("d").map(function(x){return [x,x]});
 var h='<div class="tr-head"><h2>Questões para treinar</h2><p>Casos e perguntas no modelo das provas antigas. Responda de cabeça, confira a resposta comentada e diga se acertou.</p></div>';
 h+='<div class="tr-stats"><div><b>'+r.tot+'</b><span>questões</span></div><div><b>'+r.v+'</b><span>já treinadas</span></div><div><b>'+(r.v?Math.round(r.ac*100/r.v)+"%":"–")+'</b><span>acerto</span></div></div>';
 h+='<div class="tr-fil">';
 if(gs.length>1)h+=chips("Prova","g",gs);
 if(ds.length>1)h+=chips("Disciplina","d",ds);
 if(np)h+=chips("Tipo","t",[["p","Casos de prova"],["q","Perguntas"]]);
 h+="</div>";
 h+='<button type="button" class="tr-go" data-go'+(pl.length?"":" disabled")+'>Treinar '+Math.min(10,pl.length)+' questões</button>';
 h+='<p class="tr-cob">'+pl.length+' no filtro atual · '+np+' casos de prova antiga e '+(r.tot-np)+' perguntas neste período</p>';
 V.innerHTML=h}
function sorteia(){var pl=pool().map(function(i){var h=H[i.id];return {i:i,s:(h?(h[0]?2+h[1]/1e13:1):0)+Math.random()*.5}});
 pl.sort(function(x,y){return x.s-y.s});return pl.slice(0,10).map(function(x){return x.i})}
function pergunta(){var it=S.l[S.n];
 var h='<div class="tr-top"><span class="n">'+(S.n+1)+" / "+S.l.length+'</span><div class="tr-bar"><i style="width:'+(S.n*100/S.l.length)+'%"></i></div><button type="button" class="tr-sair" data-sair>Sair</button></div>';
 h+='<article class="tr-card"><div class="tr-meta">'+(it.ja?'<span class="tr-tag">já caiu</span>':'<span class="tr-tag t2">treino</span>')+'<span>'+esc(it.d)+(it.g?" · "+it.g:"")+"</span></div>";
 h+='<p class="tr-q">'+it.q+"</p>"+(it.ask?'<p class="tr-ask">'+it.ask+"</p>":"");
 h+='<button type="button" class="tr-show" data-show>Mostrar resposta</button><div class="tr-ans" hidden>'+it.a+'</div><div class="tr-rate" hidden><button type="button" class="no" data-r="0">Errei</button><button type="button" class="ok" data-r="1">Acertei</button></div></article>';
 V.innerHTML=h;window.scrollTo({top:0})}
function fim(){var ac=S.l.filter(function(i){return S.r[i.id]}).length,er=S.l.filter(function(i){return !S.r[i.id]});
 var h='<div class="tr-card tr-res"><div class="big">'+ac+" / "+S.l.length+"</div><p>"+(ac===S.l.length?"Sem erros. Bora para a próxima rodada.":er.length>S.l.length/2?"Vale rever as apostilas dos temas abaixo e tentar de novo.":"Boa rodada. As erradas voltam primeiro nas próximas.")+"</p>";
 if(er.length)h+='<ul class="tr-erros">'+er.map(function(i){return "<li><b>"+esc(i.d)+":</b> "+esc(strip(i.q).slice(0,110))+(strip(i.q).length>110?"…":"")+"</li>"}).join("")+"</ul>";
 h+='<div class="tr-btns"><button type="button" class="tr-go" data-go>Treinar de novo</button><button type="button" class="tr-chip" data-sair>Mudar filtros</button></div></div>';
 V.innerHTML=h;S=null;window.scrollTo({top:0})}
V.addEventListener("click",function(e){var t=e.target;if(!t.closest)return;
 var c=t.closest("[data-f]");if(c){F[c.dataset.f]=c.dataset.v;home();return}
 if(t.closest("[data-go]")){var l=sorteia();if(!l.length)return;S={l:l,n:0,r:{}};pergunta();return}
 if(t.closest("[data-sair]")){S=null;home();return}
 if(t.closest("[data-show]")){var b=t.closest("[data-show]");b.hidden=true;V.querySelector(".tr-ans").hidden=false;V.querySelector(".tr-rate").hidden=false;return}
 var r=t.closest("[data-r]");if(r&&S){var it=S.l[S.n],ok=r.dataset.r==="1";S.r[it.id]=ok;H[it.id]=[ok?1:0,Date.now()];grava();S.n++;if(S.n>=S.l.length)fim();else pergunta()}});
function mostra(){var on=location.hash==="#treinar";
 if(!on){return}
 document.querySelectorAll(".view").forEach(function(x){x.hidden=x!==V});
 document.querySelectorAll(".tabs a").forEach(function(a){if(a.dataset.view==="treinar")a.setAttribute("aria-current","page");else a.removeAttribute("aria-current")});
 if(!S)home();carrega().then(function(){if(location.hash==="#treinar"&&!S)home()})}
addEventListener("hashchange",mostra);mostra();
})();
"""

CICLOS = """<section class="ck-ciclos" aria-label="Escolher o ciclo"><button type="button" class="ck-card" data-ciclo="basico"><span class="ck-t">Ciclo básico</span><span class="ck-s">1º ao 5º</span><span class="ck-d"><i style="--c:hsl(14 42% 60%)"></i><i style="--c:hsl(318 34% 62%)"></i><i style="--c:hsl(38 46% 58%)"></i><i style="--c:hsl(128 30% 56%)"></i><i style="--c:hsl(218 42% 64%)"></i><span>5 períodos</span></span></button><button type="button" class="ck-card" data-ciclo="clinico"><span class="ck-t">Ciclo clínico</span><span class="ck-s">6º ao 8º</span><span class="ck-d"><i style="--c:hsl(346 40% 58%)"></i><i style="--c:hsl(187 42% 52%)"></i><i style="--c:hsl(262 40% 66%)"></i><span>3 períodos</span></span></button></section><button type="button" class="ck-volta" aria-label="Voltar para a escolha do ciclo">‹ Ciclos</button>"""


def patch(f):
    t = f.read_text(encoding="utf-8")
    o = t
    # 1. nome
    t = t.replace('<span class="t">Caro-Kann <b>Med</b></span>',
                  '<span class="t"><span class="ck-c">C</span>aro-<span class="ck-k">K</span>ann <b>Med</b></span>')
    # 1b. textos que citavam slides como origem do material
    for a, b in [
        ("Os slides de cada aula são a base. O que vem de fora", "O que vem de fora"),
        ("Esta aula segue só os slides do professor; nenhuma fonte externa foi citada nela.", "Esta aula não cita fonte externa."),
        (" entram aqui quando chegarem os slides.", " entram aqui em breve."),
        ("Atualização · fora do slide", "Atualização · complemento"),
    ]:
        t = t.replace(a, b)
    t = re.sub(r"\s*·\s*sem slides de aula:[^\"]*", "", t)
    t = re.sub(r" · \d+ slides(?=\")", "", t)
    # 2. bloco CSS/JS
    t = re.sub(r"<!--ckp-->.*?<!--/ckp-->\s*", "", t, flags=re.S)
    arq = "[]"
    mm = re.match(r"p([1-8])\.html$", f.name)
    if mm and f.parent == P:
        m2 = re.search(r'<script>const PER=\{"id":\s*"p\d","site":\s*"([^"]+)/index\.html"', t)
        if m2:
            d = P / m2.group(1) / "d"
            arq = json.dumps(sorted(m2.group(1) + "/d/" + x.name for x in d.glob("*.js"))) if d.exists() else "[]"
    nome_js, treino_js = JS2.split("/* questões para treinar */")
    js2 = nome_js + ("/* questões para treinar */" + treino_js.replace("__ARQ__", arq) if mm and f.parent == P else "")
    bloco = "<!--ckp--><style data-ckp>" + CSS + CSS2 + "</style><script data-ckp>" + JS + "</script><script data-ckp2>" + js2 + "</script><!--/ckp-->\n"
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
