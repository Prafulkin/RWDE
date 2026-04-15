from ortools.linear_solver import pywraplp

# Simulated task backlog
TASK_DB = [
    {"name": "Client Project Work", "hours_req": 15, "priority": 10, "type": "Work"},
    {"name": "Write Blog Post", "hours_req": 4, "priority": 5, "type": "Marketing"},
    {"name": "Team Standups", "hours_req": 3, "priority": 8, "type": "Work"},
    {"name": "Admin/Emails", "hours_req": 5, "priority": 4, "type": "Admin"},
    {"name": "Learn New Tech", "hours_req": 8, "priority": 7, "type": "Growth"},
    {"name": "Networking Event", "hours_req": 4, "priority": 6, "type": "Growth"},
    {"name": "Gym & Health", "hours_req": 7, "priority": 9, "type": "Personal"},
    {"name": "Side Hustle Coding", "hours_req": 10, "priority": 6, "type": "Project"},
    {"name": "Family Dinner Time", "hours_req": 12, "priority": 10, "type": "Personal"},
    {"name": "Read Book", "hours_req": 5, "priority": 5, "type": "Personal"}
]

def optimize_time(total_hours: float, min_personal_hours: float, must_do_strict: bool):
    """
    Optimizes a weekly time schedule to maximize value (priority) 
    given a strict limit on total hours.
    Allows partial task completion (Continuous LP problem).
    """
    # Create LP solver
    solver = pywraplp.Solver.CreateSolver('GLOP')
    if not solver:
        return {"status": "ERROR", "message": "Solver not found"}

    # Variables: Hours allocated to each task. Continuous variable from 0 to hours_req
    task_vars = {}
    for task in TASK_DB:
        task_vars[task['name']] = solver.NumVar(0, task['hours_req'], task['name'])

    # Constraints
    # 1. Total hours allocated <= Total available
    solver.Add(
        sum(task_vars[task['name']] for task in TASK_DB) <= total_hours,
        "Total Weekly Hours Limit"
    )

    # 2. Minimum Personal Hours Check
    personal_vars = [task_vars[task['name']] for task in TASK_DB if task['type'] == 'Personal']
    if personal_vars:
        solver.Add(
            sum(personal_vars) >= min_personal_hours,
            "Minimum Personal Hours Constraint"
        )
        
    # 3. Must-Do Strict constraint (forces priority 10 tasks to be fully complete)
    if must_do_strict:
        for task in TASK_DB:
            if task['priority'] == 10:
                solver.Add(task_vars[task['name']] == task['hours_req'], f"Strict Completion: {task['name']}")

    # Objective: Maximize total priority weight relative to time spent
    # We want to favor spending time on high priority tasks.
    objective = solver.Objective()
    for task in TASK_DB:
        # Value added = Priority * (Hours allocated / Required Hours)
        # So coefficient is Priority / Required Hours.
        # This makes high priority, low duration tasks extremely valuable.
        coef = task['priority'] / task['hours_req'] 
        objective.SetCoefficient(task_vars[task['name']], coef)
    
    objective.SetMaximization()

    # Solve
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        plan = []
        total_allocated = 0
        total_value = 0
        
        for task in TASK_DB:
            allocated = task_vars[task['name']].solution_value()
            if allocated > 0.1:  # ignore tiny floating point remainders
                total_allocated += allocated
                # Calculate what % of the task is getting done
                completion_pct = (allocated / task['hours_req']) * 100
                total_value += task['priority'] * (allocated / task['hours_req'])
                
                plan.append({
                    "Task": task['name'],
                    "Type": task['type'],
                    "Allocated (hrs)": round(allocated, 1),
                    "Required (hrs)": task['hours_req'],
                    "Completion %": f"{round(completion_pct)}%",
                    "Priority": task['priority']
                })
        
        # Determine dropped or reduced tasks for explanation
        dropped = []
        reduced = []
        full = []
        for task in TASK_DB:
            allocated = task_vars[task['name']].solution_value()
            if allocated < 0.1:
                dropped.append(task['name'])
            elif allocated < task['hours_req'] - 0.1:
                reduced.append(task['name'])
            else:
                full.append(task['name'])
                
        explanation = "The solver structured your week by prioritizing highest return-on-time tasks.\n\n"
        if dropped:
            explanation += f"**Sacrificed Completely Strategy:** {', '.join(dropped)} were dropped completely due to constraints. "
        if reduced:
            explanation += f"**Compromise Strategy:** Hours were reduced for {', '.join(reduced)} to squeeze maximum value within the {total_hours} hr limit."

        return {
            "status": "OPTIMAL",
            "plan": sorted(plan, key=lambda x: x['Allocated (hrs)'], reverse=True),
            "metrics": {
                "Hours Scheduled": round(total_allocated, 1),
                "Capacity Utilized %": round((total_allocated / total_hours) * 100, 1) if total_hours > 0 else 0,
                "Total Subjective Value": round(total_value, 1)
            },
            "explanation": explanation
        }
    else:
        return {
            "status": "INFEASIBLE",
            "message": "Infeasible. Your strict constraints (like minimum personal hours or strict priority 10 completions) exceed your total available hours.",
            "plan": [],
            "metrics": None
        }
