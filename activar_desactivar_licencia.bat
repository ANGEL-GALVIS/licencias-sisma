@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Activar / Desactivar licencias
color 0B

if exist "%~dp0..\.venv\Scripts\python.exe" (
  set "PY=%~dp0..\.venv\Scripts\python.exe"
) else (
  set "PY=python"
)

echo.
echo  ================================================
echo   ACTIVAR / DESACTIVAR LICENCIAS (GitHub)
echo  ================================================
echo.

if /I "%~1"=="" (
  "%PY%" "%~dp0activar_desactivar_licencia.py"
) else (
  "%PY%" "%~dp0activar_desactivar_licencia.py" %*
)

echo.
pause
exit /b %ERRORLEVEL%
