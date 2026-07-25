@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Activar licencia - solo pegue el ID
color 0B

if exist "%~dp0..\.venv\Scripts\python.exe" (
  set "PY=%~dp0..\.venv\Scripts\python.exe"
) else (
  set "PY=python"
)

echo.
echo  ================================================
echo   ACTIVAR LICENCIA
echo  ================================================
echo   1. Pegue el ID del cliente y pulse Enter
echo   2. El sistema limpia el ID, elige cupo libre,
echo      crea licencia_ID.txt (activo) y sube a GitHub
echo.
echo   Tip: puede pegar licencia_xxx.txt — se limpia solo
echo  ================================================
echo.

REM Sin argumentos: solo pide el ID (cupo libre automatico)
if "%~1"=="" (
  "%PY%" "%~dp0poner_id.py" --interactivo
  echo.
  pause
  exit /b %ERRORLEVEL%
)

REM Con argumentos: pasar tal cual (ID solo, o cupo+ID, o --listar / --liberar)
"%PY%" "%~dp0poner_id.py" %*
echo.
pause
exit /b %ERRORLEVEL%
