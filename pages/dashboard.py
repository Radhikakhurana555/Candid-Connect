import streamlit as st
import pandas as pd

from services.analytics_service import dashboard_metrics, funnel_counts

st.title("Intellecap TA Copilot")
st.caption("Sourcing-to-joining recruitment workflow")

metrics = dashboard_metrics()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Open Positions", metrics.get("open_positions", 0))
col2.metric("Active Candidates", metrics.get("active_candidates", 0))
col3.metric("Scheduled Interviews", metrics.get("scheduled_interviews", 0))
col4.metric("Offers in Progress", metrics.get("offers_in_progress", 0))

if metrics.get("overdue_reminders", 0):
    st.warning(f"{metrics['overdue_reminders']} reminder(s) are overdue.")
else:
    st.success("No overdue reminders.")

st.subheader("Recruitment Funnel")
funnel = funnel_counts()
st.bar_chart(pd.DataFrame({"Stage": funnel.keys(), "Candidates": funnel.values()}).set_index("Stage"))

st.info(
    "Start by creating a requisition. Then add candidates under Candidate Assessment, "
    "run scoring, generate outreach, and move candidates through the pipeline."
)
