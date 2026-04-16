import streamlit as st
import pandas as pd
from optimizer.diet import optimize_diet
from optimizer.time_planner import optimize_time

# Configure the Streamlit page
st.set_page_config(
    page_title="RWDE - Real-World Decision Engine",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom dark theme + card styling
st.markdown(
    """
    <style>
        :root {
            color-scheme: dark;
        }
        .stApp {
            background: #070707;
            color: #ececec;
        }
        .stSidebar {
            background: #090909;
            color: #e7e7e7;
        }
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        .card {
            background: #11131a;
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 24px;
            padding: 24px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.35);
            margin-bottom: 1.5rem;
        }
        .card .section-title {
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 0.55rem;
            color: #f8fafc;
        }
        .card .section-subtitle {
            color: #9ba1ad;
            margin-bottom: 1.5rem;
            line-height: 1.5;
        }
        .metric-card {
            background: linear-gradient(180deg, rgba(19,25,36,0.95), rgba(12,14,21,0.95));
            border: 1px solid rgba(255,255,255,0.07);
            border-radius: 22px;
            padding: 22px;
            text-align: center;
            min-height: 130px;
        }
        .metric-card .label {
            display: block;
            font-size: 0.9rem;
            color: #94a3b8;
            margin-bottom: 0.75rem;
        }
        .metric-card .value {
            font-size: 1.85rem;
            font-weight: 700;
            color: #81d8f6;
        }
        .metric-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            background: rgba(255,255,255,0.05);
            color: #dbeafe;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 999px;
            padding: 0.65rem 1rem;
            font-size: 0.92rem;
            margin-bottom: 1rem;
        }
        .metric-chip span {
            display: inline-block;
        }
        .accent-button button {
            background: #ff9f1c !important;
            color: #071317 !important;
            border: none !important;
            box-shadow: 0 16px 30px rgba(255,159,28,0.22);
            border-radius: 999px !important;
            padding: 0.9rem 1.4rem !important;
            font-weight: 700 !important;
        }
        .stSidebar .sidebar .css-1d391kg {
            color: #ffffff;
        }
        .stButton>button:hover {
            transform: translateY(-1px);
            transition: transform 0.15s ease-in-out;
        }
        .stAlert {
            border-radius: 20px;
        }
        .streamlit-expanderHeader {
            color: #e2e8f0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("# 🧠 RWDE")
st.sidebar.markdown("#### Real-World Decision Engine")
st.sidebar.markdown("---")
mode = st.sidebar.radio("Choose optimizer", ["Budget Diet Optimizer", "Weekly Time Planner"])

st.sidebar.markdown("---")
st.sidebar.markdown(
    "*Powered by OR-Tools and crisp decision science, not just heuristics.*"
)

if mode == "Budget Diet Optimizer":
    st.markdown(
        """
        <div class='card'>
            <div class='section-title'>🥗 Budget Diet Optimizer</div>
            <div class='section-subtitle'>A premium planner for the cheapest nutrient-complete diet under budget and calorie constraints.</div>
            <div class='metric-chip'>
                <span>6 food categories</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    controls, output = st.columns([1, 2])

    with controls:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Set your constraints</div>", unsafe_allow_html=True)
        budget = st.slider("Daily Budget (₹)", min_value=50, max_value=500, value=250, step=10)
        min_meals = st.slider("Target Number of Meals", min_value=2, max_value=6, value=3)
        min_protein = st.number_input("Minimum Protein (g)", min_value=10, max_value=250, value=80, step=5)
        min_calories = st.number_input("Minimum Calories", min_value=500, max_value=4000, value=1500, step=100)
        max_calories = st.number_input("Maximum Calories", min_value=1000, max_value=5000, value=2500, step=100)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Run Optimization", use_container_width=True, key="diet_run"):
            run_opt = True
        else:
            run_opt = False

    with output:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Decision output</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-subtitle'>Your optimal diet plan is produced as a nutrient-balanced schedule in a sleek dashboard format.</div>",
            unsafe_allow_html=True,
        )

        if run_opt:
            with st.spinner("Formulating constraints and solving the diet model..."):
                result = optimize_diet(budget, min_protein, min_calories, max_calories, min_meals)

            if result["status"] == "OPTIMAL":
                st.success("Mathematical solution found!")
                st.markdown("</div>", unsafe_allow_html=True)

                m1, m2, m3 = st.columns(3)
                m1.markdown(
                    "<div class='metric-card'><span class='label'>Actual Cost</span><span class='value'>₹{}</span></div>".format(
                        result["metrics"]["Total Cost (₹)"],
                    ),
                    unsafe_allow_html=True,
                )
                m2.markdown(
                    "<div class='metric-card'><span class='label'>Protein Achieved</span><span class='value'>{}g</span></div>".format(
                        result["metrics"]["Total Protein (g)"],
                    ),
                    unsafe_allow_html=True,
                )
                m3.markdown(
                    "<div class='metric-card'><span class='label'>Caloric Payload</span><span class='value'>{} kcal</span></div>".format(
                        result["metrics"]["Total Calories"],
                    ),
                    unsafe_allow_html=True,
                )

                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-title'>Recommended meal plan</div>", unsafe_allow_html=True)
                df = pd.DataFrame(result["plan"])
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-title'>Trade-off analysis</div>", unsafe_allow_html=True)
                st.markdown(result["explanation"], unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(
                    f"Solver Status: {result['status']}\n\n{result.get('message', 'Unsolvable constraints.')}",
                )
        else:
            st.markdown("<div class='section-subtitle'>Adjust the settings and click Run Optimization to see the optimized plan.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

elif mode == "Weekly Time Planner":
    st.markdown(
        """
        <div class='card'>
            <div class='section-title'>⏱️ Weekly Time Planner</div>
            <div class='section-subtitle'>A task prioritization dashboard that squeezes the most value from your weekly hours.</div>
            <div class='metric-chip'>
                <span>Dynamic priority scheduling</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    controls, output = st.columns([1, 2])

    with controls:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Set your week</div>", unsafe_allow_html=True)
        total_hours = st.slider("Total Available Hours / Week", min_value=10, max_value=120, value=40, step=5)
        min_personal = st.slider("Required Personal/Health Hours", min_value=0, max_value=40, value=10, step=2)
        must_do_strict = st.checkbox(
            "Strict 'Must-Do' Priority?",
            value=True,
            help="If checked, priority 10 items must be fully completed or the solver fails.",
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Run Schedule Optimizer", use_container_width=True, key="time_run"):
            run_opt = True
        else:
            run_opt = False

    with output:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Strategic schedule output</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-subtitle'>See the prioritized plan for your week, optimized for hours used and value delivered.</div>",
            unsafe_allow_html=True,
        )

        if run_opt:
            with st.spinner("Formulating the weekly knapsack model..."):
                result = optimize_time(total_hours, min_personal, must_do_strict)

            if result["status"] == "OPTIMAL":
                st.success("Mathematical solution found!")
                st.markdown("</div>", unsafe_allow_html=True)

                m1, m2, m3 = st.columns(3)
                m1.markdown(
                    "<div class='metric-card'><span class='label'>Hours Allocated</span><span class='value'>{}h</span></div>".format(
                        result["metrics"]["Hours Scheduled"],
                    ),
                    unsafe_allow_html=True,
                )
                m2.markdown(
                    "<div class='metric-card'><span class='label'>Capacity Utilized</span><span class='value'>{}%</span></div>".format(
                        result["metrics"]["Capacity Utilized %"],
                    ),
                    unsafe_allow_html=True,
                )
                m3.markdown(
                    "<div class='metric-card'><span class='label'>Subjective Value</span><span class='value'>{}</span></div>".format(
                        result["metrics"]["Total Subjective Value"],
                    ),
                    unsafe_allow_html=True,
                )

                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-title'>Recommended schedule</div>", unsafe_allow_html=True)
                df = pd.DataFrame(result["plan"])
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("<div class='section-title'>Trade-off analysis</div>", unsafe_allow_html=True)
                st.markdown(result["explanation"], unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error(
                    f"Solver Status: {result['status']}\n\n{result.get('message', 'Unsolvable constraints.')}",
                )
        else:
            st.markdown("<div class='section-subtitle'>Choose your weekly capacity and run the optimizer to reveal the best schedule.</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
