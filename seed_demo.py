"""Optional demo-data loader. Run once with: python seed_demo.py"""
from services.repository import create_application, create_candidate, create_requisition
from database.db import init_db

init_db()
req_id = create_requisition(
    {
        "job_title": "Manager - Climate Finance",
        "business_segment": "Intellecap Consulting",
        "location": "Mumbai",
        "hiring_manager": "Hiring Manager",
        "recruiter": "TA Team",
        "experience_min": 7,
        "experience_max": 12,
        "mandatory_skills": "Climate Finance\nFinancial Modelling\nStakeholder Management",
        "preferred_skills": "Blended Finance\nInfrastructure Advisory",
        "target_companies": "Deloitte\nEY\nKPMG\nPwC\nCRISIL",
        "job_description": "Climate-finance advisory role with modelling and stakeholder-management responsibilities.",
        "application_link": "https://example.com/apply",
    },
    [
        {"criterion_name": "Relevant experience", "weight": 20, "criterion_type": "experience", "criterion_value": "7", "is_mandatory": True},
        {"criterion_name": "Mandatory skills", "weight": 30, "criterion_type": "keyword", "criterion_value": "Climate Finance\nFinancial Modelling\nStakeholder Management", "is_mandatory": True},
        {"criterion_name": "Preferred skills", "weight": 20, "criterion_type": "keyword", "criterion_value": "Blended Finance\nInfrastructure Advisory", "is_mandatory": False},
        {"criterion_name": "Target organisation exposure", "weight": 15, "criterion_type": "keyword", "criterion_value": "Deloitte\nEY\nKPMG\nPwC\nCRISIL", "is_mandatory": False},
        {"criterion_name": "Role alignment", "weight": 10, "criterion_type": "keyword", "criterion_value": "Manager\nClimate Finance", "is_mandatory": False},
        {"criterion_name": "Location", "weight": 5, "criterion_type": "location", "criterion_value": "Mumbai", "is_mandatory": False},
    ],
)
candidate_id = create_candidate(
    {
        "full_name": "Demo Candidate",
        "email": "demo@example.com",
        "linkedin_url": "https://www.linkedin.com/in/demo-candidate",
        "current_company": "CRISIL",
        "current_title": "Manager - Climate Finance",
        "location": "Mumbai",
        "total_experience": 9,
        "resume_text": "Nine years in climate finance, blended finance, financial modelling, infrastructure advisory and stakeholder management at CRISIL.",
        "source": "Demo",
        "verification_status": "Partially Verified",
    }
)
app_id = create_application(candidate_id, req_id)
print(f"Created demo requisition {req_id} and application {app_id}")
