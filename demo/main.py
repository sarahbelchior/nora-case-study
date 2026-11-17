"""Demonstração pública, local e sem dados reais de uma parte da Nora.

API FastAPI + SQLite para tarefas e organização. Este código NÃO é o
backend privado completo da Nora e NÃO deve ser publicado como serviço online.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from pathlib import Path
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("NORA_DEMO_DB", str(ROOT.parent / "instance" / "nora-demo.sqlite")))
TZ = ZoneInfo("America/Sao_Paulo")
CATEGORIES = {"pessoal", "estudos", "rotina"}


def now_iso() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


def today_iso() -> str:
    return datetime.now(TZ).date().isoformat()


@contextmanager
def db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH, timeout=5) as con:
        con.row_factory = sqlite3.Row
        yield con


def initialize_db():
    with db_connection() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            due_date TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )""")
        count = db.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            # Dados fictícios de demonstração, sem informações pessoais.
            for title, category in [
                ("Revisar conteúdos de estudo", "estudos"),
                ("Organizar compromissos", "pessoal"),
                ("Fazer uma pausa consciente", "rotina"),
            ]:
                db.execute(
                    "INSERT INTO tasks(title,category,due_date,created_at) VALUES (?,?,?,?)",
                    (title, category, today_iso(), now_iso()),
                )


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    category: Literal["pessoal", "estudos", "rotina"] = "pessoal"
    due_date: str = Field(default_factory=today_iso)


class TaskUpdate(BaseModel):
    done: bool


def validated_date(value: str) -> str:
    try:
        if datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d") != value:
            raise ValueError("formato inesperado")
    except ValueError as exc:
        raise HTTPException(422, "Data inválida: use AAAA-MM-DD") from exc
    return value


def as_task(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "title": row["title"],
            "category": row["category"], "due_date": row["due_date"],
            "done": bool(row["done"]), "created_at": row["created_at"]}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    initialize_db()
    yield


app = FastAPI(
    title="Nora Demo — API de organização",
    description="Demonstração pública local, com dados fictícios, sem autenticação e sem APIs externas.",
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/status")
def status():
    return {"application": "Nora Demo", "mode": "local_demo", "timezone": "America/Sao_Paulo"}


@app.get("/api/tasks")
def list_tasks():
    with db_connection() as db:
        rows = db.execute("SELECT * FROM tasks ORDER BY done ASC, due_date ASC, id DESC").fetchall()
    return [as_task(row) for row in rows]


@app.get("/api/overview")
def overview():
    with db_connection() as db:
        total, done = db.execute(
            "SELECT COUNT(*), COALESCE(SUM(done), 0) FROM tasks WHERE due_date = ?",
            (today_iso(),),
        ).fetchone()
    return {"today": today_iso(), "total": total, "done": done,
            "pending": total - done}


@app.post("/api/tasks", status_code=201)
def create_task(task: TaskCreate):
    title = task.title.strip()
    if not title:
        raise HTTPException(422, "Informe o título da tarefa")
    due_date = validated_date(task.due_date)
    with db_connection() as db:
        cur = db.execute(
            "INSERT INTO tasks(title,category,due_date,created_at) VALUES (?,?,?,?)",
            (title, task.category, due_date, now_iso()),
        )
        row = db.execute("SELECT * FROM tasks WHERE id=?", (cur.lastrowid,)).fetchone()
    return as_task(row)


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate):
    with db_connection() as db:
        cur = db.execute("UPDATE tasks SET done=? WHERE id=?", (int(body.done), task_id))
        if cur.rowcount == 0:
            raise HTTPException(404, "Tarefa não encontrada")
        row = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    return as_task(row)


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with db_connection() as db:
        cur = db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "Tarefa não encontrada")
