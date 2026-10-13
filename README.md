# 🛡️ Veltra AI Agent Guardrail (veltra-agent)

A lightweight, developer-first AI Security & Guardrail Middleware API designed to protect autonomous LLM agents and AI apps from prompt injections, sensitive data leaks, and runaway malicious loops[cite: 2].

Developers drop a single line of Python/JS code into their AI apps, and Veltra instantly inspects, sanitizes, and blocks dangerous prompts, API key leaks, or excessive token usage before they reach the LLM[cite: 2].

## 🚀 Key Features

- **Prompt Injection Defense:** Instantly intercepts and blocks malicious jailbreak patterns and system overrides before they reach the model[cite: 2].
- **Real-Time PII & API Key Redactor:** Automatically masks leaked API keys (`sk-...`, `AIza...`), emails, and sensitive data on the fly[cite: 2].
- **Infinite Loop Circuit Breaker:** Hard-caps tool-calling iteration loops to prevent runaway credit exhaustion and unexpected cloud bills[cite: 2].
- **Token Budget Guard:** Enforces strict per-session token limits to protect developer resources.
- **Sub-60ms Latency:** Zero measurable overhead on agent workflows[cite: 10].

## 📦 Installation & Quickstart

```bash
pip install veltra-agent
