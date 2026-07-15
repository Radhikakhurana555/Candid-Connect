from datetime import date, datetime, timezone

import pandas as pd
import streamlit as st

from services.repository import create_reminder, list_applications, list_reminders, mark_reminder_done

st.title("Nudges and Reminders")
applications = list_applications()

with st.expander("Create Reminder", expanded=True):
    if not applications:
        st.info("No applications are available.")
    else:
        app_map = {f"{a['full_name']} | {a['job_title']}": a for a in applications}
        with st.form("reminder_form"):
            selected = st.selectbox("Candidate application", list(app_map))
            reminder_type = st.selectbox("Reminder type", ["Candidate Follow-up", "Application Completion", "Interview Confirmation", "Case Study Due", "Hiring Manager Feedback", "Offer Acceptance", "Pre-joining Check-in"])
            recipient_type = st.selectbox("Recipient", ["Candidate", "Hiring Manager", "Recruiter", "Interviewer"])
            recipient_email = st.text_input("Recipient email")
            date_col, time_col = st.columns(2)
            with date_col:
                due_day = st.date_input("Due date", value=date.today())
            with time_col:
                due_time = st.time_input("Due time", value=datetime.now().time().replace(second=0, microsecond=0))
            submitted = st.form_submit_button("Create Reminder", type="primary")
        if submitted:
            create_reminder(
                {
                    "application_id": app_map[selected]["application_id"],
                    "reminder_type": reminder_type,
                    "recipient_type": recipient_type,
                    "recipient_email": recipient_email,
                    "due_at": datetime.combine(due_day, due_time).replace(tzinfo=timezone.utc).isoformat(timespec="minutes"),
                }
            )
            st.success("Reminder created.")

rows = list_reminders()
if rows:
    df = pd.DataFrame(rows)
    now = datetime.now(timezone.utc)
    df["due_datetime"] = pd.to_datetime(df["due_at"], utc=True, errors="coerce")
    df["timing"] = df.apply(lambda r: "Overdue" if r["status"] == "Pending" and r["due_datetime"] < now else ("Pending" if r["status"] == "Pending" else "Completed"), axis=1)
    st.dataframe(df.drop(columns=["due_datetime"]), use_container_width=True, hide_index=True)
    pending_map = {f"{row['full_name']} | {row['reminder_type']} | {row['due_at']}": row for row in rows if row["status"] == "Pending"}
    if pending_map:
        selected_reminder = st.selectbox("Mark reminder complete", list(pending_map))
        if st.button("Complete Reminder"):
            mark_reminder_done(pending_map[selected_reminder]["reminder_id"])
            st.success("Reminder completed.")
            st.rerun()
else:
    st.info("No reminders have been created.")

st.caption("For automatic notifications when the app is closed, run a separate scheduler or connect Power Automate, Gmail/Outlook, or a backend job service.")
