#!/usr/bin/env python3
"""Gera ferramentas/xm-reto-completo.woff2: a fonte "XM Reto" (feita à mão, só A D E M Q T U X) com
C O R N K e hífen no mesmo desenho (altura 720, haste 140, cantos chanfrados), para o nome Caro-Kann Med.
Uso: python3 ferramentas/gera-xmreto.py <woff2 original da XM Reto> (já feito; arquivo gerado fica no repositório)."""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.ttGlyphPen import TTGlyphPen

src = sys.argv[1]
t = TTFont(src)
novos = {
    "C": (590, [[(45, 620), (145, 720), (545, 720), (545, 580), (185, 580), (185, 140), (545, 140), (545, 0), (145, 0), (45, 100)]]),
    "O": (610, [[(45, 620), (145, 720), (465, 720), (565, 620), (565, 100), (465, 0), (145, 0), (45, 100)],
                [(185, 140), (425, 140), (425, 580), (185, 580)]]),
    "R": (600, [[(45, 720), (425, 720), (555, 590), (555, 330), (470, 250), (560, 0), (415, 0), (335, 220), (185, 220), (185, 0), (45, 0)],
                [(185, 350), (375, 350), (415, 390), (415, 540), (375, 580), (185, 580)]]),
    "N": (650, [[(45, 720), (185, 720), (465, 300), (465, 720), (605, 720), (605, 0), (465, 0), (185, 420), (185, 0), (45, 0)]]),
    "K": (640, [[(45, 720), (185, 720), (185, 430), (405, 720), (575, 720), (335, 380), (595, 0), (425, 0), (250, 300), (185, 230), (185, 0), (45, 0)]]),
    "hyphen": (360, [[(50, 430), (310, 430), (310, 290), (50, 290)]]),
}
cmap_extra = {"C": "C", "O": "O", "R": "R", "N": "N", "K": "K", "c": "C", "o": "O", "r": "R", "n": "N", "k": "K", "-": "hyphen"}
order = t.getGlyphOrder()
glyf, hmtx = t["glyf"], t["hmtx"]
for nome, (adv, contornos) in novos.items():
    pen = TTGlyphPen(None)
    for c in contornos:
        pen.moveTo(c[0])
        for p in c[1:]:
            pen.lineTo(p)
        pen.closePath()
    glyf[nome] = pen.glyph()
    hmtx[nome] = (adv, 45)
    if nome not in order:
        order.append(nome)
t.setGlyphOrder(order)
for sub in t["cmap"].tables:
    if sub.isUnicode():
        for ch, g in cmap_extra.items():
            sub.cmap[ord(ch)] = g
if "post" in t:
    t["post"].formatType = 2.0
    t["post"].extraNames = []
    t["post"].mapping = {}
    t["post"].glyphOrder = order
t.flavor = "woff2"
t.save(sys.argv[2] if len(sys.argv) > 2 else "ferramentas/xm-reto-completo.woff2")
