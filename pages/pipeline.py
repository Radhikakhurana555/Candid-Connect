import pandas as pd
import streamlit as st

from services.repository import get_stage_history, list_applications, update_stage
from utils.constants import PIPELINE_STAGES

st.title("Recruitment Pipeline")
applications = list_applications()
if not applications:
    st.info("No applications are available.")
    st.stop()

segment = st.multiselect("Filter by business segment", sorted({a['business_segment'] for a in applications}))
filtered = [a for a in applications if not segment or a["business_segment"] in segment]

stage_counts = pd.DataFrame(filtered).groupby("current_stage").size().reset_index(name="Candidates")
st.bar_chart(stage_counts.set_index("current_stage"))

st.subheader("Update Candidate Stage")
app_map = {f"{a['full_name']} | {a['job_title']} | {a['current_stage']}": a for a in filtered}
selected = st.selectbox("Candidate application", list(app_map))
application = app_map[selected]
new_stage = st.selectbox("Move to", PIPELINE_STAGES, index=PIPELINE_STAGES.index(application["current_stage"]))
changed_by = st.text_input("Updated by", value="TA Team")
reason = st.text_area("Comments / reason")

if st.button("Update Stage", type="primary"):
    update_stage(application["application_id"], new_stage, changed_by, reason)
    st.success(f"Candidate moved to {new_stage}.")
    st.rerun()

st.subheader("Stage History")
history = get_stage_history(application["application_id"])
if history:
    st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
