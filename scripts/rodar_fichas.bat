@echo off
REM atalho para rodar a ficha com duplo clique no Windows
cd /d "%~dp0\.."
python scripts\ficha_transfermarkt.py --baixar --dados data\dataset_parte2
echo.
pause
