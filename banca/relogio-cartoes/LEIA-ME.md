# Xeque Cards no relógio (Zepp OS)

Aplicativo para relógios Amazfit com Zepp OS 3 ou mais novo (feito para o Active Max, tela redonda de 480 px;
também declara as telas do Active 2 redondo e quadrado). Flashcards (quiz e glossários)
do Observatório (Mundo), do Terra Brasilis (Brasil) e do Xeque-Mate (Medicina), em papel bege e tinta marrom.

Como funciona: o relógio não tem internet própria. A parte `app-side/` roda dentro do app Zepp do celular, baixa
`https://arth4rhenrique883-stack.github.io/banca/cartoes.json` (gerado pelo `banca/ferramentas/montar.py`, poucos KB)
e entrega ao relógio por Bluetooth. O relógio guarda a última edição e abre com ela mesmo longe do celular.

## Instalar (uma vez, num computador)

1. Node.js instalado. No terminal: `npm i -g @zeppos/zeus-cli`
2. Nesta pasta: `npm install`
3. `zeus login` (abre o navegador; entre com a mesma conta do app Zepp do celular)
4. No celular, app Zepp: Perfil > Configurações > Sobre > toque 7 vezes no ícone do Zepp para ligar o Modo desenvolvedor.
5. `zeus preview`, escolha o relógio na lista; aparece um QR code no terminal.
6. No app Zepp: Perfil > o relógio > Modo desenvolvedor > "+" > Escanear, e aponte para o QR code.

Estado em 12/11/2026: código escrito e conferido (sintaxe e importações), mas AINDA NÃO compilado nem testado no
relógio: o servidor do Claude não alcança os endereços da Zepp. O primeiro teste precisa do computador de Arthur.
