@echo off
title Xeque Cards no relogio
cd /d "%~dp0"
echo.
echo  XEQUE CARDS NO RELOGIO
echo  ---------------------
where node >nul 2>nul
if errorlevel 1 (
  echo  Falta o Node.js. Instale a versao LTS em https://nodejs.org , feche esta janela e abra de novo.
  pause
  exit /b 1
)
echo  1 de 4: instalando a ferramenta da Zepp...
call npm install -g @zeppos/zeus-cli
echo  2 de 4: preparando o aplicativo...
call npm install
echo  3 de 4: entre com a MESMA conta do app Zepp do celular (o navegador vai abrir)...
call zeus login
echo  4 de 4: escolha o seu relogio na lista com as setas e Enter. Vai aparecer um QR code.
echo  No celular: app Zepp, Perfil, seu relogio, Modo desenvolvedor, +, Escanear.
call zeus preview
echo.
pause
