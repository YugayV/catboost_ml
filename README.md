# Полная инструкция по развертыванию модели CatBoost в Google Cloud Platform

## Описание проекта

Этот проект демонстрирует полный цикл развертывания модели машинного обучения CatBoost в Google Cloud Platform, включая:
- Создание пакета модели
- REST API для предсказаний
- Контейнеризацию с Docker
- Развертывание в Google Cloud Run
- CI/CD пайплайн

## Структура данных

Датасет содержит данные о сварочных процессах:
- **PIPE_NO** - Номер трубы (категориальная переменная)
- **DV_R** - Напряжение дуги (Arc voltage)
- **DA_R** - Ток дуги (Arc current) 
- **AV_R** - Скорость подачи проволоки (Wire feed speed)
- **AA_R** - Ток подачи проволоки (Wire feed current)
- **PM_R** - Мощность (Power)
- **FIN_JGMT** - Финальная оценка качества (целевая переменная: 0 - брак, 1 - годен)

Размер датасета: 739,888 записей

## Предварительные требования

1. **Python 3.8+**
2. **Google Cloud SDK**
3. **Docker Desktop**
4. **Git**
5. **Аккаунт Google Cloud Platform**

## Пошаговая инструкция

### Шаг 1: Настройка Google Cloud Platform

1. Создайте проект в Google Cloud Console
2. Включите необходимые API:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

3. Настройте аутентификацию:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

### Шаг 2: Установка зависимостей

```bash
pip install -r requirements/requirements.txt
pip install -r requirements/test_requirements.txt
```

### Шаг 3: Обучение модели

```bash
python classification_model/train_pipeline.py
```

### Шаг 4: Тестирование модели

```bash
python -m pytest tests/ -v
```

### Шаг 5: Создание пакета модели

```bash
python setup.py sdist bdist_wheel
```

### Шаг 6: Запуск API локально

```bash
cd packages/ml_api
python run.py
```

API будет доступен по адресу: http://localhost:5000

### Шаг 7: Тестирование API

```bash
curl -X POST http://localhost:5000/v1/predict/classification \
  -H "Content-Type: application/json" \
  -d '{"inputs": [{"DV_R": 318, "DA_R": 7798, "AV_R": 365, "AA_R": 7177, "PM_R": 9507}]}'
```

### Шаг 8: Создание Docker образа

```bash
docker build -t catboost-api .
docker run -p 5000:5000 catboost-api
```

### Шаг 9: Развертывание в Google Cloud Run

1. Загрузка образа в Container Registry:
   ```bash
   docker tag catboost-api gcr.io/YOUR_PROJECT_ID/catboost-api
   docker push gcr.io/YOUR_PROJECT_ID/catboost-api
   ```

2. Развертывание в Cloud Run:
   ```bash
   gcloud run deploy catboost-api \
     --image gcr.io/YOUR_PROJECT_ID/catboost-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Шаг 10: Настройка CI/CD

Файл `.github/workflows/deploy.yml` настроен для автоматического развертывания при push в main ветку.

## Использование API

### Endpoints

- `GET /health` - Проверка состояния API
- `GET /version` - Версия модели и API
- `POST /v1/predict/classification` - Предсказание

### Пример запроса

```json
{
  "inputs": [
    {
      "DV_R": 318,
      "DA_R": 7798,
      "AV_R": 365,
      "AA_R": 7177,
      "PM_R": 9507
    }
  ]
}
```

### Пример ответа

```json
{
  "predictions": [1],
  "version": "0.1.0",
  "errors": null
}
```

## Мониторинг и логирование

- Логи доступны в Google Cloud Logging
- Метрики производительности в Google Cloud Monitoring
- Настроены алерты для критических ошибок

## Безопасность

- API защищен HTTPS
- Валидация входных данных
- Ограничение скорости запросов
- Логирование всех запросов

## Масштабирование

Google Cloud Run автоматически масштабирует приложение в зависимости от нагрузки.

## Поддержка

Для вопросов и поддержки создайте issue в репозитории.
