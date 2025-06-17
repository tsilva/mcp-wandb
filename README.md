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
