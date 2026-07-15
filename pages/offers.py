import pandas as pd
import streamlit as st

from services.repository import get_offer, list_applications, list_offers, update_stage, upsert_offer

st.title("Offers and Joining")
applications = list_applications()
if not applications:
    st.info("No applications are available.")
    st.stop()

app_map = {f"{a['full_name']} | {a['job_title']} | {a['current_stage']}": a for a in applications}
selected = st.selectbox("Candidate application", list(app_map))
application = app_map[selected]
existing = get_offer(application["application_id"]) or {}

with st.form("offer_form"):
    offer_statuses = ["Draft", "Approval Pending", "Released", "Accepted", "Declined", "Joined", "Dropped"]
    default_status = existing.get("offer_status") or "Draft"
    offer_status = st.selectbox("Offer status", offer_statuses, index=offer_statuses.index(default_status) if default_status in offer_statuses else 0)
    col1, col2 = st.columns(2)
    with col1:
        proposed_ctc = st.number_input("Proposed CTC", min_value=0.0, value=float(existing.get("proposed_ctc") or 0), step=0.5)
        offer_date = st.date_input("Offer date", value=None)
        joining_date = st.date_input("Planned joining date", value=None)
    with col2:
        approved_ctc = st.number_input("Approved CTC", min_value=0.0, value=float(existing.get("approved_ctc") or 0), step=0.5)
        acceptance_date = st.date_input("Acceptance date", value=None)
        actual_joining_date = st.date_input("Actual joining date", value=None)
    drop_reason = st.text_area("Decline / drop reason", value=existing.get("drop_reason") or "")
    submitted = st.form_submit_button("Save Offer", type="primary")

if submitted:
    upsert_offer(
        application["application_id"],
        {
            "offer_status": offer_status,
            "proposed_ctc": proposed_ctc,
            "approved_ctc": approved_ctc,
            "offer_date": offer_date.isoformat() if offer_date else None,
            "acceptance_date": acceptance_date.isoformat() if acceptance_date else None,
            "joining_date": joining_date.isoformat() if joining_date else None,
            "actual_joining_date": actual_joining_date.isoformat() if actual_joining_date else None,
            "drop_reason": drop_reason,
        },
    )
    stage_map = {"Released": "Offer Released", "Accepted": "Offer Accepted", "Joined": "Joined"}
    if offer_status in stage_map and application["current_stage"] != stage_map[offer_status]:
        update_stage(application["application_id"], stage_map[offer_status], "TA Team", f"Offer status changed to {offer_status}")
    st.success("Offer record saved.")

st.subheader("Offer Register")
rows = list_offers()
if rows:
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
