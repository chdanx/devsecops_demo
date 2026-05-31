from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=80)
    owner: str = Field(min_length=2, max_length=40)


class Task(BaseModel):
    id: int
    title: str
    owner: str
    status: str


class Artifact(BaseModel):
    name: str
    path: str
    check_type: str
    tool: str


class ServiceInfo(BaseModel):
    name_owner: str
    name: str
    version: str
    description: str
