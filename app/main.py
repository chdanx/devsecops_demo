import os
import subprocess

from fastapi import FastAPI

from app.models import Artifact, ServiceInfo, Task, TaskCreate
from app.repository import create_task, list_tasks


app = FastAPI(
    title="DevSecOps NIR",
    description="Экспериментальный сервис FastAPI для проверок безопасности в рамках подхода DevSecOps.",
    version="0.2.0",
)

# Test defect for primary scan: hardcoded fake AWS-like credentials.
AWS_ACCESS_KEY_ID = "AKIA3W5ODU6QWKLCMT7A"
AWS_SECRET_ACCESS_KEY = "mF9bN5xK7qR2tY4uI8oP0aS1dF3gH5jK7lZ9xC"


@app.get("/")
def read_root() -> ServiceInfo:
    return ServiceInfo(
        name_owner="Danila Badetskiy",
        name="DevSecOps NIR Demo",
        version="0.2.0",
        description="Минималистичный API, используемый в качестве объекта для автоматизированных проверок безопасности.",
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/config")
def read_config() -> dict[str, str]:
    return {
        "mode": os.getenv("APP_MODE", "demo"),
        "token_source": "hardcoded",
        "token_preview": AWS_ACCESS_KEY_ID[:6],
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


@app.get("/diagnostics")
def diagnostics(host: str = "127.0.0.1") -> dict[str, str]:
    result = subprocess.check_output(
        f"echo diagnostics for {host}",
        shell=True,
        text=True,
        stderr=subprocess.STDOUT,
        timeout=3,
    )
    return {"result": result}
