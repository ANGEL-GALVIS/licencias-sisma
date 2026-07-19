@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Registrar licencia — licencias-sisma
echo.
echo  ================================================
echo   REGISTRAR / ACTIVAR INSTALACION EN GITHUB
echo  ================================================
echo   Repo: ANGEL-GALVIS/licencias-sisma
echo   Uso:
echo     registrar_instalacion.bat CLIENTE_ID
echo     registrar_instalacion.bat --desde-solicitud ruta\SOLICITUD_LICENCIA.txt
echo     registrar_instalacion.bat --inactivar CLIENTE_ID
echo.
if exist "%~dp0..\.venv\Scripts\python.exe" (
  set "PY=%~dp0..\.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
"%PY%" "%~dp0registrar_instalacion.py" %*
echo.
pause
