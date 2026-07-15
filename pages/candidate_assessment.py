import hashlib
import json

import pandas as pd
import streamlit as st

from services.repository import (
    create_application,
    create_candidate,
    find_duplicate_candidate,
    get_application,
    get_assessment_details,
    get_criteria,
    list_applications,
    list_requisitions,
    save_assessment,
)
from services.scoring_service import assess_candidate
from utils.constants import VERIFICATION_STATUSES
from utils.file_utils import extract_text, save_uploaded_file
from utils.validators import validate_linkedin_url


def submission_fingerprint(*values: object) -> str:
    normalized = "|".join(str(value or "").strip().lower() for value in values)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


st.title("Candidate Assessment")
add_tab, assess_tab = st.tabs(["Add Candidate", "Assess Existing Candidate"])

with add_tab:
    requisitions = list_requisitions(open_only=True)
    if not requisitions:
        st.warning("Create an open requisition first.")
    else:
        req_map = {f"{r['requisition_id']} | {r['job_title']}": r for r in requisitions}
        with st.form("candidate_form", clear_on_submit=False):
            selected_req = st.selectbox("Requisition", list(req_map))
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full name *")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                linkedin_url = st.text_input("LinkedIn URL")
                current_company = st.text_input("Current organisation")
            with col2:
                current_title = st.text_input("Current designation")
                location = st.text_input("Location")
                total_experience = st.number_input(
                    "Total experience", min_value=0.0, max_value=50.0, step=0.5
                )
                source = st.selectbox(
                    "Source",
                    ["LinkedIn", "Referral", "Job Portal", "Vendor", "Internal Database", "Other"],
                )
                verification_status = st.selectbox(
                    "Verification status", VERIFICATION_STATUSES, index=2
                )
            resume = st.file_uploader("Resume", type=["pdf", "docx", "txt"])
            submitted = st.form_submit_button("Save Candidate", type="primary")

        if submitted:
            requisition_id = req_map[selected_req]["requisition_id"]
            resume_identity = ""
            if resume is not None:
                resume_identity = f"{resume.name}:{resume.size}"

            fingerprint = submission_fingerprint(
                full_name,
                email,
                phone,
                linkedin_url,
                current_company,
                requisition_id,
                resume_identity,
            )

            if not full_name.strip():
                st.error("Candidate name is required.")
            elif linkedin_url and not validate_linkedin_url(linkedin_url):
                st.error("Enter a valid LinkedIn profile URL containing /in/.")
            elif st.session_state.get("last_candidate_submission") == fingerprint:
                st.warning("This candidate submission has already been processed.")
            else:
                existing_candidate = find_duplicate_candidate(
                    email=email,
                    phone=phone,
                    linkedin_url=linkedin_url,
                    full_name=full_name,
                    current_company=current_company,
                )

                if existing_candidate:
                    candidate_id = existing_candidate["candidate_id"]
                    app_id = create_application(candidate_id, requisition_id)
                    st.session_state["last_candidate_submission"] = fingerprint
                    st.info(
                        "An existing candidate record was found and reused; "
                        "no duplicate candidate was created."
                    )
                    st.success(f"Application ID: {app_id}")
                else:
                    path = save_uploaded_file(resume, "resumes")
                    candidate_id = create_candidate(
                        {
                            "full_name": full_name.strip(),
                            "email": email.strip(),
                            "phone": phone.strip(),
                            "linkedin_url": linkedin_url.strip(),
                            "current_company": current_company.strip(),
                            "current_title": current_title.strip(),
                            "location": location.strip(),
                            "total_experience": total_experience,
                            "resume_path": path,
                            "resume_text": extract_text(path),
                            "source": source,
                            "verification_status": verification_status,
                        }
                    )
                    app_id = create_application(candidate_id, requisition_id)
                    st.session_state["last_candidate_submission"] = fingerprint
                    st.success(f"Candidate saved. Application ID: {app_id}")

with assess_tab:
    applications = list_applications()
    if not applications:
        st.info("No candidate applications are available.")
    else:
        app_map = {
            f"{a['full_name']} | {a['job_title']} | {a['application_id']}": a
            for a in applications
        }
        selected_app_label = st.selectbox("Candidate application", list(app_map))
        selected = app_map[selected_app_label]
        application = get_application(selected["application_id"])
        st.write(
            f"**Current role:** {application.get('current_title') or 'Not available'} "
            f"at {application.get('current_company') or 'Not available'}"
        )
        st.write(f"**LinkedIn:** {application.get('linkedin_url') or 'Not available'}")
        st.write(f"**Verification:** {application.get('verification_status')}")
        if st.button("Run Role-specific Assessment", type="primary"):
            criteria = get_criteria(application["requisition_id"])
            result = assess_candidate(application, criteria)
            save_assessment(application["application_id"], result)
            st.success("Assessment completed.")
            st.rerun()

        refreshed = get_application(selected["application_id"])
        if refreshed.get("score_bucket"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Fit Score", f"{refreshed['fit_score']}/100")
            c2.metric("Bucket", refreshed["score_bucket"])
            c3.metric("Recommendation", refreshed["recommendation"])
            st.write(refreshed["suitability_reason"])
            details = get_assessment_details(refreshed["application_id"])
            st.dataframe(
                pd.DataFrame(details)[
                    ["criterion_name", "weight", "awarded_score", "evidence"]
                ],
                use_container_width=True,
                hide_index=True,
            )
            with st.expander("Stored strengths and concerns"):
                st.write("**Strengths**", json.loads(refreshed.get("strengths") or "[]"))
                st.write("**Concerns**", json.loads(refreshed.get("concerns") or "[]"))
