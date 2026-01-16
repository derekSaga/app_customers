#!/bin/sh
set -e

# Validar variáveis de ambiente
if [ -z "$APP_PORT" ]; then
  echo "ERRO: APP_PORT não está definida. Usando porta padrão 8000"
  export APP_PORT=8000
fi

echo "Iniciando aplicação na porta $APP_PORT..."
uvicorn src.main:app --host 0.0.0.0 --port $APP_PORT