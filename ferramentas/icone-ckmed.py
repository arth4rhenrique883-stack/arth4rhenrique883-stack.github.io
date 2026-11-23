#!/usr/bin/env python3
"""v103 (23/11/2026, Caro-Kann Med): ECG encurtado (x 62..178) e coroa maior/mais grossa, a pedido do Arthur.
v96 (07/11/2026, só xmp): ícone com a coroa da rainha no ECG bem mais grossa e visível.
Redesenha o traço do ECG do título (mesma geometria do SVG .xm-ecg, viewBox 240x46; recorta x 36..204 para a coroa ocupar mais) com PIL em 4x:
traço colorido grosso (gradiente rosa→ciano→violeta) com contorno preto, anéis maiores nas pontas da coroa.
Gera rainha3-192/180/512.png e rainha3-maskable-512.png em periodos/ (fundo branco, 512/192 com cantos arredondados).
Uso: python3 icone-grosso.py <raiz do Pages>   (com XM_APK_RES=<pasta res/ do flavor xmp> também gera os mipmaps do APK)"""
import os, sys
from PIL import Image, ImageDraw
P = os.path.join(sys.argv[1], 'periodos')
PTS = [(62,34),(66,30),(70,30),(74,34),(100,34),(104,38),(109,15),(115,25),(120,6),(125,25),(131,15),(136,42),(140,34),(160,34),(166,28),(172,28),(178,34)]
RINGS = [(109,12.4),(120,3.4),(131,12.4)]
STOPS = [(0,(255,93,143)),(.5,(63,214,230)),(1,(167,123,255))]
def grad(t):
    for (a,ca),(b,cb) in zip(STOPS, STOPS[1:]):
        if t <= b:
            k = (t-a)/(b-a); return tuple(int(ca[i]+(cb[i]-ca[i])*k) for i in range(3))
    return STOPS[-1][1]
def desenha(n, ocup, raio, arred=True, ss=4, transp=False):
    N = n*ss; s = N*ocup/116.0
    ox = (N - 116*s)/2 - 62*s; oy = (N - 46*s)/2 - 0.5*s     # centra a faixa na vertical
    X = lambda x: ox + x*s; Y = lambda y: oy + y*s
    W = 6.8*s    # espessura do traço colorido (unid. do viewBox): 8,5 un., 1,7x a do título
    O = 2.3*s            # espessura do contorno preto de cada lado
    def mascara(w, rr):
        m = Image.new('L', (N, N), 0); d = ImageDraw.Draw(m)
        for a, b in zip(PTS, PTS[1:]): d.line([(X(a[0]),Y(a[1])),(X(b[0]),Y(b[1]))], fill=255, width=int(w))
        for p in PTS: d.ellipse((X(p[0])-w/2, Y(p[1])-w/2, X(p[0])+w/2, Y(p[1])+w/2), fill=255)
        for cx, cy in RINGS:
            r = rr*s; d.ellipse((X(cx)-r, Y(cy)-r, X(cx)+r, Y(cy)+r), fill=255)
        return m
    out = mascara(W + 2*O, 4.6 + O/s)     # contorno
    core = mascara(W, 4.6)
    # furo preto no centro dos anéis (identidade da coroa)
    hole = Image.new('L', (N, N), 0); hd = ImageDraw.Draw(hole)
    for cx, cy in RINGS:
        r = 1.7*s; hd.ellipse((X(cx)-r, Y(cy)-r, X(cx)+r, Y(cy)+r), fill=255)
    cores = [grad(min(1, max(0, (i - X(62))/(116*s)))) for i in range(N)]
    row = Image.new('RGB', (N, 1))
    row.putdata(cores); gx = row.resize((N, N))
    base = Image.new('RGBA', (N, N), (255,255,255,0 if transp else 255))
    blk = Image.new('RGBA', (N, N), (8,8,12,255)); base.paste(blk, (0,0), out)
    base.paste(gx.convert('RGBA'), (0,0), core)
    base.paste(blk, (0,0), hole)
    if transp:   # RGBA sem fundo: o paste acima não grava alfa, então recompõe a máscara
        a = Image.new('L', (N, N), 0); a.paste(255, (0,0), out); a.paste(255, (0,0), core); base.putalpha(a)
    img = base.resize((n, n), Image.LANCZOS)
    if arred:
        m = Image.new('L', (n*4, n*4), 0)
        ImageDraw.Draw(m).rounded_rectangle((0,0,n*4-1,n*4-1), radius=int(n*4*raio), fill=255)
        img.putalpha(m.resize((n, n), Image.LANCZOS))
    return img
saidas = {'rainha3-512.png': (512, .90, .22, True), 'rainha3-192.png': (192, .90, .22, True),
          'rainha3-180.png': (180, .90, 0, False), 'rainha3-maskable-512.png': (512, .68, 0, False)}
for nome, (n, oc, r, a) in saidas.items():
    im = desenha(n, oc, r, a)
    if not a: im = im.convert('RGB')
    im.save(os.path.join(P, nome))
print('ok')

# APK (android/app/src/xmp/res/mipmap-*): ic_frente (transparente, dentro da zona segura), ic_fundo (branco), ic_launcher (legado, arredondado)
apk = os.environ.get('XM_APK_RES')
if apk:
    for d, base in {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}.items():
        pasta = os.path.join(apk, 'mipmap-' + d); os.makedirs(pasta, exist_ok=True)
        c = base * 108 // 48
        desenha(c, .62, 0, False, transp=True).save(os.path.join(pasta, 'ic_frente.png'))
        Image.new('RGB', (c, c), (255, 255, 255)).save(os.path.join(pasta, 'ic_fundo.png'))
        desenha(base, .94, .22, True).save(os.path.join(pasta, 'ic_launcher.png'))
    print('apk ok')
