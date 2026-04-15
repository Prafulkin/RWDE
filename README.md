# Real-World Decision Engine (RWDE)

This is a decision intelligence engine powered by mathematical optimization (not just an LLM).
It uses Google OR-Tools to solve real-world problems under strict constraints, minimizing or maximizing an objective function rather than guessing heuristically.

## Architecture

* **Frontend:** Streamlit. Gives a fast, beautiful, reactive dashboard.
* **Backend Models:** Google OR-Tools (Mixed-Integer and Linear Programming formulations).
* **Python Engine:** `optimizer/` module handling model formulation (`SCIP` / `GLOP` solvers).

## Available Modules

1. **Diet Optimizer (MIP)**
   * **Goal:** Minimize Cost.
   * **Constraints:** Must stay under budget, hit macro thresholds, and enforce variety limits.
   * **Variables:** Integer serving sizes of mock foods.

2. **Weekly Time Planner (Continuous LP/Knapsack)**
   * **Goal:** Maximize subjective value (Value = Priority / required hours).
   * **Constraints:** Capped weekly hours bandwidth, minimum category hours, and strict completion flags.
   * **Variables:** Continuous hourly allocations per task.

## Running the Application Locally

1. Create a virtual environment (optional but recommended)
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit Application:
   ```bash
   streamlit run app.py
   ```
