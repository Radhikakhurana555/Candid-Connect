from datetime import date

import pandas as pd
import streamlit as st

from services.repository import create_requisition, list_requisitions
from utils.constants import BUSINESS_SEGMENTS

st.title("Requisition Management")

create_tab, list_tab = st.tabs(["Create Requisition", "View Requisitions"])

with create_tab:
    st.caption("Define the role and scoring criteria. Weights must total 100.")
    with st.form("requisition_form"):
        job_title = st.text_input("Job title *")
        business_segment = st.selectbox("Business segment *", BUSINESS_SEGMENTS)
        col1, col2 = st.columns(2)
        with col1:
            location = st.text_input("Location")
            hiring_manager = st.text_input("Hiring manager")
            experience_min = st.number_input("Minimum experience", min_value=0.0, max_value=50.0, value=5.0)
        with col2:
            recruiter = st.text_input("Recruiter")
            target_closure_date = st.date_input("Target closure date", value=date.today())
            experience_max = st.number_input("Maximum experience", min_value=0.0, max_value=50.0, value=12.0)
        mandatory_skills = st.text_area("Mandatory skills", help="One skill per line")
        preferred_skills = st.text_area("Preferred skills", help="One skill per line")
        target_companies = st.text_area("Target organisations", help="One organisation per line")
        job_description = st.text_area("Job description", height=220)
        application_link = st.text_input("Application link")

        st.markdown("### Scoring criteria")
        default_rows = pd.DataFrame(
            [
                {"criterion_name": "Relevant experience", "weight": 20.0, "criterion_type": "experience", "criterion_value": str(experience_min), "is_mandatory": True},
                {"criterion_name": "Mandatory skills", "weight": 25.0, "criterion_type": "keyword", "criterion_value": mandatory_skills, "is_mandatory": True},
                {"criterion_name": "Preferred skills", "weight": 15.0, "criterion_type": "keyword", "criterion_value": preferred_skills, "is_mandatory": False},
                {"criterion_name": "Target organisation exposure", "weight": 15.0, "criterion_type": "keyword", "criterion_value": target_companies, "is_mandatory": False},
                {"criterion_name": "Role and seniority alignment", "weight": 20.0, "criterion_type": "keyword", "criterion_value": job_title, "is_mandatory": False},
                {"criterion_name": "Location alignment", "weight": 5.0, "criterion_type": "location", "criterion_value": location, "is_mandatory": False},
            ]
        )
        criteria_df = st.data_editor(
            default_rows,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "criterion_type": st.column_config.SelectboxColumn(options=["keyword", "experience", "location"]),
                "is_mandatory": st.column_config.CheckboxColumn(),
            },
        )
        submitted = st.form_submit_button("Create Requisition", type="primary")

    if submitted:
        total_weight = float(criteria_df["weight"].fillna(0).sum())
        if not job_title.strip():
            st.error("Job title is required.")
        elif round(total_weight, 2) != 100.0:
            st.error(f"Scoring weights total {total_weight:g}. They must total 100.")
        else:
            req_id = create_requisition(
                {
                    "job_title": job_title,
                    "business_segment": business_segment,
                    "location": location,
                    "hiring_manager": hiring_manager,
                    "recruiter": recruiter,
                    "experience_min": experience_min,
                    "experience_max": experience_max,
                    "mandatory_skills": mandatory_skills,
                    "preferred_skills": preferred_skills,
                    "target_companies": target_companies,
                    "job_description": job_description,
                    "application_link": application_link,
                    "target_closure_date": target_closure_date.isoformat(),
                },
                criteria_df.fillna("").to_dict("records"),
            )
            st.success(f"Requisition {req_id} created successfully.")

with list_tab:
    rows = list_requisitions()
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No requisitions created yet.")
