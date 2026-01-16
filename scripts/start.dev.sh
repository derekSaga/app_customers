#!/bin/sh
set -e

# Instalar dependências com grupo de desenvolvimento
poetry install

# Manter o container de pé
echo "Container pronto. Utilize 'docker exec' para executar comandos."
tail -f /dev/null