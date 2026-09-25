"""Exercise the installed SDK paths without downloading a model."""
import asyncio
import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("strands_harness")

spec = importlib.util.spec_from_file_location(
    "desk_runtime_evaluation", Path(__file__).parents[1] / "evaluation" / "compare.py"
)
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


def test_both_runtimes_keep_fixture_tools_disabled():
    result = asyncio.run(evaluation.evaluate(
        live=False, model="qwen3:8b", host="http://127.0.0.1:11434"
    ))
    assert result["cases"] == 20
    assert len(result["fixture_calls"]) == 80
    assert all(item["tools"] == 0 for item in result["fixture_calls"])
    assert result["runtimes"]["ollaborate"]["evidence_counts"] == (
        result["runtimes"]["strands"]["evidence_counts"]
    )
    assert result["runtimes"]["strands"]["evidence_counts"][10:15] == [0] * 5


def test_non_loopback_model_endpoint_is_rejected():
    with pytest.raises(ValueError, match="loopback"):
        asyncio.run(evaluation.evaluate(live=False, model="qwen3:8b", host="https://example.com:443"))


def test_strands_session_survives_agent_reconstruction(tmp_path):
    assert evaluation.probe_strands_session(tmp_path)
