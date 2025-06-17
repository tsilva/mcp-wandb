import os
import matplotlib.pyplot as plt
import wandb
from mcp.server.fastmcp import FastMCP, Image
import io
from typing import List         

from dotenv import load_dotenv
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
async def plot_run_metric(
    entity: str,
    project_name: str,
    run_id: str,
    metric_names: List[str],
) -> str:                        # <-- return str, not bytes
    """
    Plot the requested metrics and return the **base-64-encoded PNG**.
    """

    if not (project_name and run_id and metric_names):
        return "project_name, run_id, and metric_names are required."

    try:
        import pandas as pd
    except ImportError:
        pd = None

    try:
        run = api.run(f"{entity}/{project_name}/{run_id}")

        # Always fetch list-of-dicts for predictable shape
        raw_history = run.history(keys=metric_names, pandas=False)
        if not raw_history:
            return f"No metric data found in run '{run_id}'."

        # Data-frame if possible, plain Python dict otherwise
        if pd:
            history = pd.DataFrame(raw_history)
        else:
            history = {k: [] for k in metric_names}
            for row in raw_history:
                for k in metric_names:
                    history[k].append(row.get(k))

        available_metrics = [
            m for m in metric_names
            if (m in history.columns if pd else any(history[m]))
        ]
        if not available_metrics:
            return f"None of the requested metrics found in run '{run_id}'."

        # ------- plotting -------
        plt.figure(figsize=(10, 6))
        for metric in available_metrics:
            y = history[metric] if pd else history[metric]
            plt.plot(y, label=metric)

        plt.title(f"Run: {run.name} – Metrics: {', '.join(available_metrics)}")
        plt.xlabel("Step")
        plt.ylabel("Value")
        plt.grid(True)
        plt.legend()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)

        # hand raw bytes to FastMCP – no manual b64 step
        return Image(data=buf.getvalue(), format="png")

    except Exception as e:
        return f"Error plotting metrics from run '{run_id}': {e}"

@mcp.tool()
async def get_run_details(entity: str, project_name: str, run_id: str) -> str:
    """
    Retrieve detailed information about a W&B run, including:
    - Overview (name, id, state, etc.)
    - Config (user-defined hyperparameters)
    - Summary (final logged metrics)
    - System/environment details
    """
    if not (project_name and run_id):
        return "Both project_name and run_id are required."

    try:
        run = api.run(f"{entity}/{project_name}/{run_id}")

        # Basic Overview
        overview = {
            "name": run.name,
            "id": run.id,
            "state": run.state,
            "created_at": str(run.created_at),
            "finished_at": str(run.finished_at),
            "duration (s)": run.duration,
            "tags": run.tags,
            "notes": run.notes,
            "url": run.url,
        }

        # Config
        config = dict(run.config)

        # Summary Metrics
        summary = dict(run.summary)

        # System Info (if available)
        system = {}
        try:
            system = dict(run.system_metrics)
        except Exception:
            system = {"info": "System metrics not available."}

        def format_dict(d: dict, title: str) -> str:
            if not d:
                return f"\n### {title}\n(No data)\n"
            lines = "\n".join(f"{k}: {v}" for k, v in d.items())
            return f"\n### {title}\n{lines}\n"

        # Combine all sections
        output = (
            format_dict(overview, "Overview") +
            format_dict(config, "Config") +
            format_dict(summary, "Summary") +
            format_dict(system, "System Info")
        )

        return output

    except Exception as e:
        return f"Error fetching run details for '{run_id}': {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
