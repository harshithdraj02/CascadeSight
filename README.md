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
To isolate non-obvious systemic hazards from high-degree hubs, the **Cascade Risk Score (CRS)** scales quadratically with blast radius while penalizing raw degree centrality:

$$\text{CRS}(v) = \frac{(\text{Blast Radius Percentage}(v))^2}{100 \times \max(\text{Degree}(v), 1)}$$

* **High Hubs** (High degree, moderate blast): Balanced score.
* **Isolated Nodes** (Low degree, low blast): Low score.
* **Hidden Single Points of Failure** (Low degree, 50%+ blast): **Extremely high CRS score**.

---

## ✨ Features & Architecture

### 🏢 1. Smart City / Cloud Microservices Graph
* 20 interconnected digital infrastructure nodes (Config Services, API Gateways, Auth, User DB, Redis Cache, Background Workers, Monitoring Agents).
* Designed with an intentional **Hidden Single Point of Failure**: `Internal Config Service`.

### 🌐 2. Meta (Facebook) October 4, 2021 Post-Mortem Validation
* Topology reconstructed directly from Meta's engineering post-mortem of their historic 6-hour global outage.
* Validates that `Backbone BGP Router Config` scores as the **#1 systemic danger node** (100% historical match).

### 📈 3. Non-Linear Tipping Point (Percolation Curve)
* Varies sensitivity threshold $\theta$ from $0.10$ to $0.90$.
* Plots the exact critical percolation threshold where system degradation shifts from linear tolerance to complete structural breakdown.

### 🎮 4. Interactive HTML5 Canvas Dashboard
* Live state rendering: **Healthy (Green)**, **At Risk (Yellow)**, **Failed (Red)**.
* Click-to-fail trigger selection, step-by-step playback animation, and dynamic threshold sliders.

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
