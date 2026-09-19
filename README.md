# Dual-Line Railway Track Access Optimiser (Lines Alpha & Beta)

Automated decision-support system designed for railway works controllers and track access schedulers to resolve nightly possession conflicts.

## Features
- **Topological Route Expansion:** Maps possessions through station platforms (`PLAT`) and tunnel sectors (`SEC`).
- **Safety Buffers & Coupling:** Handles 750V Live Rail mirroring, interchange crossover rules (`H01_H02`), and consist exclusion zones.
- **Multi-Scenario Policy Solver:** Supports Scenario A (Strict Supply), Scenario B (Strict Schedule), and Scenario C (Balanced Trade-Off).
- **100% Workload Baseline:** Fully schedules all activities without drops, adhering to precedence constraints.

## Project Structure
- `app.py`: Streamlit interactive web dashboard and visualization.
- `engine/topology.py`: Dual-line rail network topology and sector calculations.
- `engine/solver.py`: Heuristic constraint-satisfaction scheduling engine.
- `Dockerfile`: Production deployment configuration for Google Cloud Run.

## Local Setup
1. Clone the repository:
   ```bash
   git clone <REPO_URL>
   cd railway-access-optimiser
