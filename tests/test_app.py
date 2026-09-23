from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from ollaborate_desk import app as module


@pytest.fixture
def client(tmp_path, monkeypatch):
    source = tmp_path / "documents"
    source.mkdir()
    (source / "plan.md").write_text("The launch is scheduled for 2031.", encoding="utf-8")
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setattr(module, "DATA", data)
    monkeypatch.setattr(module, "SOURCE", source)
    return TestClient(module.app)


def test_status_and_index_failure(client, monkeypatch):
    response = client.get("/api/status")
    assert response.status_code == 200
    assert response.json()["offline"] is True
    assert response.json()["source"].endswith("documents")
    def fails():
        raise RuntimeError("model unavailable")

    monkeypatch.setattr(module, "knowledge", fails)
    assert client.post("/api/index").status_code == 503


def test_index_result_and_task_review(client, monkeypatch):
    class FakeIndex:
        def index(self):
            self.report = SimpleNamespace(files=1, chunks=1, skipped=0)
            return self

        def ask(self, prompt):
            return SimpleNamespace(
                text="The launch is in 2031 [1].",
                citations=[SimpleNamespace(location="plan.md", excerpt="The launch is scheduled for 2031.", score=0.9)],
                warning=None,
            )

    class FakeTeam:
        def __init__(self, *args, **kwargs):
            pass

        async def pipeline(self, prompt):
            assert "launch" in prompt.lower()
            return SimpleNamespace(output="Draft: launch in 2031 [1].")

    monkeypatch.setattr(module, "knowledge", FakeIndex)
    monkeypatch.setattr("ollaborate.Team", FakeTeam)
    assert client.post("/api/index").json() == {"files": 1, "chunks": 1, "skipped": 0}
    result = client.post("/api/tasks", json={"instruction": "Summarize the launch"})
    assert result.status_code == 200, result.text
    task = result.json()
    assert task["evidence"][0]["path"] == "plan.md"
    assert client.get("/api/tasks").json()[0]["id"] == task["id"]
    assert not (module.DATA / "outputs").exists()
    saved = client.post("/api/save", json={"task_id": task["id"], "filename": "launch.md"})
    assert saved.status_code == 200
    assert (module.DATA / "outputs" / "launch.md").read_text() == task["output"]
    assert client.post("/api/save", json={"task_id": task["id"], "filename": "launch.md"}).status_code == 409
    assert client.post("/api/save", json={"task_id": task["id"], "filename": "../bad.md"}).status_code == 422


def test_missing_task_and_input_validation(client):
    assert client.post("/api/save", json={"task_id": 999, "filename": "missing.md"}).status_code == 404
    assert client.post("/api/tasks", json={"instruction": ""}).status_code == 422
