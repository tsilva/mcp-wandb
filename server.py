import os
import tempfile
import matplotlib.pyplot as plt
import wandb
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import List

load_dotenv(override=True)

# Initialize FastMCP server
mcp = FastMCP("simple-wandb-mcp-server")

WANDB_API_KEY = os.getenv("WANDB_API_KEY")
assert WANDB_API_KEY, "WANDB_API_KEY must be set in the environment."
api = wandb.Api(api_key=WANDB_API_KEY)

@mcp.tool()
async def get_wandb_projects(entity: str) -> str:
    """Get a list of projects from Weights & Biases."""
    try:
        projects = api.projects(entity=entity)
        return "\n".join(f"- {p.name}" for p in projects) or f"No projects found for '{entity}'."
    except Exception as e:
        return f"Error fetching projects: {e}"

@mcp.tool()
async def list_wandb_runs(entity: str, project_name: str) -> str:
    """List all runs for a given W&B project."""
    if not project_name:
        return "Project name is required."

    try:
        runs = api.runs(path=f"{entity}/{project_name}")
        return "\n".join(f"- {r.name} (id: {r.id}, state: {r.state})" for r in runs) or f"No runs found in '{project_name}'."
    except Exception as e:
        return f"Error fetching runs for '{project_name}': {e}"

@mcp.tool()
async def list_project_metrics(entity: str, project_name: str) -> str:
    """List all unique metric names logged in a W&B project."""
    if not project_name:
        return "Project name is required."

    try:
        runs = api.runs(path=f"{entity}/{project_name}")
        metrics = set()
        for run in runs:
            # Run.history can return a DataFrame if pandas is installed, or a
            # list of dicts otherwise. Use pandas=False to ensure a consistent
            # list-of-dicts format so we can reliably extract metric names.
            history_rows = run.history(samples=1, pandas=False)
            if history_rows:
                metrics.update([k for k in history_rows[0].keys() if not k.startswith("_")])

        return "\n".join(sorted(metrics)) or f"No metrics found in '{project_name}'."
    except Exception as e:
        return f"Error fetching metrics for '{project_name}': {e}"

@mcp.tool()
async def plot_run_metric(entity: str, project_name: str, run_id: str, metric_names: List[str]) -> str:
    """
    Plot one or more metrics from a specific W&B run and return the image path.
    """

    if not project_name or not run_id or not metric_names:
        return "project_name, run_id, and metric_names are required."

    try:
        run = api.run(f"{entity}/{project_name}/{run_id}")
        history = run.history(keys=metric_names, pandas=True)

        if history.empty:
            return f"No metric data found in run '{run_id}'."

        available_metrics = [m for m in metric_names if m in history.columns]
        if not available_metrics:
            return f"None of the requested metrics found in run '{run_id}'."

        plt.figure(figsize=(10, 6))
        for metric in available_metrics:
            plt.plot(history[metric], label=metric)

        plt.title(f"Run: {run.name} - Metrics: {', '.join(available_metrics)}")
        plt.xlabel("Step")
        plt.ylabel("Value")
        plt.grid(True)
        plt.legend()

        temp_path = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
        plt.savefig(temp_path)
        plt.close()

        return temp_path

    except Exception as e:
        return f"Error plotting metrics from run '{run_id}': {e}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
