PIPELINE_STAGES = [
    "Sourced",
    "Outreach Initiated",
    "Interested",
    "Applied",
    "Recruiter Screening",
    "CAS Prepared",
    "Hiring Manager Review",
    "R1",
    "R2",
    "Case Study",
    "Leadership Discussion",
    "Reference Check",
    "Compensation Discussion",
    "Offer Approval",
    "Offer Released",
    "Offer Accepted",
    "Pre-Joining",
    "Joined",
    "Rejected",
    "Withdrawn",
    "On Hold",
]

BUSINESS_SEGMENTS = [
    "Intellecap Consulting",
    "Investment Banking - Debt",
    "Investment Banking - Equity",
    "Aavishkaar Capital",
    "Finance",
    "Human Resources",
    "Group Functions",
    "Internships",
]

SCORE_BUCKETS = {
    "strong": {"label": "Strong Fit", "min": 75.01, "action": "Proceed with outreach"},
    "potential": {"label": "Potential Fit", "min": 50.0, "action": "Recruiter review required"},
    "reject": {"label": "Reject", "min": 0.0, "action": "Do not progress unless overridden"},
}

OUTREACH_STATUSES = [
    "Outreach Pending",
    "Outreach Sent",
    "Follow-up 1 Due",
    "Follow-up 1 Sent",
    "Follow-up 2 Due",
    "Follow-up 2 Sent",
    "Responded - Interested",
    "Responded - Not Interested",
    "No Response",
    "Application Pending",
    "Applied",
]

VERIFICATION_STATUSES = [
    "Verified",
    "Partially Verified",
    "Unverified",
    "Invalid URL",
    "Duplicate",
]
