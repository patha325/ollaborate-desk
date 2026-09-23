import pytest

LibreIndex = pytest.importorskip("libreindex").LibreIndex


class LocalModel:
    def embed(self, texts, model):
        return [[1.0, 0.0] if "launch" in text.lower() else [0.0, 1.0] for text in texts]

    def generate(self, prompt, model):
        assert "SOURCE [1]" in prompt
        return "The launch is in 2031 [1]."


def test_real_embedded_index_and_reindex(tmp_path):
    source = tmp_path / "docs"
    source.mkdir()
    note = source / "plan.md"
    note.write_text("The launch is in 2031.", encoding="utf-8")
    index = LibreIndex(source, backend=LocalModel(), database=tmp_path / "index").index()
    answer = index.ask("When is the launch?")
    assert answer.citations[0].path == "plan.md"
    assert answer.citations[0].excerpt.startswith("The launch")
    assert answer.text.endswith("[1].")
    note.write_text("The launch is in 2032.", encoding="utf-8")
    index.index()
    assert "2032" in index.ask("When is the launch?").citations[0].excerpt
