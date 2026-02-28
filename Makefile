.PHONY: lint format diff-dump diff-copy test

ARGS ?= .

lint:
	@echo "🔍 Running Ruff (Linter)..."
	poetry run ruff check $(ARGS)
	@echo "🧠 Running Mypy (Type Checker)..."
	# Run mypy to check types
	poetry run mypy $(ARGS)

format:
	@echo "🎨 Formatting code..."
	poetry run ruff check --fix $(ARGS)
	poetry run ruff format $(ARGS)

diff-dump:
	@echo "📋 Exporting diff (staged) to t.txt..."
	git diff --staged HEAD > t.txt
	@echo "✅ File 't.txt' generated successfully."

diff-copy:
	@echo "📋 Trying to copy diff to clipboard..."
	@# Tries to detect common clipboard tools (Mac, Linux, WSL)
	@if command -v pbcopy > /dev/null; then git diff --staged HEAD | pbcopy; echo "✅ Copied to clipboard (pbcopy)"; \
	elif command -v xclip > /dev/null; then git diff --staged HEAD | xclip -selection clipboard; echo "✅ Copied to clipboard (xclip)"; \
	elif command -v clip.exe > /dev/null; then git diff --staged HEAD | clip.exe; echo "✅ Copied to clipboard (clip.exe)"; \
	else echo "❌ No clipboard tool found (install xclip or use 'make diff-dump')."; exit 1; \
	fi

test:
	@echo "🧪 Running tests with coverage..."
	poetry run pytest --cov=src --cov-report=term-missing --cov-report=html