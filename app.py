from pathlib import Path
import sys

import streamlit as st

# Ensure local packages are importable in Streamlit Community Cloud.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from database.db import init_db

st.set_page_config(page_title="Intellecap TA Copilot", page_icon="🧭", layout="wide")
init_db()

st.sidebar.markdown("## Intellecap TA Copilot")
st.sidebar.caption("Internal recruitment workflow MVP")

pages = {
    "Overview": [
        st.Page("pages/dashboard.py", title="Dashboard", icon="📊", default=True),
    ],
    "Talent Acquisition": [
        st.Page("pages/requisitions.py", title="Requisitions", icon="📋"),
        st.Page("pages/sourcing.py", title="AI Sourcing", icon="🔍"),
        st.Page("pages/candidate_assessment.py", title="Candidate Assessment", icon="🧠"),
        st.Page("pages/outreach.py", title="Outreach", icon="✉️"),
        st.Page("pages/pipeline.py", title="Recruitment Pipeline", icon="🗂️"),
    ],
    "Interview and Selection": [
        st.Page("pages/interviews.py", title="Interviews", icon="🎤"),
        st.Page("pages/cas_generator.py", title="CAS Generator", icon="📄"),
        st.Page("pages/offers.py", title="Offers and Joining", icon="🤝"),
    ],
    "Management": [
        st.Page("pages/reminders.py", title="Nudges and Reminders", icon="⏰"),
        st.Page("pages/analytics.py", title="Analytics", icon="📈"),
    ],
}

navigation = st.navigation(pages)
navigation.run()
