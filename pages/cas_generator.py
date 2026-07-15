from pathlib import Path

import pandas as pd
import streamlit as st

from services.repository import (
    get_application,
    get_assessment_details,
    list_applications,
    list_cas_versions,
    list_interviews,
    save_cas,
)
from services.template_service import build_cas, hiring_manager_email

st.title("CAS and Hiring Manager Pack")
applications = list_applications()
if not applications:
    st.info("No applications are available.")
    st.stop()

app_map = {f"{a['full_name']} | {a['job_title']} | {a['current_stage']}": a for a in applications}
selected = st.selectbox("Candidate application", list(app_map))
application = get_application(app_map[selected]["application_id"])
assessment = get_assessment_details(application["application_id"])
interviews = list_interviews(application["application_id"])

cas_text = build_cas(application, assessment, interviews)
edited_cas = st.text_area("Candidate Assessment Summary", value=cas_text, height=520)
generated_by = st.text_input("Prepared by", value="TA Team")
approved = st.checkbox("I have reviewed and approved this CAS")

if st.button("Save New CAS Version", type="primary", disabled=not approved):
    output_dir = Path(__file__).resolve().parents[1] / "uploads" / "cas_reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    version_preview = len(list_cas_versions(application["application_id"])) + 1
    output_path = output_dir / f"{application['application_id']}_CAS_v{version_preview}.txt"
    output_path.write_text(edited_cas, encoding="utf-8")
    version = save_cas(application["application_id"], application["current_stage"], edited_cas, generated_by, str(output_path))
    st.success(f"CAS version {version} saved.")

st.download_button("Download CAS", edited_cas, file_name=f"{application['full_name']}_CAS.txt", mime="text/plain")

st.subheader("Hiring Manager Email")
assessment_points = "\n".join(f"- {row['criterion_name']}: {row['evidence']}" for row in assessment if row["awarded_score"] < row["weight"] * 0.7)
interview_details = "Add interview date, time, panel, meeting link, and attachments."
subject, email_body = hiring_manager_email(application, application["current_stage"], application.get("suitability_reason") or "Assessment pending", assessment_points or "No material gaps identified in the recorded assessment.", interview_details)
st.text_input("Email subject", value=subject)
st.text_area("Email body", value=email_body, height=360)

st.subheader("CAS Version History")
versions = list_cas_versions(application["application_id"])
if versions:
    st.dataframe(pd.DataFrame(versions)[["version_number", "stage", "generated_at", "generated_by", "file_path"]], use_container_width=True, hide_index=True)
