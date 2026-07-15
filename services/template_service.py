from __future__ import annotations

import json


def _loads(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        result = json.loads(value)
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        return []


def candidate_outreach(application: dict, channel: str = "LinkedIn InMail") -> tuple[str, str]:
    subject = f"Opportunity with Intellecap – {application['job_title']}"
    reason = application.get("suitability_reason") or "your relevant professional experience"
    body = f"""Hi {application['full_name']},

I came across your profile and noted your experience as {application.get('current_title') or 'a professional'} with {application.get('current_company') or 'your current organisation'}.

We are currently hiring for the position of {application['job_title']} within {application['business_segment']} at Intellecap. Based on the information available, {reason}

Please let me know whether you would be open to a brief discussion.

Regards,
Talent Acquisition
Intellecap"""
    if channel == "LinkedIn Connection Request":
        body = (
            f"Hi {application['full_name']}, we are hiring for {application['job_title']} at Intellecap. "
            "Your experience appears relevant, and I would be glad to connect and share details."
        )
    return subject, body


def jd_application_email(application: dict) -> tuple[str, str]:
    subject = f"Job Description and Application Link – {application['job_title']}"
    body = f"""Dear {application['full_name']},

Thank you for expressing interest in the {application['job_title']} opportunity with {application['business_segment']} at Intellecap.

Please review the job description and complete your application using the link below:
{application.get('application_link') or '[Application link to be added]'}

Location: {application.get('location') or 'As per the job description'}

Once the application is completed, we will review the details and share the next steps.

Regards,
Talent Acquisition
Intellecap"""
    return subject, body


def hiring_manager_email(application: dict, stage: str, cas_summary: str, assessment_points: str, interview_details: str) -> tuple[str, str]:
    subject = f"{stage} Discussion – {application['full_name']} | {application['job_title']}"
    body = f"""Dear {application.get('hiring_manager') or 'Hiring Manager'},

Please find below the details of {application['full_name']} for the {stage} discussion for the position of {application['job_title']}.

Current Organisation: {application.get('current_company') or 'Not available'}
Current Designation: {application.get('current_title') or 'Not available'}
Total Experience: {application.get('total_experience') or 0} years
Fitment Score: {application.get('fit_score') or 0}/100
Recommendation: {application.get('recommendation') or 'Pending assessment'}
LinkedIn: {application.get('linkedin_url') or 'Not available'}

Fitment Summary:
{cas_summary}

Key areas to assess:
{assessment_points}

Interview Details:
{interview_details}

The candidate's resume and latest CAS may be enclosed for reference.

Regards,
Talent Acquisition"""
    return subject, body


def build_cas(application: dict, assessment_details: list[dict], interview_rows: list[dict]) -> str:
    strengths = _loads(application.get("strengths"))
    concerns = _loads(application.get("concerns"))
    score_lines = "\n".join(
        f"- {row['criterion_name']}: {row['awarded_score']}/{row['weight']} – {row.get('evidence') or ''}"
        for row in assessment_details
    ) or "- Assessment pending"
    interview_lines = "\n".join(
        f"- {row.get('interview_stage')}: {row.get('recommendation') or 'Feedback pending'}; {row.get('feedback_notes') or ''}"
        for row in interview_rows
    ) or "- No interview feedback recorded"

    return f"""CANDIDATE ASSESSMENT SUMMARY

Candidate: {application['full_name']}
Position: {application['job_title']}
Business Segment: {application['business_segment']}
Current Organisation: {application.get('current_company') or 'Not available'}
Current Designation: {application.get('current_title') or 'Not available'}
Location: {application.get('location') or 'Not available'}
Total Experience: {application.get('total_experience') or 0} years
LinkedIn: {application.get('linkedin_url') or 'Not available'}
Current Stage: {application.get('current_stage')}

FITMENT
Score: {application.get('fit_score') or 0}/100
Bucket: {application.get('score_bucket') or 'Pending'}
Recommendation: {application.get('recommendation') or 'Pending'}

Fitment Summary:
{application.get('suitability_reason') or 'Assessment pending.'}

Strengths:
{chr(10).join(f'- {item}' for item in strengths) or '- Not yet assessed'}

Areas to Validate:
{chr(10).join(f'- {item}' for item in concerns) or '- Not yet assessed'}

SCORE BREAKDOWN
{score_lines}

INTERVIEW FEEDBACK
{interview_lines}

Recruiter Notes:
[Add recruiter observations, compensation, notice period, motivation, and mobility details before sharing.]
"""
