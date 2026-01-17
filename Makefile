.PHONY: lint format diff-dump diff-copy

lint:
	@echo "🔍 Rodando Ruff (Linter)..."
	poetry run ruff check .
	@echo "🧠 Rodando Mypy (Type Checker)..."
	poetry run mypy .

format:
	@echo "🎨 Formatando código..."
	poetry run ruff check --fix .
	poetry run ruff format .

diff-dump:
	@echo "📋 Exportando diff (staged) para t.txt..."
	git diff --staged HEAD > t.txt
	@echo "✅ Arquivo 't.txt' gerado com sucesso."

diff-copy:
	@echo "📋 Tentando copiar diff para o clipboard..."
	@# Tenta detectar ferramentas comuns de clipboard (Mac, Linux, WSL)
	@if command -v pbcopy > /dev/null; then git diff --staged HEAD | pbcopy; echo "✅ Copiado para o clipboard (pbcopy)"; \
	elif command -v xclip > /dev/null; then git diff --staged HEAD | xclip -selection clipboard; echo "✅ Copiado para o clipboard (xclip)"; \
	elif command -v clip.exe > /dev/null; then git diff --staged HEAD | clip.exe; echo "✅ Copiado para o clipboard (clip.exe)"; \
	else echo "❌ Nenhuma ferramenta de clipboard encontrada (instale xclip ou use 'make diff-dump')."; exit 1; \
	fi