# DevSecOps NIR Demo

Минимальный экспериментальный стенд для практической апробации методики автоматизированной проверки безопасности FastAPI-приложения в CI/CD-конвейере.

## Состав стенда

- `app/main.py` - тестовое FastAPI-приложение;
- `app/models.py` - Pydantic-модели входных и выходных данных;
- `app/repository.py` - простое in-memory-хранилище демонстрационных задач;
- `requirements.txt` - зависимости Python-приложения;
- `Dockerfile` - сборка контейнерного образа с намеренно расширенной поверхностью анализа для Trivy;
- `.github/workflows/security.yml` - GitHub Actions pipeline с проверками Gitleaks, Bandit, Semgrep, pip-audit и Trivy;
- `reports/` - каталог для локальных отчетов.

## Локальный запуск приложения

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Проверка:

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/tasks
curl http://127.0.0.1:8000/security/artifacts
```

Документация FastAPI доступна по адресу:

```text
http://127.0.0.1:8000/docs
```

## Docker

```bash
docker build -t devsecops-nir:demo .
docker run --rm -p 8000:8000 devsecops-nir:demo
```

В первичной версии Dockerfile намеренно использует образ `python:3.11-slim-bullseye`, устанавливает несколько системных пакетов и запускает приложение от `root`. Это сделано для демонстрации работы Trivy на контейнерном образе и конфигурации контейнеризации.

## Локальные проверки безопасности

Установка Python-инструментов:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install bandit pip-audit semgrep
```

Запуск проверок:

```bash
mkdir -p reports
gitleaks detect --source . --no-git --redact --report-format json --report-path reports/gitleaks.json
bandit -r app -f json -o reports/bandit.json
semgrep scan --config auto --error --json --output reports/semgrep.json app
pip-audit -r requirements.txt --format json --output reports/pip-audit.json
docker build -t devsecops-nir:demo .
trivy image --severity HIGH,CRITICAL --format json --output reports/trivy-image.json devsecops-nir:demo
```

Если Gitleaks не установлен локально, его можно запустить через Docker:

```bash
docker run --rm -v "$PWD:/repo" ghcr.io/gitleaks/gitleaks:v8.24.2 detect --source /repo --no-git --redact --report-format json --report-path /repo/reports/gitleaks.json
```

Для проверки Dockerfile как конфигурационного артефакта:

```bash
trivy config --severity HIGH,CRITICAL --format json --output reports/trivy-config.json .
```

## Запуск pipeline в GitHub Actions

1. Создать репозиторий на GitHub.
2. Выполнить `git init`, добавить remote и отправить проект в ветку `main`.
3. Открыть вкладку `Actions`.
4. Выбрать workflow `Security checks`.
5. Запустить workflow вручную через `Run workflow` или выполнить push в `main`.

Первичный запуск должен завершиться блокировкой security gate из-за тестовых дефектов. После исправления дефектов pipeline запускается повторно.

## Исправление тестовых дефектов

1. Удалить hardcoded AWS-like credentials из `app/main.py` и читать значение из переменной окружения `DEMO_API_TOKEN`.
2. Удалить endpoint `/diagnostics` или заменить `subprocess` на безопасную реализацию без `shell=True`.
3. Обновить `urllib3==1.26.5` до актуальной версии.
4. Сократить список системных пакетов, перейти на более свежий базовый образ при необходимости, создать непривилегированного пользователя в `Dockerfile` и запускать приложение от него.
