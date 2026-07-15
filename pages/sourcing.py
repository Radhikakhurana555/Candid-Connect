import pandas as pd
import streamlit as st

from services.repository import (
    create_application,
    create_candidate,
    find_candidate_by_linkedin,
    list_requisitions,
)
from services.sourcing_service import build_sourcing_strategy
from utils.validators import validate_linkedin_url

st.title("AI-assisted Sourcing")
st.caption("Generate a sourcing strategy and import verifiable, clickable profile links. This MVP does not scrape LinkedIn.")

requisitions = list_requisitions(open_only=True)
if not requisitions:
    st.warning("Create an open requisition first.")
    st.stop()

req_map = {f"{r['requisition_id']} | {r['job_title']}": r for r in requisitions}
selected_label = st.selectbox("Select requisition", list(req_map))
requisition = req_map[selected_label]

strategy = build_sourcing_strategy(requisition)
col1, col2 = st.columns(2)
with col1:
    st.subheader("LinkedIn Boolean")
    st.code(strategy["linkedin_boolean"] or "Add role criteria to generate a Boolean string.", language=None)
with col2:
    st.subheader("Google X-ray Query")
    st.code(strategy["google_xray_query"] or "Add role criteria to generate a query.", language=None)
st.caption(strategy["note"])

with st.expander("Targeting logic", expanded=True):
    st.write("**Titles:**", ", ".join(strategy["primary_titles"]) or "Not specified")
    st.write("**Mandatory keywords:**", ", ".join(strategy["mandatory_keywords"]) or "Not specified")
    st.write("**Preferred keywords:**", ", ".join(strategy["optional_keywords"]) or "Not specified")
    st.write("**Target companies:**", ", ".join(strategy["target_companies"]) or "Not specified")

st.divider()
st.subheader("Import candidate profiles")
template = pd.DataFrame(
    columns=["full_name", "linkedin_url", "current_company", "current_title", "location", "total_experience", "email", "phone", "source"]
)
st.download_button("Download CSV template", template.to_csv(index=False), "candidate_import_template.csv", "text/csv")
upload = st.file_uploader("Upload completed CSV", type=["csv"])

if upload:
    df = pd.read_csv(upload).fillna("")
    st.dataframe(df, use_container_width=True, hide_index=True)
    if st.button("Import Profiles", type="primary"):
        imported, duplicates, invalid = 0, 0, 0
        for _, row in df.iterrows():
            name = str(row.get("full_name", "")).strip()
            url = str(row.get("linkedin_url", "")).strip()
            if not name or not validate_linkedin_url(url):
                invalid += 1
                continue
            if find_candidate_by_linkedin(url):
                duplicates += 1
                continue
            candidate_id = create_candidate(
                {
                    "full_name": name,
                    "linkedin_url": url,
                    "current_company": row.get("current_company", ""),
                    "current_title": row.get("current_title", ""),
                    "location": row.get("location", ""),
                    "total_experience": float(row.get("total_experience") or 0),
                    "email": row.get("email", ""),
                    "phone": row.get("phone", ""),
                    "source": row.get("source", "LinkedIn"),
                    "verification_status": "Partially Verified",
                }
            )
            create_application(candidate_id, requisition["requisition_id"])
            imported += 1
        st.success(f"Imported: {imported} | Duplicates: {duplicates} | Invalid rows: {invalid}")
