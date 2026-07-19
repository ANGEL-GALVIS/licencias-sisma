@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Poner ID de licencia (cupos 1-6)
if exist "%~dp0..\.venv\Scripts\python.exe" (
  set "PY=%~dp0..\.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
echo.
echo  ================================================
echo   CUPOS DE LICENCIA (1 a 6) — solo ponga el ID
echo  ================================================
echo   Uso:
echo     poner_id.bat 1 codigo_que_envio_el_cliente
echo     poner_id.bat 2 otro_codigo
echo     poner_id.bat --listar
echo     poner_id.bat 1 codigo --inactivar
echo.
"%PY%" "%~dp0poner_id.py" %*
echo.
pause
