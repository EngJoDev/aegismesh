<div align="center">

```
    ___    ______ _____ ____ ____   __  ___ _____ _____ __  __
   /   |  / ____// ___//  _// ___/ /  |/  // ___// ___// / / /
  / /| | / __/  / / __ / /  \__ \ / /|_/ // __/  \__ \/ /_/ / 
 / ___ |/ /___ / /_/ // /  ___/ // /  / // /___ ___/ // __  /  
/_/  |_/_____/ \____/___/ /____//_/  /_//_____//____//_/ /_/   
```

# ⚡ AegisMesh
### Ultra-Fast Distributed AI Security Gateway, Semantic Cache & Anti-DDoS Threat Shield

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Security: WAF & AI Shield](https://img.shields.io/badge/Security-WAF%20%2B%20PromptGuard-brightgreen.svg)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)

*Protect LLMs, microservices, and backend APIs against DDoS surges, SQLi/XSS exploits, and Prompt Injections—with sub-millisecond semantic caching.*

[Quickstart](#-quickstart) • [Features](#-key-features) • [Architecture](#-architecture) • [SOC Dashboard](#-real-time-soc-dashboard) • [Testing](#-testing)

---

</div>

## 💥 The Problem
Modern web applications and AI APIs face three critical operational threats:
1. **Financial Exhaustion (Token Bankruptcy):** Repetitive API queries to OpenAI, Anthropic, or Gemini cost thousands of dollars per month with high latency.
2. **AI Jailbreaks & Prompt Injection:** Malicious actors trick LLMs into leaking system instructions, credentials, and private customer databases.
3. **DDoS & Scraping Floods:** Unthrottled traffic crashes microservices and exceeds rate limits.

**AegisMesh** is a next-generation high-concurrency reverse proxy and security gateway that sits in front of your upstream APIs, neutralizing threats before they reach your infrastructure.

---

## 🚀 Key Features

* **🛡️ AI Prompt-Injection Guard:** Intercepts jailbreaks, "DAN modes", and instruction overrides in real time.
* **🔒 Automatic PII Masking:** Detects and redacts credit cards, emails, SSNs, and leaked API tokens on the fly.
* **⚡ High-Throughput Token Bucket Limiter:** Thread-safe in-memory rate limiting preventing API abuse and DDoS floods.
* **💾 Semantic In-Memory Caching:** Hashes and caches responses, returning identical or repeated requests in `< 5ms` with zero upstream cost.
* **📊 Cyberpunk SOC Dashboard:** Live Web UI streaming telemetry, blocked attacks, latency, and threat origins.

---

## 📦 Quickstart

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/EngJoDev/aegismesh.git
cd aegismesh

# Run with quick launcher
./run.sh --version
```

### 2. Start the Security Gateway

```bash
# Start proxy on port 8088 protecting your upstream backend
./run.sh start --port 8088 --upstream https://httpbin.org
```

### 3. Open the Security Dashboard
Visit the live dashboard in your browser:
👉 **`http://localhost:8088/_aegis/dashboard`**

---

## 🏛 Architecture

```mermaid
flowchart TD
    Client["Inbound Client Requests\n(Web, Mobile, Agents)"]
    
    subgraph AegisMesh["AegisMesh Security Gateway"]
        Limiter["Anti-DDoS TokenBucket Limiter"]
        WAF["WAF & AI Injection Shield"]
        PII["PII Redaction Engine"]
        Cache{"Semantic Cache Hit?"}
    end
    
    Upstream["Protected Upstream API / LLM\n(OpenAI, FastAPI, Microservices)"]
    SOC["Live Web SOC Dashboard\n(Real-time Telemetry)"]

    Client --> Limiter
    Limiter -->|Allow| WAF
    Limiter -->|Exceed| Reject429["429 Rate Limit Block"]
    
    WAF -->|Threat Detected| Block403["403 Threat Neutralized"]
    WAF -->|Clean| PII
    
    PII --> Cache
    Cache -->|YES (Hit)| ReturnCached["Sub-5ms Zero Cost Response"]
    Cache -->|NO (Miss)| Upstream
    
    AegisMesh -.->|Stream Metrics| SOC
```

---

## 🧪 Testing

Run the automated test suite:
```bash
./.venv/bin/python -m unittest discover tests
```

---

## 🤝 Contributing
Contributions are warmly welcomed! Please check out [CONTRIBUTING.md](CONTRIBUTING.md) to get started.

## 📄 License
This project is licensed under the [MIT License](LICENSE).
