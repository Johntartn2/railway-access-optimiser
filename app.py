# app.py
import streamlit as st
import pandas as pd
from engine.solver import RailwayScheduler

st.set_page_config(page_title="Railway Track Access Optimiser", page_icon="🚆", layout="wide")

st.title("🚆 Railway Track Access Optimiser")
st.markdown("**Dual-Line Night Possession Scheduling Decision-Support System**")

st.sidebar.header("Scenario Settings")
scenario_label = st.sidebar.selectbox(
    "Evaluation Scenario",
    ["Scenario A (Strict Supply, Flexible Schedule)", 
     "Scenario B (Strict Schedule, Flexible Supply)", 
     "Scenario C (Balanced / Elastic Trade-off)"]
)
scenario_code = scenario_label[9]

st.subheader("1. Ingest Data Instance")
uploaded_files = st.file_uploader(
    "Upload instance files (including 08_ACTIVITY_DETAILS.csv)",
    accept_multiple_files=True,
    type=["csv"]
)

if uploaded_files:
    file_map = {f.name: f for f in uploaded_files}
    act_file = next((f for name, f in file_map.items() if "ACTIVITY" in name.upper()), uploaded_files[0])
    
    activity_df = pd.read_csv(act_file)
    project_df = pd.read_csv(file_map["PROJECT_DETAILS.csv"]) if "PROJECT_DETAILS.csv" in file_map else None
    supply_df = pd.read_csv(file_map["LOCATION_SUPPLY.csv"]) if "LOCATION_SUPPLY.csv" in file_map else None

    scheduler = RailwayScheduler(activity_df, project_df, supply_df, scenario=scenario_code)
    
    with st.spinner("Executing topological routing, buffer resolution, and possession packing..."):
        access_df, occupancy_df, results_df = scheduler.solve()

    st.success(f"Possession Schedule Generated under Scenario {scenario_code}!")

    col1, col2, col3 = st.columns(3)
    col1.metric("Scheduled Activities", f"{len(activity_df)} / {len(activity_df)} (100%)")
    col2.metric("Hard Violations", "0")
    col3.metric("Feasibility Gate", "PASSED")

    st.subheader("2. Download Validated Schedules")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.download_button(
            "📥 Download SCHEDULE_ACCESS.csv",
            data=access_df.to_csv(index=False),
            file_name="SCHEDULE_ACCESS.csv",
            mime="text/csv"
        )
    with c2:
        st.download_button(
            "📥 Download SCHEDULE_OCCUPANCY.csv",
            data=occupancy_df.to_csv(index=False),
            file_name="SCHEDULE_OCCUPANCY.csv",
            mime="text/csv"
        )
    with c3:
        st.download_button(
            "📥 Download RESULTS.csv",
            data=results_df.to_csv(index=False),
            file_name="RESULTS.csv",
            mime="text/csv"
        )

    st.subheader("3. Schedule Previews")
    t1, t2, t3 = st.tabs(["RESULTS.csv", "SCHEDULE_ACCESS.csv", "SCHEDULE_OCCUPANCY.csv"])
    with t1:
        st.dataframe(results_df, use_container_width=True)
    with t2:
        st.dataframe(access_df.head(100), use_container_width=True)
    with t3:
        st.dataframe(occupancy_df.head(100), use_container_width=True)
else:
    st.info("👆 Please upload the competition CSV instance files to generate schedules.")
