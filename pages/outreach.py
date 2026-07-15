from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

from services.repository import get_application, list_applications, list_outreach, save_outreach
from services.template_service import candidate_outreach, jd_application_email

st.title("Candidate Outreach")
applications = list_applications()
if not applications:
    st.info("No applications are available.")
    st.stop()

app_map = {f"{a['full_name']} | {a['job_title']} | {a['score_bucket'] or 'Unassessed'}": a for a in applications}
selected = st.selectbox("Candidate application", list(app_map))
application = get_application(app_map[selected]["application_id"])

if not application.get("score_bucket"):
    st.warning("Run the candidate assessment before generating fit-based outreach.")

col1, col2 = st.columns(2)
with col1:
    channel = st.selectbox("Channel", ["LinkedIn InMail", "LinkedIn Connection Request", "Email"])
with col2:
    message_type = st.selectbox("Message type", ["Initial Outreach", "JD and Application Link", "Follow-up 1", "Follow-up 2"])

if message_type == "JD and Application Link":
    subject, default_body = jd_application_email(application)
else:
    subject, default_body = candidate_outreach(application, channel)

subject = st.text_input("Subject", value=subject)
body = st.text_area("Message", value=default_body, height=320)
follow_up_days = st.number_input("Follow-up after days", min_value=0, max_value=30, value=3)
sent_status = st.selectbox("Status", ["Draft", "Sent"])

if st.button("Save Outreach Record", type="primary"):
    now = datetime.now(timezone.utc)
    save_outreach(
        {
            "application_id": application["application_id"],
            "channel": channel,
            "message_type": message_type,
            "subject": subject,
            "message_body": body,
            "sent_status": sent_status,
            "sent_at": now.isoformat(timespec="seconds") if sent_status == "Sent" else None,
            "follow_up_due_at": (now + timedelta(days=int(follow_up_days))).isoformat(timespec="seconds"),
        }
    )
    st.success("Outreach record saved. This MVP records messages; connect Gmail/Outlook later for direct sending.")

st.subheader("Outreach History")
rows = list_outreach(application["application_id"])
if rows:
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("No outreach has been recorded for this candidate.")
