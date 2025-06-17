import asyncio
import importlib
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest
import wandb

# Ensure repository root is on the import path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Stub out FastMCP and dotenv so server imports without the full MCP env
class FakeFastMCP:
    def __init__(self, name):
        self.name = name

    def tool(self):
        def decorator(fn):
            return fn
        return decorator

    def run(self, *args, **kwargs):
        pass

fake_fastmcp_module = ModuleType("mcp.server.fastmcp")
fake_fastmcp_module.FastMCP = FakeFastMCP
fake_server_module = ModuleType("mcp.server")
fake_server_module.fastmcp = fake_fastmcp_module
fake_mcp_module = ModuleType("mcp")
fake_mcp_module.server = fake_server_module
sys.modules.setdefault("mcp", fake_mcp_module)
sys.modules.setdefault("mcp.server", fake_server_module)
sys.modules.setdefault("mcp.server.fastmcp", fake_fastmcp_module)

fake_dotenv = ModuleType("dotenv")
fake_dotenv.load_dotenv = lambda *args, **kwargs: None
sys.modules.setdefault("dotenv", fake_dotenv)


def load_server():
    api_key = os.getenv("WANDB_API_KEY") or os.getenv("TEST_WANDB_API_KEY")
    if not api_key:
        pytest.skip("WANDB_API_KEY not provided")
    os.environ.setdefault("WANDB_API_KEY", api_key)
    return importlib.import_module("server")


@pytest.mark.skipif(not (os.getenv("WANDB_API_KEY") or os.getenv("TEST_WANDB_API_KEY")), reason="WANDB_API_KEY not set")
def test_get_wandb_projects_matches_api():
    server = load_server()
    entity = os.getenv("TEST_WANDB_ENTITY")
    if not entity:
        pytest.skip("TEST_WANDB_ENTITY not set")
    expected = [p.name for p in server.api.projects(entity=entity)]
    result = asyncio.run(server.get_wandb_projects(entity))
    result_names = [line[2:] for line in result.splitlines() if line.startswith("- ")]
    assert result_names == expected


@pytest.mark.skipif(not (os.getenv("WANDB_API_KEY") or os.getenv("TEST_WANDB_API_KEY")), reason="WANDB_API_KEY not set")
def test_list_wandb_runs_matches_api():
    server = load_server()
    entity = os.getenv("TEST_WANDB_ENTITY")
    project = os.getenv("TEST_WANDB_PROJECT")
    if not entity or not project:
        pytest.skip("TEST_WANDB_ENTITY or TEST_WANDB_PROJECT not set")
    expected = [f"- {r.name} (id: {r.id}, state: {r.state})" for r in server.api.runs(path=f"{entity}/{project}")]
    result = asyncio.run(server.list_wandb_runs(entity, project))
    result_lines = result.splitlines()
    assert result_lines == expected


@pytest.mark.skipif(not (os.getenv("WANDB_API_KEY") or os.getenv("TEST_WANDB_API_KEY")), reason="WANDB_API_KEY not set")
def test_list_project_metrics_matches_api():
    server = load_server()
    entity = os.getenv("TEST_WANDB_ENTITY")
    project = os.getenv("TEST_WANDB_PROJECT")
    if not entity or not project:
        pytest.skip("TEST_WANDB_ENTITY or TEST_WANDB_PROJECT not set")

    runs = server.api.runs(path=f"{entity}/{project}")
    metrics = set()
    for run in runs:
        history_rows = run.history(samples=1, pandas=False)
        if history_rows:
            metrics.update([k for k in history_rows[0].keys() if not k.startswith("_")])
    expected = sorted(metrics)

    result = asyncio.run(server.list_project_metrics(entity, project))
    result_metrics = sorted([m for m in result.splitlines() if m])
    assert result_metrics == expected


@pytest.mark.skipif(not (os.getenv("WANDB_API_KEY") or os.getenv("TEST_WANDB_API_KEY")), reason="WANDB_API_KEY not set")
def test_plot_run_metric_creates_file(tmp_path):
    server = load_server()
    entity = os.getenv("TEST_WANDB_ENTITY")
    project = os.getenv("TEST_WANDB_PROJECT")
    run_id = os.getenv("TEST_WANDB_RUN_ID")
    metric_names = os.getenv("TEST_WANDB_METRICS")
    if not all([entity, project, run_id, metric_names]):
        pytest.skip("Required wandb details not set")

    metric_list = [m.strip() for m in metric_names.split(",")]
    path = asyncio.run(server.plot_run_metric(entity, project, run_id, metric_list))
    assert os.path.isfile(path)
    assert os.path.getsize(path) > 0
    os.remove(path)
