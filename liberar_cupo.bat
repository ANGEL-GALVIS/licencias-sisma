@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Liberar cupo de licencia
color 0C

if exist "%~dp0..\.venv\Scripts\python.exe" (
  set "PY=%~dp0..\.venv\Scripts\python.exe"
) else (
  set "PY=python"
)

echo.
echo  ================================================
echo   LIBERAR CUPO (desactiva licencia + deja LIBRE)
echo  ================================================
echo.

"%PY%" "%~dp0poner_id.py" --listar
echo.

if not "%~1"=="" (
  set "CUPO=%~1"
) else (
  set /p CUPO="  Cual cupo quieres liberar (1-6): "
)

if "%CUPO%"=="" (
  echo   Cancelado.
  pause
  exit /b 1
)

echo.
set /p CONF="  Confirma liberar el cupo %CUPO%? (S/N) [S]: "
if "%CONF%"=="" set "CONF=S"
if /I not "%CONF%"=="S" (
  echo   Cancelado.
  pause
  exit /b 0
)

echo.
"%PY%" "%~dp0poner_id.py" --liberar %CUPO%
echo.
pause
exit /b %ERRORLEVEL%
