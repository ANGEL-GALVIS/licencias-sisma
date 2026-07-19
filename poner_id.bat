@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Poner ID de licencia (cupos 1-12)
color 0B

if exist "%~dp0..\.venv\Scripts\python.exe" (
  set "PY=%~dp0..\.venv\Scripts\python.exe"
) else (
  set "PY=python"
)

echo.
echo  ================================================
echo   CUPOS DE LICENCIA (1 a 12)
echo  ================================================
echo.

REM Si ya trajeron argumentos (desde CMD), usarlos directo
if not "%~1"=="" (
  "%PY%" "%~dp0poner_id.py" %*
  echo.
  pause
  exit /b %ERRORLEVEL%
)

REM Doble clic / sin argumentos: preguntar
"%PY%" "%~dp0poner_id.py" --listar
echo.
set /p CUPO="  Numero de cupo (1-12): "
if "%CUPO%"=="" (
  echo   Cancelado.
  pause
  exit /b 1
)
set /p IDCLIENTE="  Pegue el ID del cliente: "
if "%IDCLIENTE%"=="" (
  echo   Cancelado: falta el ID.
  pause
  exit /b 1
)
echo.
set /p INACT="  Desactivar en vez de activar? (S/N) [N]: "
if /I "%INACT%"=="S" (
  "%PY%" "%~dp0poner_id.py" %CUPO% %IDCLIENTE% --inactivar
) else (
  "%PY%" "%~dp0poner_id.py" %CUPO% %IDCLIENTE%
)
echo.
pause
exit /b %ERRORLEVEL%
