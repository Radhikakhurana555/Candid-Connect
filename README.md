# Intellecap TA Copilot — Streamlit MVP

A runnable internal recruitment workflow prototype covering:

1. Requisition creation and role-specific scoring weights
2. AI-assisted sourcing strategy and Boolean generation
3. Candidate and resume intake
4. Explainable fit scoring with >75, 50–75 and <50 buckets
5. Candidate outreach and JD/application-link templates
6. R1, R2, Case Study and complete stage tracking
7. Interview scheduling and structured feedback
8. Versioned Candidate Assessment Summary (CAS)
9. Hiring-manager email preparation
10. Offers, joining and drop-reason tracking
11. Candidate and stakeholder reminders
12. Sourcing-to-interview, interview-to-offer and offer-to-joining analytics

## Important sourcing note

The MVP does **not scrape LinkedIn**. It generates search strings for authorised LinkedIn Recruiter/public-search workflows and lets recruiters import profile URLs. URL validation checks format only; recruiters must verify profile identity and current information through authorised sources.

## 1. Prerequisites

- Python 3.10 or later
- Git (recommended)

## 2. Set up locally

```bash
cd intellecap_ta_copilot
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

The SQLite database `recruitment.db` is created automatically on first launch.

## 3. Optional demo data

```bash
python seed_demo.py
```

Run this only once on a fresh database.

## 4. Recommended usage sequence

1. Open **Requisitions** and create a role.
2. Confirm scoring weights total 100.
3. Use **AI Sourcing** to create search strings and import profile URLs.
4. Add resumes under **Candidate Assessment**.
5. Run the role-specific assessment.
6. Generate messages under **Outreach**.
7. Move candidates through stages under **Recruitment Pipeline**.
8. Schedule interviews and enter feedback.
9. Generate and approve a CAS at each stage.
10. Track offer and joining outcomes.
11. Create nudges and review analytics.

## 5. Scoring rules

- **Above 75:** Strong Fit — proceed with outreach
- **50 to 75:** Potential Fit — recruiter review required
- **Below 50:** Reject — do not progress unless overridden

Mandatory criteria can downgrade a Strong Fit to a Hold/Potential Fit when evidence is missing.

The included scoring engine is deterministic and keyword-based so the app runs without an external AI key. Replace or augment `services/scoring_service.py` with an approved LLM/embedding service for semantic assessment, while retaining the criterion-level evidence and human review.

## 6. Project structure

```text
app.py                         Navigation controller
pages/                         Streamlit screens
database/schema.sql            SQLite schema
database/db.py                 Database connection helpers
services/repository.py         CRUD and workflow operations
services/scoring_service.py    Explainable scoring logic
services/sourcing_service.py   Boolean and X-ray query generation
services/template_service.py   Outreach, HM email and CAS templates
services/analytics_service.py  Funnel and conversion metrics
utils/                         Constants, validation and file parsing
uploads/                       Local resume, JD and CAS storage
```

## 7. Production hardening before internal launch

The folder is an MVP. Before storing live candidate information:

- Move SQLite and local uploads to PostgreSQL plus approved encrypted storage.
- Add SSO and role-based access controls.
- Add consent, retention and deletion controls.
- Add audit logs for edits, downloads, sharing and overrides.
- Connect Gmail/Outlook only through approved organisational credentials.
- Run reminders in a backend scheduler; Streamlit alone should not be relied upon when no user session is open.
- Add malware scanning and file validation for uploads.
- Add field-level controls for compensation and sensitive assessment information.
- Complete security, privacy and legal review.

## 8. Streamlit deployment

Push the folder to a private Git repository and deploy `app.py`. Store secrets in the deployment platform’s secrets manager rather than Git. For confidential recruiting data, use an organisation-approved private deployment rather than an unrestricted public app.
