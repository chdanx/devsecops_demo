import os

from fastapi import FastAPI

from app.models import Artifact, ServiceInfo, Task, TaskCreate
from app.repository import create_task, list_tasks


app = FastAPI(
    title="DevSecOps NIR",
    description="Экспериментальный сервис FastAPI для проверок безопасности в рамках подхода DevSecOps.",
    version="0.3.0",
)


@app.get("/")
def read_root() -> ServiceInfo:
    return ServiceInfo(
        name_owner="Danila Badetskiy",
        name="DevSecOps NIR Demo",
        version="0.3.0",
        description="Минималистичный API, используемый в качестве объекта для автоматизированных проверок безопасности.",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/config")
def read_config() -> dict[str, str]:
    demo_token = os.getenv("DEMO_API_TOKEN", "")
    return {
        "mode": os.getenv("APP_MODE", "demo"),
        "configuration_source": "environment",
        "external_secret_configured": str(bool(demo_token)).lower(),
    }


@app.get("/tasks", response_model=list[Task])
def get_tasks() -> list[Task]:
    return list_tasks()


@app.post("/tasks", response_model=Task, status_code=201)
def add_task(task: TaskCreate) -> Task:
    return create_task(task)


@app.get("/security/artifacts", response_model=list[Artifact])
def get_security_artifacts() -> list[Artifact]:
    return [
        Artifact(
            name="Application source code",
            path="app/",
            check_type="SAST",
            tool="Bandit, Semgrep",
        ),
        Artifact(
            name="Python dependencies",
            path="requirements.txt",
            check_type="SCA",
            tool="pip-audit",
        ),
        Artifact(
            name="Secrets in source and configuration files",
            path=".",
            check_type="Secrets scanning",
            tool="Gitleaks",
        ),
        Artifact(
            name="Docker image and Dockerfile",
            path="Dockerfile",
            check_type="Container scanning",
            tool="Trivy",
        ),
    ]
