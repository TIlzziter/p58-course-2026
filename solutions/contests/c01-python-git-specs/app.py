"""Контест 1 — эталон E1 и E4 (доска задач)."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Контест 1")

ROOMS = {"abc": {"players": ["Аня"]}}
COLUMNS = ["backlog", "todo", "in_progress", "review", "done"]
ALLOWED = {("backlog", "todo"), ("todo", "in_progress"), ("in_progress", "review"),
           ("review", "done"), ("review", "in_progress")}
ISSUES: dict[int, dict] = {}


@app.get("/ping")
def ping():
    return {"pong": True}


@app.get("/rooms/{room_id}")
def get_room(room_id: str):
    if room_id not in ROOMS:
        raise HTTPException(404, "Комната не найдена")
    return {"id": room_id, **ROOMS[room_id]}


class IssueIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class MoveIn(BaseModel):
    to: str


@app.post("/issues", status_code=201)
def create_issue(body: IssueIn):
    new_id = max(ISSUES, default=0) + 1
    ISSUES[new_id] = {"id": new_id, "title": body.title, "status": "backlog"}
    return ISSUES[new_id]


@app.get("/issues")
def list_issues(status: str | None = None):
    if status is not None and status not in COLUMNS:
        raise HTTPException(422, "Неизвестная колонка")
    return [i for i in ISSUES.values() if status is None or i["status"] == status]


@app.post("/issues/{issue_id}/move")
def move_issue(issue_id: int, body: MoveIn):
    issue = ISSUES.get(issue_id)
    if issue is None:
        raise HTTPException(404, "Задача не найдена")
    if (issue["status"], body.to) not in ALLOWED:
        raise HTTPException(409, f"Нельзя перейти из {issue['status']} в {body.to}")
    issue["status"] = body.to
    return issue


@app.get("/board")
def board():
    result = {c: [i["id"] for i in ISSUES.values() if i["status"] == c] for c in COLUMNS}
    total = len(ISSUES)
    result["done_percent"] = round(len(result["done"]) * 100 / total) if total else 0
    return result
