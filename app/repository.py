from app.models import Task, TaskCreate


_tasks: list[Task] = [
    Task(id=1, title="Review dependency report", owner="developer", status="open"),
    Task(id=2, title="Check container scan result", owner="devsecops", status="open"),
]


def list_tasks() -> list[Task]:
    return _tasks


def create_task(task: TaskCreate) -> Task:
    next_id = max((item.id for item in _tasks), default=0) + 1
    created = Task(id=next_id, title=task.title, owner=task.owner, status="open")
    _tasks.append(created)
    return created
