# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Model Context Protocol (MCP) server that exposes Weights & Biases (W&B) functionality as tools. Built with FastMCP, it provides tools for querying W&B projects, runs, metrics, and generating metric plots.

## Development Commands

```bash
# Install dependencies (requires Python 3.13+)
uv sync

# Run the MCP server (stdio transport)
python server.py

# Run tests (requires W&B API key and test environment variables)
WANDB_API_KEY=<key> TEST_WANDB_ENTITY=<entity> TEST_WANDB_PROJECT=<project> TEST_WANDB_RUN_ID=<run_id> TEST_WANDB_METRICS=<metric1,metric2> pytest tests/
```

## Architecture

**Single-file server** (`server.py`): All MCP tools are defined in one file using the `@mcp.tool()` decorator from FastMCP.

**MCP Tools exposed:**
- `get_wandb_projects` - List projects for an entity
- `list_wandb_runs` - List runs in a project
- `list_project_metrics` - Get unique metric names across all runs
- `plot_run_metric` - Generate PNG plot of metrics (returns base64-encoded image via FastMCP `Image`)
- `get_run_details` - Get comprehensive run info (overview, config, summary, system metrics)

**Environment:** Requires `WANDB_API_KEY` environment variable (loaded via python-dotenv from `.env` file).

## Testing Notes

Tests in `tests/test_tools.py` stub out FastMCP and dotenv to test tool functions directly against the real W&B API. Tests are skipped if required environment variables are not set.

## Key Maintenance

README.md must be kept up to date with any significant project changes.
