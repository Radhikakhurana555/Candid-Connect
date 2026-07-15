from datetime import date, datetime, time

import pandas as pd
import streamlit as st

from services.repository import list_applications, list_interviews, save_interview, update_interview_feedback

st.title("Interview Management")
schedule_tab, feedback_tab = st.tabs(["Schedule Interview", "Submit Feedback"])
applications = list_applications()

with schedule_tab:
    if not applications:
        st.info("No applications are available.")
    else:
        app_map = {f"{a['full_name']} | {a['job_title']} | {a['current_stage']}": a for a in applications}
        with st.form("schedule_interview"):
            selected = st.selectbox("Candidate", list(app_map))
            stage = st.selectbox("Interview stage", ["Recruiter Screening", "R1", "R2", "Case Study", "Leadership Discussion"])
            date_col, time_col = st.columns(2)
            with date_col:
                interview_day = st.date_input("Interview date", value=date.today())
            with time_col:
                interview_time = st.time_input("Interview time", value=datetime.now().time().replace(second=0, microsecond=0))
            interviewers = st.text_input("Interviewers", help="Comma-separated names or emails")
            submitted = st.form_submit_button("Schedule Interview", type="primary")
        if submitted:
            save_interview(
                {
                    "application_id": app_map[selected]["application_id"],
                    "interview_stage": stage,
                    "interview_date": datetime.combine(interview_day, interview_time).isoformat(timespec="minutes"),
                    "interviewer_names": interviewers,
                }
            )
            st.success("Interview scheduled.")

with feedback_tab:
    interviews = list_interviews()
    if not interviews:
        st.info("No interviews are available.")
    else:
        interview_map = {
            f"{i['full_name']} | {i['interview_stage']} | {i.get('interview_date') or 'Date not set'}": i
            for i in interviews
        }
        selected = st.selectbox("Interview", list(interview_map), key="feedback_interview")
        record = interview_map[selected]
        with st.form("feedback_form"):
            overall_rating = st.slider("Overall rating", 1.0, 5.0, 3.0, 0.5)
            recommendation = st.selectbox("Recommendation", ["Strongly Proceed", "Proceed", "Hold", "Consider for Another Role", "Reject"])
            notes = st.text_area("Feedback and assessment notes", height=220)
            submitted = st.form_submit_button("Submit Feedback", type="primary")
        if submitted:
            update_interview_feedback(
                record["interview_id"],
                {
                    "interview_status": "Completed",
                    "feedback_status": "Submitted",
                    "recommendation": recommendation,
                    "overall_rating": overall_rating,
                    "feedback_notes": notes,
                },
            )
            st.success("Feedback submitted.")

st.subheader("Interview Register")
rows = list_interviews()
if rows:
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
