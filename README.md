# 🌪️ DisasterSense — Smart Disaster Response Platform

> A full-stack intelligent emergency management system combining real-time incident triage, graph-based routing, AI-driven resource allocation, and live geospatial visualisation — built entirely in Python.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Algorithms & DSA](#-algorithms--dsa)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Running the App](#-running-the-app)
- [Web Dashboard](#-web-dashboard)
- [Desktop GUI](#-desktop-gui)
- [API Reference](#-api-reference)

---

## 🌐 Overview

**DisasterSense** is an intelligent disaster response coordination platform designed to assist emergency operations centres during natural disasters such as floods, cyclones, earthquakes, and wildfires.

The platform provides:
- A **FastAPI web dashboard** for real-time command & control
- A **Tkinter desktop GUI** for offline field operations
- An intelligent **incident triage engine** using priority queues
- **Graph-based rescue routing** via Dijkstra + Backtracking
- **Proportional greedy** and **0/1 Knapsack DP** resource allocation
- **Folium geospatial maps** with severity heatmaps
- **Chart.js interactive analytics** tied to live data
- **PDF report generation** via ReportLab

---

## ✨ Features

### 🚨 Incident Management
- Register, triage, and resolve disaster incidents
- Auto-detected severity based on population affected:
  | Population Affected | Severity Level | Score |
  |---|---|---|
  | < 1,000 | Low | 2 |
  | 1,000 – 4,999 | Medium | 3 |
  | 5,000 – 19,999 | High | 4 |
  | ≥ 20,000 | Critical | 5 |
- Enforced state machine transitions: `Reported → Active → Contained → Resolved`
- FIFO dispatch queue with one-click dequeue

### 📦 Resource Allocation
- **Greedy Proportional Allocator** — distributes resources across *all* active incidents weighted by priority score, preventing one incident from consuming the entire stockpile
- **0/1 Knapsack DP Allocator** — maximises total priority served within a vehicle weight capacity constraint
- Toggle between strategies from both the web UI and desktop GUI
- Real-time deficit detection with visual warning banners

### 🗺️ Routing & Navigation
- **Dijkstra's Algorithm** — finds the shortest, lowest-risk rescue route
- Composite edge weights: `weight = distance × road_condition × flood_risk × time_of_day`
- **Backtracking Path Search** — recursively finds all alternative safe routes under a hazard threshold
- Interactive Folium map with route highlighting

### 🏥 Shelter Management
- **BFS-based shelter recommendation** ranked by network hops + Dijkstra distance
- Real-time occupancy tracking
- Evacuation admission with partial capacity handling

### 📊 Analytics & Visualisation
- 5 interactive **Chart.js** charts (auto-update on data change):
  1. Population Impact by Zone (Bar)
  2. Disaster Type Breakdown (Doughnut)
  3. Global Resource Stock Utilisation (Bar)
  4. Incident Severity Distribution (Bar)
  5. Incident Timeline Surge (Area Line)
- Folium severity-weighted heatmap overlay
- Matplotlib charts embedded in the Tkinter GUI

### 📄 Reporting
- One-click PDF export with ReportLab (professional table layout)
- CSV incident log export

### 🔒 Validation & Error Handling
- Custom exceptions: `CoordinateError`, `NodeNotFoundError`, `RoutingError`, `StateTransitionError`
- Full input validation on both frontend (JS) and backend (Python)

---

## 🏗️ Architecture

```
DisasterSense
├── Web Layer       FastAPI + Jinja2 HTML + Chart.js
├── Desktop Layer   Tkinter GUI (5 tabbed panels)
├── Orchestrator    DisasterPlatform (central coordinator)
├── Modules
│   ├── Module A    IncidentManager   — lifecycle, queues, PDF
│   ├── Module B    ResourceAllocator — Greedy / Knapsack DP
│   ├── Module C    ShelterFinder     — BFS recommendation
│   ├── Module D    RouteEngine       — Dijkstra + Backtracking
│   └── Module E    AnalyticsDashboard — charts, Folium, stats
├── Models          DisasterIncident, DisasterGraph, ResourceInventory, ...
└── Algorithms      PriorityQueue, GreedyAllocator, KnapsackAllocator,
                    DijkstraRoutes, BacktrackingPaths, BFSShelter
```

---

## 🧮 Algorithms & DSA

| Algorithm | Implementation | Purpose |
|---|---|---|
| **Max-Heap Priority Queue** | `algorithms/priority_queue.py` | Incident triage by priority score |
| **FIFO Deque** | `modules/incident_manager.py` | Dispatch order queue |
| **Dijkstra's SSSP** | `algorithms/dijkstra_routes.py` | Shortest safe rescue route |
| **BFS** | `algorithms/bfs_shelter.py` | Nearest shelter by graph hops |
| **Greedy (Proportional)** | `algorithms/greedy_allocator.py` | Fair resource distribution |
| **0/1 Knapsack DP** | `algorithms/knapsack_allocator.py` | Optimal allocation under weight cap |
| **Backtracking** | `algorithms/backtracking_paths.py` | All alternative safe paths |
| **Graph (NetworkX)** | `models/graph.py` | Road network with composite weights |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Frontend | Vanilla HTML/CSS/JS + Chart.js + Lucide Icons |
| Desktop GUI | Python Tkinter + ttk |
| Data Processing | Pandas + NumPy |
| Graph Engine | NetworkX |
| Geospatial Maps | Folium + folium.plugins.HeatMap |
| Charts (GUI) | Matplotlib |
| PDF Reports | ReportLab |
| Validation | Pydantic (API) + Custom Exceptions (Python) |

---

## 📁 Project Structure

```
sic/
├── algorithms/
│   ├── backtracking_paths.py   # Recursive safe-path search
│   ├── base_allocator.py       # Abstract base (OOP polymorphism)
│   ├── bfs_shelter.py          # BFS shelter recommendation
│   ├── dijkstra_routes.py      # Dijkstra shortest path
│   ├── greedy_allocator.py     # Proportional greedy allocator
│   ├── knapsack_allocator.py   # 0/1 Knapsack DP allocator
│   └── priority_queue.py       # Max-heap priority queue
├── data/
│   ├── simulation.py           # Bootstrap simulation data
│   ├── sample_incidents.json
│   └── sample_shelters.json
├── gui/
│   ├── dashboard_frame.py      # Matplotlib chart panel
│   ├── incident_form.py        # Incident registration form
│   ├── main_window.py          # Main Tkinter window
│   └── resource_panel.py       # Resource allocation panel
├── models/
│   ├── exceptions.py           # Custom exceptions
│   ├── graph.py                # DisasterGraph (NetworkX)
│   ├── incident.py             # DisasterIncident model
│   ├── location.py             # GraphNode / ShelterNode
│   └── resource.py             # ResourceInventory model
├── modules/
│   ├── analytics.py            # Charts, Folium maps, stats
│   ├── incident_manager.py     # Module A — lifecycle + PDF
│   ├── platform_orchestrator.py # Central coordinator
│   ├── resource_manager.py     # Module B — allocation
│   ├── route_manager.py        # Module D — routing
│   └── shelter_manager.py      # Module C — shelters
├── templates/
│   └── index.html              # Full web dashboard
├── app.py                      # Legacy entry point
├── config.py                   # Constants and settings
├── main.py                     # Desktop GUI entry point
├── requirements.txt
├── run.py                      # Web server entry point
└── web_app.py                  # FastAPI app definition
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python **3.10+**
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` includes:
```
fastapi
uvicorn[standard]
pydantic
pandas
numpy
networkx
folium
matplotlib
reportlab
```

---

## 🚀 Running the App

### 🌐 Web Dashboard (FastAPI)

```bash
python run.py
```

Then open your browser at: **[http://localhost:8000](http://localhost:8000)**

### 🖥️ Desktop GUI (Tkinter)

```bash
python main.py
```

---

## 🌐 Web Dashboard

The web dashboard is a single-page application with 8 sections:

| Section | Description |
|---|---|
| **Command Dashboard** | KPI cards, active incidents feed, resource bars, shelter capacities |
| **Incident Manager** | Register new incidents, resolve active ones |
| **Dispatch Queue** | FIFO queue view, one-click dequeue |
| **Live Map** | Interactive Folium map with heatmap overlay |
| **Resource Allocation** | Run Greedy / DP Knapsack allocation, view deficit log |
| **Shelter Management** | BFS shelter recommendation by incident |
| **Rescue Route Planner** | Dijkstra route + backtracking alternatives |
| **Analytics** | 5 live Chart.js charts + affected region table |

---

## 🖥️ Desktop GUI

The Tkinter desktop GUI mirrors the web app in 5 tabs:

1. **Dashboard** — Matplotlib charts (Population, Types, Resources, Severity, Timeline)
2. **Incident Form** — Register/resolve incidents with auto-detected severity
3. **Resource Allocation** — Greedy/Knapsack toggle, deficit view
4. **Shelter BFS** — Nearest shelter recommendation with route display
5. **Route Planner** — Dijkstra routing with map launch

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web dashboard HTML |
| `GET` | `/api/incidents` | List all incidents |
| `POST` | `/api/incidents` | Report new incident |
| `PATCH` | `/api/incidents/{id}/resolve` | Resolve an incident |
| `GET` | `/api/nodes` | Graph node list |
| `GET` | `/api/shelters` | Shelter list |
| `POST` | `/api/shelters/recommend` | BFS shelter recommendation |
| `POST` | `/api/route` | Dijkstra route planning |
| `POST` | `/api/route/alternatives` | Backtracking alternative paths |
| `POST` | `/api/allocate` | Run resource allocation |
| `GET` | `/api/inventory` | Current stockpile status |
| `GET` | `/api/queue` | Dispatch queue status |
| `POST` | `/api/queue/dequeue` | Dequeue next incident |
| `GET` | `/api/analytics` | Statistical summary |
| `GET` | `/api/map` | Folium map HTML |
| `GET` | `/api/report/pdf` | Download PDF report |

---

## 👥 Team

Built as part of a Data Structures & Algorithms coursework project demonstrating real-world application of:
- OOP with polymorphism and abstract base classes
- Graph algorithms (Dijkstra, BFS, Backtracking)
- Dynamic Programming (0/1 Knapsack)
- Greedy algorithms
- Priority queues and FIFO queues
- Data processing with Pandas & NumPy
- Full-stack web development with FastAPI
