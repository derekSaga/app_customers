# App Customers Service

Este microsserviço é responsável pelo gerenciamento de clientes. Ele foi construído utilizando **Python** com **FastAPI**, seguindo os princípios da **Clean Architecture** para garantir desacoplamento, testabilidade e manutenibilidade.

## 🏗 Arquitetura

O projeto está organizado em camadas concêntricas, onde as dependências apontam para dentro (em direção ao Domínio).

### Estrutura de Diretórios (`src/`)

- **`domain/`**: O núcleo da aplicação. Contém as regras de negócio puras, Entidades (`Customer`), Value Objects (`Email`), Exceções de Domínio e Interfaces de Serviços. Não depende de nenhuma biblioteca externa ou framework.
- **`usecases/`**: Contém a lógica de aplicação (casos de uso). Define as portas (interfaces) que os adaptadores devem implementar.
  - **`handlers/`**: Implementação do padrão *Chain of Responsibility* para processamento de regras.
- **`adapters/`**: Implementações concretas das interfaces definidas nos casos de uso.
  - **`api/`**: Controladores REST (FastAPI).
  - **`database/`**: Repositórios SQLAlchemy e configuração do banco.
  - **`cache/`**: Implementação de cache com Redis.
  - **`publishers/`**: Adaptadores para mensageria (Google Pub/Sub).
- **`di/`**: (Dependency Injection) Configuração e injeção de dependências. Responsável por "colar" as camadas, instanciando os adaptadores e injetando-os nos casos de uso.
- **`config/`**: Variáveis de ambiente e configurações globais (Pydantic Settings).

## 🚀 Tecnologias

- **Linguagem**: Python 3.14+
- **Framework Web**: FastAPI
- **Banco de Dados**: PostgreSQL (via SQLAlchemy Async)
- **Cache/Lock**: Redis
- **Mensageria**: Google Cloud Pub/Sub
- **Logging**: Loguru
- **Observabilidade**: Correlation ID Middleware

## ⚙️ Fluxos Principais

### Criação de Cliente (`POST /api/v1/customers`)

Este endpoint atua como gatilho para o processo assíncrono. Ele retorna `202 Accepted` imediatamente após as validações iniciais e publicação do evento.

O fluxo utiliza o padrão **Chain of Responsibility**:

1.  **`RedisCheckHandler`**:
    -   Verifica se o e-mail já existe no cache (Short-circuit).
    -   Aplica um lock temporário para evitar condições de corrida.
2.  **`DomainValidationHandler`**:
    -   Verifica a existência no banco de dados (Source of Truth).
    -   Gera a entidade `Customer` com ID único (sem persistir ainda).
3.  **`PublishHandler`**:
    -   Publica o evento `events.customer.created` no Pub/Sub. A persistência real é feita por um Worker consumidor.

## 🛠 Como Rodar

### Pré-requisitos

- Python 3.14+
- Docker (opcional, para rodar Redis/Postgres)

### Instalação

1. Clone o repositório e instale as dependências:

```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente (crie um arquivo `.env` baseado no `src/config/settings.py`):

```env
REDIS_HOST=localhost
REDIS_PORT=6379
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db_customers
GOOGLE_CLOUD_PROJECT=seu-projeto-gcp
```

3. Execute a aplicação:

```bash
uvicorn src.main:app --reload
```

A documentação interativa da API estará disponível em: `http://localhost:8000/docs`

## 📂 Mapa do Projeto

Uma visão geral de onde encontrar cada componente:

```text
src
├── adapters
│   ├── api          # Rotas e Controllers (FastAPI)
│   ├── cache        # Implementação Redis
│   ├── database     # Tabelas e Repositórios SQL
│   └── publishers   # Implementação PubSub
├── config           # Settings
├── di               # Injeção de Dependência (Factories)
├── domain
│   ├── entities     # Entidades (Customer)
│   ├── services     # Serviços de Domínio
│   └── value_objects
├── main.py          # Entrypoint
└── usecases
    ├── ports        # Interfaces (Repositories, Publishers)
    └── v1
        └── customers
            ├── create_customer.py # Caso de Uso Principal
            └── handlers           # Steps do Chain of Responsibility
```

## 🧪 Testes

Para rodar os testes (se configurados com pytest):

```bash
pytest
```