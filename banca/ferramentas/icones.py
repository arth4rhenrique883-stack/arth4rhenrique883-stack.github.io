"""Gera os ícones das publicações no estilo de jornal antigo (papel bege, tinta marrom, filetes duplos, letra condensada)."""
import os
from PIL import Image, ImageDraw, ImageFont
AQUI = os.path.dirname(os.path.abspath(__file__))
BANCA = os.path.dirname(AQUI)
PAPEL = (236, 227, 212); TINTA = (58, 45, 43)
PUBS = {"jornal": ("J", "CADA DIA"), "observatorio": ("O", "DIÁRIO"), "xequemate": ("X", "MEDICINA"), "lafaiete": ("C", "LAFAIETE"), "brasil": ("T", "BRASIL"), "mundo-lafaiete": ("M", "MUNDO"), "mundo": ("O", "MUNDO"), "juizdefora": ("M", "JUIZ DE FORA"), "caso-master": ("D", "DOSSIÊ")}
FONTE = os.path.join(AQUI, "Anton.ttf")

def icone(letra, rotulo, tam, maskable):
    S = 1024
    im = Image.new("RGB", (S, S), PAPEL); d = ImageDraw.Draw(im)
    m = 170 if maskable else 90           # margem (área segura no maskable)
    w = S - 2 * m
    def duplo(y, desce):
        d.rectangle([m, y, S - m, y + 18], fill=TINTA)
        y2 = y + 34 if desce else y - 34
        d.rectangle([m, y2, S - m, y2 + 8], fill=TINTA)
    topo = m + 10; base = S - m - 28
    duplo(topo, True); duplo(base, False)
    fr = ImageFont.truetype(FONTE, int(w * 0.12))
    rb = d.textbbox((0, 0), rotulo, font=fr)
    rh = rb[3] - rb[1]
    area_top = topo + 70; area_bot = base - 60
    alvo = (area_bot - area_top) - 30 - rh
    tam_f = 100
    while True:
        f = ImageFont.truetype(FONTE, tam_f + 10)
        bb = d.textbbox((0, 0), letra, font=f)
        if bb[3] - bb[1] > alvo: break
        tam_f += 10
    f = ImageFont.truetype(FONTE, tam_f)
    bb = d.textbbox((0, 0), letra, font=f)
    lw, lh = bb[2] - bb[0], bb[3] - bb[1]
    total = lh + 30 + rh
    y0 = area_top + (area_bot - area_top - total) / 2
    d.text(((S - lw) / 2 - bb[0], y0 - bb[1]), letra, font=f, fill=TINTA)
    d.text(((S - (rb[2] - rb[0])) / 2 - rb[0], y0 + lh + 30 - rb[1]), rotulo, font=fr, fill=TINTA)
    return im.resize((tam, tam), Image.LANCZOS)

PUBS[""] = ("X", "NEWS")  # o ícone do aplicativo único, na raiz da banca/
for pasta, (letra, rotulo) in PUBS.items():
    out = os.path.join(BANCA, pasta); os.makedirs(out, exist_ok=True)
    for t in (180, 192, 512):
        icone(letra, rotulo, t, False).save(os.path.join(out, f"icone-{t}.png"), optimize=True)
    icone(letra, rotulo, 512, True).save(os.path.join(out, "icone-maskable-512.png"), optimize=True)
print("ok")
