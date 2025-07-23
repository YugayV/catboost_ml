.PHONY: help install test lint format build deploy clean setup-ci

# Переменные
PYTHON := python
PIP := pip
PROJECT_NAME := catboost-gcp-deployment
VENV := venv
GCP_PROJECT_ID := $(shell gcloud config get-value project)

help: ## Показать справку
	@echo "🚀 Доступные команды для $(PROJECT_NAME):"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "📦 Установка зависимостей..."
	$(PYTHON) -m venv $(VENV)
	$(VENV)/Scripts/activate && $(PIP) install --upgrade pip
	$(VENV)/Scripts/activate && $(PIP) install -r requirements/requirements.txt
	$(VENV)/Scripts/activate && $(PIP) install -r requirements/test_requirements.txt
	$(VENV)/Scripts/activate && $(PIP) install -e .
	@echo "✅ Зависимости установлены!"

install-dev: ## Установить зависимости для разработки
	@echo "🛠️ Установка dev зависимостей..."
	$(VENV)/Scripts/activate && $(PIP) install black isort flake8 mypy bandit safety pre-commit
	$(VENV)/Scripts/activate && pre-commit install
	@echo "✅ Dev зависимости установлены!"

test: ## Запустить тесты
	@echo "🧪 Запуск тестов..."
	$(VENV)/Scripts/activate && $(PYTHON) -m pytest tests/ -v

test-coverage: ## Запустить тесты с покрытием
	@echo "📊 Запуск тестов с покрытием..."
	$(VENV)/Scripts/activate && $(PYTHON) -m pytest tests/ -v --cov=classification_model --cov-report=html --cov-report=term

lint: ## Проверить код линтером
	@echo "🔍 Проверка кода..."
	$(VENV)/Scripts/activate && flake8 classification_model/ packages/ml_api/
	$(VENV)/Scripts/activate && black --check classification_model/ packages/ml_api/
	$(VENV)/Scripts/activate && isort --check-only classification_model/ packages/ml_api/

format: ## Отформатировать код
	@echo "✨ Форматирование кода..."
	$(VENV)/Scripts/activate && black classification_model/ packages/ml_api/
	$(VENV)/Scripts/activate && isort classification_model/ packages/ml_api/

security: ## Проверить безопасность
	@echo "🔒 Проверка безопасности..."
	$(VENV)/Scripts/activate && bandit -r classification_model/ packages/ml_api/
	$(VENV)/Scripts/activate && safety check

prepare-data: ## Подготовить тестовые данные
	@echo "📊 Подготовка данных..."
	@if [ ! -f "classification_model/datasets/Dataset.csv" ]; then \
		echo "Создание тестового датасета..."; \
		mkdir -p classification_model/datasets; \
		echo "DV_R,DA_R,AV_R,AA_R,PM_R,FIN_JGMT" > classification_model/datasets/Dataset.csv; \
		$(PYTHON) -c "import random, csv; [csv.writer(open('classification_model/datasets/Dataset.csv', 'a', newline='')).writerow([random.uniform(300, 350), random.uniform(7000, 9000), random.uniform(350, 400), random.uniform(7000, 8000), random.uniform(9000, 10000), random.randint(0, 1)]) for i in range(1000)]"; \
		echo "✅ Тестовый датасет создан!"; \
	else \
		echo "✅ Данные уже существуют!"; \
	fi

train: prepare-data ## Обучить модель
	@echo "🎯 Обучение модели..."
	$(VENV)/Scripts/activate && export PYTHONPATH="${PYTHONPATH}:$(shell pwd)" && $(PYTHON) classification_model/train_pipeline.py
	@echo "✅ Модель обучена!"

api-local: ## Запустить API локально
	@echo "🌐 Запуск API локально..."
	$(VENV)/Scripts/activate && cd packages/ml_api && $(PYTHON) run.py

test-api: ## Протестировать API
	@echo "🧪 Тестирование API..."
	@curl -f http://localhost:5000/health && echo "✅ Health check OK"
	@curl -f http://localhost:5000/version && echo "✅ Version check OK"
	@curl -X POST http://localhost:5000/v1/predict/classification \
		-H "Content-Type: application/json" \
		-d '{"inputs": [{"DV_R": 320, "DA_R": 8000, "AV_R": 370, "AA_R": 7500, "PM_R": 9500}]}' \
		&& echo "✅ Prediction test OK"

build-package: ## Собрать пакет модели
	@echo "📦 Сборка пакета..."
	$(VENV)/Scripts/activate && $(PYTHON) setup.py sdist bdist_wheel
	@echo "✅ Пакет собран!"

build-docker: ## Собрать Docker образ
	@echo "🐳 Сборка Docker образа..."
	docker build -t $(PROJECT_NAME):latest .
	@echo "✅ Docker образ собран!"

test-docker: build-docker ## Протестировать Docker образ
	@echo "🧪 Тестирование Docker образа..."
	docker run -d -p 5000:5000 --name test-api $(PROJECT_NAME):latest
	@sleep 15
	@curl -f http://localhost:5000/health && echo "✅ Docker health check OK"
	@docker stop test-api
	@docker rm test-api
	@echo "✅ Docker тест завершен!"

push-docker: ## Отправить образ в GCR
	@echo "📤 Отправка образа в Google Container Registry..."
	@if [ -z "$(GCP_PROJECT_ID)" ]; then \
		echo "❌ GCP_PROJECT_ID не установлен. Запустите: gcloud config set project YOUR_PROJECT_ID"; \
		exit 1; \
	fi
	gcloud auth configure-docker
	docker tag $(PROJECT_NAME):latest gcr.io/$(GCP_PROJECT_ID)/catboost-api:latest
	docker push gcr.io/$(GCP_PROJECT_ID)/catboost-api:latest
	@echo "✅ Образ отправлен!"

deploy-gcp: push-docker ## Развернуть на Google Cloud Run
	@echo "🚀 Развертывание на Google Cloud Run..."
	gcloud run deploy catboost-api \
		--image gcr.io/$(GCP_PROJECT_ID)/catboost-api:latest \
		--platform managed \
		--region us-central1 \
		--allow-unauthenticated \
		--memory 2Gi \
		--cpu 2 \
		--max-instances 10
	@echo "✅ Развертывание завершено!"

clean: ## Очистить временные файлы
	@echo "🧹 Очистка..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	@echo "✅ Очистка завершена!"

setup-ci: ## Настроить CI/CD
	@echo "🔧 Настройка CI/CD..."
	$(PYTHON) scripts/ci_cd_setup.py
	@echo "✅ CI/CD настроен!"

all: install install-dev prepare-data lint test build-package build-docker ## Выполнить все основные команды

ci: lint test security build-package build-docker test-docker ## Запустить CI пайплайн локально