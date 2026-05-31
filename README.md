# DevSecOps NIR Demo

Минимальный экспериментальный стенд для практической апробации методики автоматизированной проверки безопасности FastAPI-приложения в CI/CD-конвейере.

## Состав стенда

- `app/main.py` - тестовое FastAPI-приложение;
- `app/models.py` - Pydantic-модели входных и выходных данных;
- `app/repository.py` - простое in-memory-хранилище демонстрационных задач;
- `requirements.txt` - зависимости Python-приложения;
- `Dockerfile` - сборка контейнерного образа;
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

В исправленной версии Dockerfile использует компактный образ `python:3.13-alpine`, не устанавливает лишние системные пакеты и запускает приложение от непривилегированного пользователя `appuser`.

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

В текущей версии проекта тестовые дефекты уже исправлены:

1. Hardcoded credentials удалены из `app/main.py`, конфигурация читается через переменные окружения.
2. Endpoint `/diagnostics` с `subprocess` и `shell=True` удален.
3. Зависимости обновлены до актуальных версий.
4. Dockerfile переведен на компактный базовый образ и непривилегированного пользователя.

Ожидаемый результат повторного GitHub Actions запуска:

```text
Security gate passed. No blocking findings were detected.
```
