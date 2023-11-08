ENV_NAME=gym-abalone-venv
env:
	rm -rf $(ENV_NAME)
	python3 -m venv $(ENV_NAME)
	./$(ENV_NAME)/bin/python3 -m pip install -U pip
	./$(ENV_NAME)/bin/python3 -m pip install -r requirements.txt
	./$(ENV_NAME)/bin/python3 -m pip install -e . --no-deps
	./$(ENV_NAME)/bin/python3 -m pre_commit install --install-hooks --overwrite

lint: ## Run linters
	./$(ENV_NAME)/bin/pre-commit run -a

test: lint ## Run tests
	./$(ENV_NAME)/bin/pytest -vv --durations=10 --cov-fail-under=50 --cov=gym-abalone --cov-report html tests/
