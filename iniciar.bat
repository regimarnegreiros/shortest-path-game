@ECHO OFF

python --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO msgbox "Python nao esta instalado. Por favor instale-o." > %tmp%\tmp.vbs
    CSCRIPT /nologo %tmp%\tmp.vbs
    DEL %tmp%\tmp.vbs

    EXIT /B 1
)

pip freeze > %tmp%\pip_freeze.tmp

FINDSTR /I Flask %tmp%\pip_freeze.tmp > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    GOTO ERRO
)

FINDSTR /I NetworkX %tmp%\pip_freeze.tmp > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    GOTO ERRO
)

DEL %tmp%\pip_freeze.tmp
START /MIN "Flask" python .\src\backend\app.py

CHOICE /C T /N /M "Pressione [T] para sair..."
TASKKILL /T /F /FI "WINDOWTITLE EQ Flask" > NUL 2>&1
EXIT

:ERRO

DEL %tmp%\pip_freeze.tmp
ECHO msgbox "Flask ou NetworkX nao instalados. Por favor instale-os com pip install -r requirements.txt" > %tmp%\tmp.vbs
CSCRIPT /nologo %tmp%\tmp.vbs
DEL %tmp%\tmp.vbs

EXIT
