TA COPILOT DUPLICATION PATCH

Replace these files in the matching folders of your GitHub repository:

1. pages/requisitions.py
2. pages/candidate_assessment.py
3. services/repository.py
4. services/analytics_service.py

What the patch changes:
- Prevents the same requisition submission from being processed twice in one session.
- Checks for an existing matching open requisition before creating another.
- Checks LinkedIn URL, email, phone, and name + current company before creating a candidate.
- Reuses an existing candidate record and existing candidate/requisition application.
- Counts distinct active candidates on the dashboard.

Important:
This patch prevents future duplication. It does not delete rows already stored in recruitment.db.
For a test deployment where no data needs to be retained, remove recruitment.db from the repository and reboot the app. The database will be recreated automatically.
