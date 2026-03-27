@echo off
set "py_script=%~dp0auto_connect_flow.py"

echo ======================================================
echo    Samsung Flow Auto-Connect (Note 9 + Tablet)
echo ======================================================
echo.
echo Requisitos:
echo 1. Asegura que Samsung DeX este ABIERTO en Windows.
echo 2. Note 9 y Tablet deben estar visibles por ADB.
echo.
pause

python "%py_script%"

echo.
echo Si el Note 9 no entra a DeX, reconecta el cable USB.
echo.
pause
