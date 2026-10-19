@echo off
REM [IA] Claude Code (Claude Opus 5) - atalho para rodar a ficha com duplo clique no Windows
cd /d "%~dp0\.."
python scripts\ficha_transfermarkt.py --dados data\dataset_parte2
echo.
pause
