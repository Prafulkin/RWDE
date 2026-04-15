from ortools.linear_solver import pywraplp

# Simulated database of foods
FOOD_DB = [
    {"name": "Oats (50g)", "cost": 15, "protein": 6, "calories": 150, "max_servings": 4},
    {"name": "Eggs (2)", "cost": 14, "protein": 12, "calories": 140, "max_servings": 5},
    {"name": "Chicken Breast (100g)", "cost": 30, "protein": 31, "calories": 165, "max_servings": 4},
    {"name": "Lentils (1 cup cooked)", "cost": 18, "protein": 18, "calories": 230, "max_servings": 3},
    {"name": "Rice (1 cup)", "cost": 10, "protein": 4, "calories": 205, "max_servings": 4},
    {"name": "Milk (1 glass)", "cost": 15, "protein": 8, "calories": 150, "max_servings": 3},
    {"name": "Peanut Butter (2 tbsp)", "cost": 20, "protein": 8, "calories": 190, "max_servings": 2},
    {"name": "Banana", "cost": 5, "protein": 1, "calories": 105, "max_servings": 4},
    {"name": "Paneer (100g)", "cost": 35, "protein": 18, "calories": 265, "max_servings": 3},
    {"name": "Soy Chunks (50g)", "cost": 12, "protein": 26, "calories": 170, "max_servings": 2},
    {"name": "Almonds (30g)", "cost": 40, "protein": 6, "calories": 164, "max_servings": 2},
    {"name": "Spinach (1 bunch)", "cost": 20, "protein": 3, "calories": 23, "max_servings": 2},
]

def optimize_diet(budget: float, min_protein: float, min_calories: float, max_calories: float, min_meals: int):
    """
    Optimizes finding a daily diet that minimizes cost while hitting macro targets.
    Returns optimal food selection, constraints analysis, and metrics.
    """
    # Create the linear solver with the SCIP backend (Handles Mixed-Integer Programming)
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return {"status": "ERROR", "message": "Solver not found"}

    # Variables: Number of servings for each food item (integer)
    food_vars = {}
    for food in FOOD_DB:
        # Cannot have negative servings, and limit by max_servings to ensure variety
        food_vars[food['name']] = solver.IntVar(0, food['max_servings'], food['name'])

    # Constraints
    # 1. Total Cost <= Budget
    solver.Add(
        sum(food_vars[food['name']] * food['cost'] for food in FOOD_DB) <= budget, 
        "Budget Constraint"
    )

    # 2. Total Protein >= Min Protein
    solver.Add(
        sum(food_vars[food['name']] * food['protein'] for food in FOOD_DB) >= min_protein,
        "Protein Target Constraint"
    )

    # 3. Total Calories >= Min Calories
    solver.Add(
        sum(food_vars[food['name']] * food['calories'] for food in FOOD_DB) >= min_calories,
        "Min Calories Constraint"
    )

    # 4. Total Calories <= Max Calories
    solver.Add(
        sum(food_vars[food['name']] * food['calories'] for food in FOOD_DB) <= max_calories,
        "Max Calories Constraint"
    )

    # 5. Minimum total servings to somewhat approximate meals
    # Assuming standard meal ~2 servings of things. 
    solver.Add(
        sum(food_vars[food['name']] for food in FOOD_DB) >= min_meals * 2,
        "Min Meals constraint"
    )

    # Objective: Minimize Total Cost
    objective = solver.Objective()
    for food in FOOD_DB:
        objective.SetCoefficient(food_vars[food['name']], food['cost'])
    objective.SetMinimization()

    # Solve
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        plan = []
        total_cost = 0
        total_protein = 0
        total_cal = 0
        
        for food in FOOD_DB:
            var = food_vars[food['name']]
            servings = int(var.solution_value())
            if servings > 0:
                cost = servings * food['cost']
                protein = servings * food['protein']
                cal = servings * food['calories']
                
                total_cost += cost
                total_protein += protein
                total_cal += cal
                
                plan.append({
                    "Food": food['name'],
                    "Servings": servings,
                    "Cost (₹)": cost,
                    "Protein (g)": protein,
                    "Calories": cal
                })
                
        # Generate Explanation
        explanation = (
            f"The solver found an OPTIMAL combination for ₹{total_cost} "
            f"(target was ₹{budget}), saving you ₹{int(budget - total_cost)} while meeting all nutritional requirements. "
            f"It prioritized high-protein, low-cost ingredients like "
        )
        # Find the most cost-efficient protein source from the plan
        if plan:
            best_protein_src = max(plan, key=lambda x: x["Protein (g)"] / max(x["Cost (₹)"], 1))
            explanation += f"**{best_protein_src['Food']}** to satisfy the protein constraint efficiently."

        return {
            "status": "OPTIMAL",
            "plan": plan,
            "metrics": {
                "Total Cost (₹)": total_cost,
                "Total Protein (g)": total_protein,
                "Total Calories": total_cal
            },
            "explanation": explanation
        }
    else:
        # Infeasible or unbounded
        return {
            "status": "INFEASIBLE",
            "message": "It is mathematically impossible to meet all your constraints. Try increasing your budget, or lowering your expectations for protein/calories.",
            "plan": [],
            "metrics": None
        }
