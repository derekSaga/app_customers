FROM python:3.14.2-alpine

WORKDIR /app

# Instalar Poetry
RUN pip install --no-cache-dir poetry

# Copiar arquivos de configuração
COPY pyproject.toml poetry.lock* /app/

# Instalar dependências com Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --without dev --no-root

# Copiar o código da aplicação
COPY . /app

# Expor a porta padrão do FastAPI
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["./start.sh"]
