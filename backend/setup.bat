@echo off
echo ========================================
echo Creando entorno virtual en carpeta venv
echo ========================================
python -m venv venv

if %ERRORLEVEL% NEQ 0 (
    echo Error al crear el entorno virtual. Asegúrate de tener Python instalado y en el PATH.
    pause
    exit /b
)

echo.
echo ========================
echo Activando entorno virtual
echo ========================

call venv\Scripts\activate

if exist C:\github\theofficegurus\EyeOfSauron\backend\requirements.txt (
    echo.
    echo =====================================
    echo Instalando dependencias de requirements.txt
    echo =====================================
    pip install -r C:\github\theofficegurus\EyeOfSauron\backend\requirements.txt
) else (
    echo.
    echo No se encontro requirements.txt
    echo Puedes instalar paquetes manualmente con pip
)

echo.
echo Entorno virtual listo. 
echo Un solo ojo sin párpados, envuelto en llamas, fijo en la red. No parpadea. No duerme. Lo ve todo.

pause
