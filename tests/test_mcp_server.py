import json
from types import SimpleNamespace

import pytest

from ollaborate_desk import app as desk
from ollaborate_desk import mcp_server as bridge


@pytest.fixture
def local_desk(tmp_path, monkeypatch):
    source = tmp_path / "documents"
    source.mkdir()
    (source / "plan.md").write_text("The local launch is planned for 2031.", encoding="utf-8")
    monkeypatch.setattr(desk, "SOURCE", source)
    monkeypatch.setattr(desk, "DATA", tmp_path / "data")
    desk.DATA.mkdir()
    yield


def test_search_uses_local_index_and_bounds_results(local_desk, monkeypatch):
    class FakeKnowledge:
        def ask(self, query):
            assert query == "launch"
            return SimpleNamespace(text="Evidence", warning=None, citations=[
                SimpleNamespace(location="plan.md", excerpt="Launch 2031", score=0.8)
            ])

    monkeypatch.setattr(desk, "knowledge", FakeKnowledge)
    result = bridge.search_files("launch")
    assert result["evidence"] == [{"path": "plan.md", "excerpt": "Launch 2031", "score": 0.8}]
    with pytest.raises(ValueError):
        bridge.search_files("  ")


def test_drafts_are_read_only_and_scoped(local_desk):
    with desk.connect() as conn:
        conn.execute("INSERT INTO tasks(created,instruction,output,evidence,status) VALUES(?,?,?,?,?)",
                     ("2031-01-01", "Summarize", "Draft text", json.dumps([{"path": "plan.md"}]), "draft"))
    assert bridge.list_drafts() == [{"id": 1, "created": "2031-01-01", "instruction": "Summarize", "status": "draft"}]
    assert bridge.get_draft(1)["output"] == "Draft text"
    assert bridge.get_draft(1)["evidence"] == [{"path": "plan.md"}]
    with pytest.raises(ValueError, match="Task not found"):
        bridge.get_draft(999)
    with pytest.raises(ValueError, match="limit"):
        bridge.list_drafts(51)


def test_mcp_tool_registration(local_desk):
    pytest.importorskip("mcp")
    import asyncio

    server = bridge.create_server()
    names = {tool.name for tool in asyncio.run(server.list_tools())}
    assert names == {"search_files", "list_drafts", "get_draft"}
