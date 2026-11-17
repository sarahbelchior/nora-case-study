"""Testes de API com banco temporário. Não acessam serviços externos."""
import pytest
from fastapi.testclient import TestClient
from demo import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "demo-test.sqlite")
    with TestClient(main.app) as c:
        yield c


def test_ui_and_docs_available(client):
    assert client.get("/").status_code == 200
    assert "Nora Demo" in client.get("/").text
    assert client.get("/docs").status_code == 200


def test_initial_sample_tasks(client):
    rows = client.get("/api/tasks").json()
    assert len(rows) == 3
    assert all(row["done"] is False for row in rows)
    assert client.get("/api/status").json()["mode"] == "local_demo"


def test_create_update_delete_task(client):
    created = client.post("/api/tasks", json={"title": "Preparar entrevista", "category": "estudos", "due_date": "2026-11-20"})
    assert created.status_code == 201
    ident = created.json()["id"]
    assert created.json()["title"] == "Preparar entrevista"
    completed = client.patch(f"/api/tasks/{ident}", json={"done": True})
    assert completed.status_code == 200 and completed.json()["done"] is True
    assert client.delete(f"/api/tasks/{ident}").status_code == 204
    assert client.patch(f"/api/tasks/{ident}", json={"done": False}).status_code == 404


def test_validation_and_safe_sql(client):
    assert client.post("/api/tasks", json={"title":" ","due_date":"2026-01-01"}).status_code == 422
    assert client.post("/api/tasks", json={"title":"Tarefa","due_date":"31-12-2026"}).status_code == 422
    assert client.post("/api/tasks", json={"title":"Tarefa","category":"inexistente"}).status_code == 422
    malicious="Projeto'); DROP TABLE tasks; --"
    assert client.post("/api/tasks",json={"title": malicious}).status_code == 201
    assert any(row['title'] == malicious for row in client.get('/api/tasks').json())


def test_persistence_across_requests(client):
    before = client.get('/api/overview').json()
    first=client.get('/api/tasks').json()[0]
    client.patch(f"/api/tasks/{first['id']}",json={"done":True})
    after=client.get('/api/overview').json()
    assert after['done'] == before['done']+1
    assert after['total'] == before['total']
    assert any(row['id']==first['id'] and row['done'] for row in client.get('/api/tasks').json())
