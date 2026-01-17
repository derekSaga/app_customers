.PHONY: lint format

lint:
	@echo "🔍 Rodando Ruff (Linter)..."
	poetry run ruff check .
	@echo "🧠 Rodando Mypy (Type Checker)..."
	poetry run mypy .

format:
	@echo "🎨 Formatando código..."
	poetry run ruff check --fix .
	poetry run ruff format .