# Simple WandB MCP Server

A minimal FastMCP server exposing tools for interacting with
[Weights & Biases](https://wandb.ai/).

## Tools

- `get_wandb_projects(entity: str)` – list projects for a W&B entity.
- `list_wandb_runs(entity: str, project_name: str)` – list runs in a project.
- `list_project_metrics(entity: str, project_name: str)` – show unique metric names
  across all runs in a project.
- `plot_run_metric(entity: str, project_name: str, run_id: str, metric_names: List[str])`
  – generate a plot of selected metrics for a run.

## Usage

Ensure the environment variable `WANDB_API_KEY` is set and run:

```bash
python server.py
```

## Development

Unit tests require access to a real W&B account. Set the following environment
variables before running `pytest`:

- `WANDB_API_KEY` or `TEST_WANDB_API_KEY`
- `TEST_WANDB_ENTITY` – the W&B entity to query
- `TEST_WANDB_PROJECT` – project name used for run/metric tests
- `TEST_WANDB_RUN_ID` – a run ID within the project
- `TEST_WANDB_METRICS` – comma separated metric names for the run

Run the test suite with:

```bash
pytest
```
