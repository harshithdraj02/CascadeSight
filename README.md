# ⚡ CascadeSight — Systemic Infrastructure Cascade Risk & Collapse Simulator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](https://www.python.org/)
[![Flask Server](https://img.shields.io/badge/Backend-Flask-000000.svg)](https://flask.palletsprojects.com/)
[![NetworkX](https://img.shields.io/badge/Graph_Engine-NetworkX-orange.svg)](https://networkx.org/)

**CascadeSight** is an interactive infrastructure resilience platform and systemic risk modeling engine. It predicts, visualizes, and quantifies cascading domino collapses across complex microservices, smart city digital infrastructure, and enterprise networks.

---

## 🎯 The Core Problem & Conceptual Framework

Modern digital infrastructures—from smart cities and cloud banking to massive global platforms—are complex directed dependency graphs. Traditional monitoring tools focus primarily on **Degree Centrality** (counting direct connections). However, this creates a dangerous blind spot:

> **Hidden Single Points of Failure (HSPOF)**: Low-degree nodes with few direct connections that underpin critical downstream paths. When an HSPOF fails, it triggers a catastrophic multi-stage cascade across the entire ecosystem.

CascadeSight solves this by applying **Discrete-Time Threshold Percolation Theory** and introducing a novel metric: the **Cascade Risk Score (CRS)**.

---

## 📐 Mathematical Formulation

### 1. Discrete-Time Threshold Propagation Model
For a directed graph $G = (V, E)$ where an edge $(u, v) \in E$ indicates that node $v$ **depends on** node $u$:

$$\text{Upstream}(v) = \{ u \in V \mid (u, v) \in E \}$$

At discrete timestep $t$, node $v$ transitions to state **FAILED** if the fraction of its failed upstream dependencies meets or exceeds the threshold $\theta$:

$$\frac{|\{ u \in \text{Upstream}(v) \mid \text{state}(u, t) = \text{FAILED} \}|}{|\text{Upstream}(v)|} \ge \theta$$

### 2. Cascade Risk Score (CRS)
To isolate non-obvious systemic hazards from high-degree hubs, the **Cascade Risk Score (CRS)** scales quadratically with blast radius while dividing by total structural connectivity:

$$\text{CRS}(v) = \frac{(\text{Blast Radius Percentage}(v))^2}{100 \times \max(\text{Total Degree}(v), 1)}$$

where $\text{Total Degree}(v) = \text{in\_degree}(v) + \text{out\_degree}(v)$.

* **Decoy Hubs** (High degree, moderate blast): Balanced score due to degree penalization.
* **Isolated Nodes** (Low degree, low blast): Low score due to quadratic blast scaling.
* **Hidden Single Points of Failure (HSPOF)** (Degree $\le 8$, Blast $\ge 50\%$): High CRS score (e.g., `Internal Config Service` scores **9.14** with **80.0%** blast).

---

## ✨ Features & Architecture

### 🏢 1. Smart City / Cloud Microservices Graph
* 20 interconnected digital infrastructure nodes (Config Services, API Gateways, Auth, User DB, Redis Cache, Background Workers, Monitoring Agents).
* Contains an architectural **Hidden Single Point of Failure**: `Internal Config Service` (Degree: 7, Blast: 80.0%, CRS: 9.14).

### 🌐 2. Meta (Facebook) October 4, 2021 Post-Mortem Modeling
* Explanatory dependency model reconstructed from Meta's engineering post-mortem of their historic 6-hour global outage.
* Demonstrates that formalizing the published failure chain identifies `Backbone BGP Router Config` as the #1 systemic risk node (100% blast radius).

### 📈 3. Non-Linear Tipping Point (Percolation Curve)
* Varies sensitivity threshold $\theta$ from $0.10$ to $0.90$.
* Plots the exact critical percolation threshold where system degradation shifts from linear tolerance to complete structural breakdown.

### 🎮 4. Interactive HTML5 Canvas Dashboard
* Live state rendering: **Healthy (Green)**, **At Risk (Yellow)**, **Failed (Red)**.
* Click-to-fail trigger selection, step-by-step playback animation, and dynamic threshold sliders.

### 🛡️ 5. Architectural Remediation & Circuit Breaker Engine
* Simulates enterprise resilience patterns (Circuit Breakers RFC-825, Stale-While-Revalidate Fallback Caching, and Async Queue Decoupling).
* Proves pre- vs post-mitigation risk reduction in real time, dropping systemic blast radius from 80%+ down to <15%.

### 📥 6. Dynamic Infrastructure Ingestion (Docker Compose & Cloud DAGs)
* Real-world manifest parser ingests `docker-compose.yml` and Kubernetes Service dependency topologies directly into directed graphs.
* Moves beyond hardcoded graphs into dynamic CI/CD pre-deployment architecture analysis.

### 📋 7. Enterprise SRE & DORA Compliance Audit Report
* Generates automated compliance reports mapped to **EU DORA Article 11** (ICT concentration risk) and **ISO 22301** (business continuity).
* One-click printable PDF audit export for enterprise architectural reviews.

---

## 🌐 Alignment with United Nations SDGs

* **SDG 9: Industry, Innovation & Infrastructure (Target 9.1 & 9.4)** — Enhances digital infrastructure reliability by identifying choke-points before deployment.
* **SDG 11: Sustainable Cities & Communities (Target 11.b)** — Safeguards smart city municipal SCADA, ambulance dispatch, and traffic grid operations from cascading failures.
* **SDG 16: Strong Institutions (Target 16.6)** — Ensures continuity in critical public administration and emergency communication pipelines.

---

## 🛠️ Installation & Usage

### 🚀 Quick Start (Windows)
Double-click the included `run.bat` script. It automatically installs dependencies and opens the web app in your browser:
```cmd
run.bat
```

### 🐍 Manual Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/CascadeSight.git
   cd CascadeSight
   ```
2. Install Python requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run CLI demo:
   ```bash
   python demo_cli.py
   ```
4. Start Web Application:
   ```bash
   python app.py
   ```
5. Open browser at: **`http://localhost:5000`**

---

## 📁 Repository Structure

```
CascadeSight/
├── app.py                     # Flask REST API & Web Dashboard Server
├── demo_cli.py                # Terminal CLI Demo & Mathematical Validation
├── run.bat                    # Zero-setup Windows Launcher
├── requirements.txt           # Python Package Dependencies
├── README.md                  # Project Documentation
├── presentation_guide.md      # Pitch Deck & Technical Storytelling Guide
├── core/
│   ├── graph_engine.py        # Directed Graph Engine & Post-Mortem Topologies
│   ├── cascade_model.py       # Discrete-Time Cascade Failure Simulator
│   ├── risk_scorer.py         # Cascade Risk Score (CRS) Engine
│   ├── tipping_point.py       # Percolation Tipping Point Analyzer
│   └── case_study.py          # Meta Oct 4, 2021 Case Study Validator
└── static/
    ├── index.html             # Dashboard User Interface
    ├── style.css              # Glassmorphism Dark Theme Stylesheet
    └── app.js                 # HTML5 Canvas Graph Visualizer & Controls
```

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for details.
