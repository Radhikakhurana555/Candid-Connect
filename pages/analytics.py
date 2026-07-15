import pandas as pd
import plotly.express as px
import streamlit as st

from services.analytics_service import conversion_metrics, funnel_counts, hires_by_segment, rejections_by_stage

st.title("Recruitment Analytics")
conversions = conversion_metrics()
cols = st.columns(4)
for col, (label, value) in zip(cols, conversions.items()):
    col.metric(label, f"{value}%")

st.subheader("Sourcing-to-Joining Funnel")
funnel = funnel_counts()
funnel_df = pd.DataFrame({"Stage": list(funnel.keys()), "Candidates": list(funnel.values())})
fig = px.funnel(funnel_df, x="Candidates", y="Stage")
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Hires by Business Segment")
    hires = hires_by_segment()
    if hires:
        st.bar_chart(pd.DataFrame(hires).set_index("business_segment"))
    else:
        st.info("No joining data is available.")
with right:
    st.subheader("Rejections by Previous Stage")
    rejects = rejections_by_stage()
    if rejects:
        st.bar_chart(pd.DataFrame(rejects).set_index("stage"))
    else:
        st.info("No rejection-stage data is available.")

st.markdown("### Metric definitions")
st.write("**Sourced → Interviewed:** unique candidates with at least one completed formal interview divided by applications created.")
st.write("**Interviewed → Offer:** offers released/accepted/joined divided by candidates with a completed interview.")
st.write("**Offer → Joining:** joined candidates divided by released/accepted/joined offers.")
