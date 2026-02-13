<div align="center">
  <img src="logo.png" alt="simple-wandb-mcp-server" width="512"/>

  # simple-wandb-mcp-server

  [![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

  **🔬 Query your Weights & Biases experiments directly from LLM agents via Model Context Protocol 📊**

  [W&B Documentation](https://docs.wandb.ai/) · [MCP Specification](https://modelcontextprotocol.io/)
</div>

---

## Overview

A Model Context Protocol (MCP) server that exposes Weights & Biases functionality as tools. Built with FastMCP, it enables LLM agents to query W&B projects, list runs, retrieve metrics, and generate metric plots—all through a simple stdio interface.

## Features

- **List projects** — Get all W&B projects for an entity
- **Browse runs** — List runs with name, ID, and state
- **Discover metrics** — Find unique metric names across all runs in a project
- **Plot metrics** — Generate PNG visualizations of run metrics (returned as base64)
- **Run details** — Retrieve comprehensive run info including config, summary, and system metrics

## Quick Start

```bash
# Install with uv
uv add simple-wandb-mcp-server

# Or clone and install
git clone https://github.com/tsilva/simple-wandb-mcp-server.git
cd simple-wandb-mcp-server
uv sync
```

Set your W&B API key:

```bash
export WANDB_API_KEY=your_api_key
# Or create a .env file
echo "WANDB_API_KEY=your_api_key" > .env
```

Run the server:

```bash
python server.py
```

## MCP Client Configuration

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "wandb": {
      "command": "python",
      "args": ["/path/to/simple-wandb-mcp-server/server.py"],
      "env": {
        "WANDB_API_KEY": "your_api_key"
      }
    }
  }
}
```

## Available Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `get_wandb_projects` | `entity` | List all projects for a W&B entity |
| `list_wandb_runs` | `entity`, `project_name` | List all runs in a project |
| `list_project_metrics` | `entity`, `project_name` | Get unique metric names across all runs |
| `plot_run_metric` | `entity`, `project_name`, `run_id`, `metric_names` | Generate a PNG plot of specified metrics |
| `get_run_details` | `entity`, `project_name`, `run_id` | Get detailed run info (overview, config, summary, system metrics) |

## Example Usage

Once connected to an MCP client, you can ask questions like:

- *"List all my W&B projects"*
- *"Show me the runs in my training-experiments project"*
- *"What metrics are being logged in this project?"*
- *"Plot the loss and accuracy for run abc123"*
- *"Give me the details of my latest run"*

## Development

```bash
# Install dependencies
uv sync

# Run tests (requires W&B credentials)
WANDB_API_KEY=<key> \
TEST_WANDB_ENTITY=<entity> \
TEST_WANDB_PROJECT=<project> \
TEST_WANDB_RUN_ID=<run_id> \
TEST_WANDB_METRICS=<metric1,metric2> \
pytest tests/
```

## Requirements

- Python 3.13+
- W&B account and API key

## License

MIT

## Author

[tsilva](https://github.com/tsilva)
