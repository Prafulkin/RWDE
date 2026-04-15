import streamlit as st
import pandas as pd
from optimizer.diet import optimize_diet
from optimizer.time_planner import optimize_time

# Configure the Streamlit page
st.set_page_config(page_title="RWDE - Real-World Decision Engine", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for extra aesthetic polish
st.markdown("""
<style>
    .metric-box {
        background-color: #111111;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #00B4D8;
    }
    .metric-label {
        font-size: 14px;
        color: #888;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🧠 RWDE")
st.sidebar.markdown("Real-World Decision Engine")
mode = st.sidebar.radio("Select Optimizer Module", ["Budget Diet Optimizer", "Weekly Time Planner"])

st.sidebar.markdown("---")
st.sidebar.markdown("""
*Powered by Google OR-Tools.*
Mathematical optimization driving real-world constraint logic.
""")

if mode == "Budget Diet Optimizer":
    st.title("🥗 Budget Diet Optimizer")
    st.markdown("Find the mathematically cheapest combination of foods to hit your nutritional goals, accounting for real-world constraints like maximum meal sizes and budget limits.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Set Constraints")
        budget = st.slider("Daily Budget (₹)", min_value=50, max_value=500, value=250, step=10)
        min_meals = st.slider("Target Number of Meals", min_value=2, max_value=6, value=3)
        min_protein = st.number_input("Minimum Protein (g)", min_value=10, max_value=250, value=80, step=5)
        min_calories = st.number_input("Minimum Calories", min_value=500, max_value=4000, value=1500, step=100)
        max_calories = st.number_input("Maximum Calories", min_value=1000, max_value=5000, value=2500, step=100)
        
        run_opt = st.button("Run Optimization 🚀", use_container_width=True, type="primary")
        
    with col2:
        st.subheader("Decision Output")
        
        if run_opt:
            with st.spinner("Formulating constraints and solving LP model..."):
                result = optimize_diet(budget, min_protein, min_calories, max_calories, min_meals)
                
            if result['status'] == 'OPTIMAL':
                st.success("Mathematical Solution Found!")
                
                # Metrics Row
                m1, m2, m3 = st.columns(3)
                m1.markdown(f'<div class="metric-box"><div class="metric-label">Actual Cost</div><div class="metric-value">₹{result["metrics"]["Total Cost (₹)"]}</div></div>', unsafe_allow_html=True)
                m2.markdown(f'<div class="metric-box"><div class="metric-label">Protein Achieved</div><div class="metric-value">{result["metrics"]["Total Protein (g)"]}g</div></div>', unsafe_allow_html=True)
                m3.markdown(f'<div class="metric-box"><div class="metric-label">Caloric Payload</div><div class="metric-value">{result["metrics"]["Total Calories"]} kcal</div></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Plan Table
                df = pd.DataFrame(result['plan'])
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Explanation
                st.info(f"**Trade-off Analysis:**\n\n{result['explanation']}")

            else:
                st.error(f"Solver Status: {result['status']}\n\n{result.get('message', 'Unsolvable constraints.')}")

elif mode == "Weekly Time Planner":
    st.title("⏱️ Weekly Time Planner")
    st.markdown("A Knapsack-style algorithm solving for maximum subjective value generation within your weekly hours capacity, cleanly sacrificing lower-priority tasks.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Set Constraints")
        total_hours = st.slider("Total Available Hours / Week", min_value=10, max_value=120, value=40, step=5)
        min_personal = st.slider("Required Personal/Health Hours", min_value=0, max_value=40, value=10, step=2)
        must_do_strict = st.checkbox("Strict 'Must-Do' Priority?", value=True, help="If checked, priority 10 items must be fully completed or the solver fails.")
        
        run_opt = st.button("Run Schedule Optimizer 🚀", use_container_width=True, type="primary")

    with col2:
        st.subheader("Strategic Schedule output")

        if run_opt:
            with st.spinner("Formulating Knapsack model..."):
                result = optimize_time(total_hours, min_personal, must_do_strict)
                
            if result['status'] == 'OPTIMAL':
                st.success("Mathematical Solution Found!")
                
                # Metrics Row
                m1, m2, m3 = st.columns(3)
                m1.markdown(f'<div class="metric-box"><div class="metric-label">Hours Allocated</div><div class="metric-value">{result["metrics"]["Hours Scheduled"]}h</div></div>', unsafe_allow_html=True)
                m2.markdown(f'<div class="metric-box"><div class="metric-label">Capacity Utilized</div><div class="metric-value">{result["metrics"]["Capacity Utilized %"]}%</div></div>', unsafe_allow_html=True)
                m3.markdown(f'<div class="metric-box"><div class="metric-label">Subjective Value Generated</div><div class="metric-value">{result["metrics"]["Total Subjective Value"]}</div></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                df = pd.DataFrame(result['plan'])
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Explanation
                st.info(f"**Trade-off Analysis:**\n\n{result['explanation']}")

            else:
                st.error(f"Solver Status: {result['status']}\n\n{result.get('message', 'Unsolvable constraints.')}")
