#!/bin/sh

python --version >&1 >/dev/null
if [ $? -ne 0 ]; then
    echo "Python nao esta instalado. Por favor instale-o."
    exit 1
fi

PACOTES_INSTALADOS=1

pip freeze >/tmp/pip_freeze.txt

grep -i "Flask" /tmp/pip_freeze.txt >&1 >/dev/null || PACOTES_INSTALADOS=0
grep -i "NetworkX" /tmp/pip_freeze.txt >&1 >/dev/null || PACOTES_INSTALADOS=0

if [ $PACOTES_INSTALADOS -ne 1 ]; then
    rm /tmp/pip_freeze.txt
    echo "Flask ou NetworkX nao estao instalados. Por favor instale-os com" \
    "pip install -r requirements.txt."
    exit 1
fi

rm /tmp/pip_freeze.txt
echo "Acesse o aplicativo em http://localhost:5000. Para parar, use Ctrl+C."

python ./src/backend/app.py
