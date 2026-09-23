import sys

from ollaborate_desk import app as module


def test_standalone_index_and_reindex(tmp_path, monkeypatch):
    source = tmp_path / "docs"
    source.mkdir()
    note = source / "plan.md"
    note.write_text("The launch is in 2031.", encoding="utf-8")
    monkeypatch.setitem(sys.modules, "libreindex", None)
    monkeypatch.setattr(module, "SOURCE", source)
    monkeypatch.setattr(module, "DATA", tmp_path / "data")
    knowledge = module.knowledge().index()
    assert knowledge.report.files == 1
    assert knowledge.ask("launch").citations[0].location == "plan.md"
    note.write_text("The launch is in 2032.", encoding="utf-8")
    knowledge.index()
    assert "2032" in knowledge.ask("launch").citations[0].excerpt
