# 🪄 simple-wandb-mcp-server

<p align="center">
  <img src="logo.png" alt="simple-wandb-mcp-server logo" width="200"/>
</p>

A minimal, blazing-fast Model Context Protocol (MCP) server for Weights & Biases (W&B) projects.

---

## ✨ Features

- 🚀 Lightweight and easy to deploy
- 🔌 Simple HTTP API for querying W&B runs, metrics, and configs
- 📊 Fetch run details, metrics, and plots in seconds
- 🛠️ Built for integration with LLMs, dashboards, and automation
- 🐍 Pure Python, no heavy dependencies

---

## ⚙️ Setup

```bash
# Clone the repository
$ git clone https://github.com/yourusername/simple-wandb-mcp-server.git
$ cd simple-wandb-mcp-server

# (Optional) Create and activate a virtual environment
$ python -m venv venv
$ source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
$ pip install -r requirements.txt  # or pip install .
```

---

## 🚀 Usage

Start the server:

```bash
$ python server.py
```

The server will start on `http://localhost:8000` by default.

### Example API Calls

- **Get W&B run details:**
  - `GET /wandb/run?entity=<entity>&project_name=<project>&run_id=<run_id>`
- **List all runs in a project:**
  - `GET /wandb/runs?entity=<entity>&project_name=<project>`
- **List all metrics in a project:**
  - `GET /wandb/metrics?entity=<entity>&project_name=<project>`
- **Plot a metric for a run:**
  - `GET /wandb/plot?entity=<entity>&project_name=<project>&run_id=<run_id>&metric_names=<metric1,metric2>`

---

## 🧩 Integrations

- Works out-of-the-box with [Weights & Biases](https://wandb.ai/)
- Designed for easy extension and embedding in larger systems

---

## 📄 License

This project is licensed under the MIT License.

---

## About

A simple, production-ready MCP server for W&B. Perfect for LLM agents, dashboards, and automation scripts that need fast access to experiment metadata and metrics.

---

## Contributing

Pull requests and issues are welcome! Feel free to open an issue or submit a PR.

---

## Author

- [tsilva](https://github.com/tsilva)
