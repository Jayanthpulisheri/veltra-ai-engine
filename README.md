# Veltra AI Agent Guardrail (`veltra-agent`)

> **Sub-60ms deterministic firewall, sandbox, and real-time audit exporter for autonomous AI agents.**

[![PyPI version](https://badge.fury.io/py/veltra-agent.svg)](https://badge.fury.io/py/veltra-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`veltra-agent` intercepts subprocess execution in real-time, enforcing non-bypassable runtime policies to prevent autonomous LLM agents (LangChain, AutoGen, CrewAI, OpenAI Tool Calls) from running destructive shell commands, accessing read-only root directories, exfiltrating data, or leaking API keys.

---

## Key Features

- **Sub-60ms Guardrail Latency**: Zero measurable overhead on agent workflows.
- **Async Output Streaming**: Line-by-line execution streaming via `asyncio` without standard buffer delays.
- **Dynamic Policy Hot-Reloading**: Update security rules in `veltra.config.json` on the fly without restarting agent processes.
- **Docker Sandbox Fallback**: Optional containerized execution for high-risk untrusted tool executions.
- **Enterprise SIEM Export**: Generate structured JSON security payloads ready for Datadog, Splunk, or AWS S3 ingestion.

---

## Quick Start

### Installation

```bash
pip install veltra-agent
