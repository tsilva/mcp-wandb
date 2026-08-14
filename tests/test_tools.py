import asyncio
import importlib
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def server(monkeypatch):
    monkeypatch.delenv("WANDB_API_KEY", raising=False)
    sys.modules.pop("server", None)
    module = importlib.import_module("server")
    module._api = MagicMock()
    return module


def test_mcp_tools_are_registered_with_the_real_sdk(server):
    tools = asyncio.run(server.mcp.list_tools())

    assert {tool.name for tool in tools} == {
        "get_wandb_projects",
        "list_project_metrics",
        "list_wandb_runs",
        "plot_run_metric",
        "get_run_details",
    }


def test_discovery_does_not_require_credentials(monkeypatch):
    monkeypatch.delenv("WANDB_API_KEY", raising=False)
    sys.modules.pop("server", None)

    module = importlib.import_module("server")

    assert module._api is None
    assert "WANDB_API_KEY" in asyncio.run(module.get_wandb_projects("example"))


def test_get_wandb_projects_formats_names(server):
    server._api.projects.return_value = [SimpleNamespace(name="one"), SimpleNamespace(name="two")]

    result = asyncio.run(server.get_wandb_projects("entity"))

    assert result == "- one\n- two"
    server._api.projects.assert_called_once_with(entity="entity")


def test_list_wandb_runs_rejects_a_missing_project_without_an_api_call(server):
    result = asyncio.run(server.list_wandb_runs("entity", ""))

    assert result == "Project name is required."
    server._api.runs.assert_not_called()


def test_list_wandb_runs_formats_run_metadata(server):
    server._api.runs.return_value = [SimpleNamespace(name="train", id="run-1", state="finished")]

    result = asyncio.run(server.list_wandb_runs("entity", "project"))

    assert result == "- train (id: run-1, state: finished)"


def test_list_project_metrics_excludes_private_fields(server):
    run = MagicMock()
    run.history.return_value = [{"accuracy": 0.9, "loss": 0.1, "_step": 1}]
    server._api.runs.return_value = [run]

    result = asyncio.run(server.list_project_metrics("entity", "project"))

    assert result == "accuracy\nloss"
    run.history.assert_called_once_with(samples=1, pandas=False)


def test_plot_run_metric_returns_a_png_image(server):
    run = MagicMock(name="run")
    run.name = "training"
    run.history.return_value = [{"loss": 1.0}, {"loss": 0.5}]
    server._api.run.return_value = run

    result = asyncio.run(server.plot_run_metric("entity", "project", "run-1", ["loss"]))

    assert isinstance(result, server.Image)
    assert result.data.startswith(b"\x89PNG\r\n\x1a\n")
    assert result.to_image_content().mimeType == "image/png"
    run.history.assert_called_once_with(keys=["loss"], pandas=False)


def test_get_run_details_formats_expected_sections(server):
    run = SimpleNamespace(
        name="training",
        id="run-1",
        state="finished",
        created_at="2026-01-01",
        finished_at="2026-01-02",
        duration=10,
        tags=["test"],
        notes="offline fixture",
        url="https://example.invalid/run-1",
        config={"epochs": 2},
        summary={"accuracy": 0.9},
        system_metrics={"cpu": 1},
    )
    server._api.run.return_value = run

    result = asyncio.run(server.get_run_details("entity", "project", "run-1"))

    assert "### Overview" in result
    assert "### Config" in result
    assert "epochs: 2" in result
    assert "accuracy: 0.9" in result


def test_api_errors_are_returned_without_leaking_control_flow(server):
    server._api.projects.side_effect = RuntimeError("rejected fixture")

    result = asyncio.run(server.get_wandb_projects("../../unexpected"))

    assert result == "Error fetching projects: rejected fixture"
