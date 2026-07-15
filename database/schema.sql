CREATE TABLE IF NOT EXISTS requisitions (
    requisition_id TEXT PRIMARY KEY,
    job_title TEXT NOT NULL,
    business_segment TEXT NOT NULL,
    location TEXT,
    hiring_manager TEXT,
    recruiter TEXT,
    experience_min REAL DEFAULT 0,
    experience_max REAL DEFAULT 40,
    mandatory_skills TEXT,
    preferred_skills TEXT,
    target_companies TEXT,
    job_description TEXT,
    application_link TEXT,
    status TEXT DEFAULT 'Open',
    created_at TEXT NOT NULL,
    target_closure_date TEXT
);

CREATE TABLE IF NOT EXISTS scoring_criteria (
    criteria_id TEXT PRIMARY KEY,
    requisition_id TEXT NOT NULL,
    criterion_name TEXT NOT NULL,
    weight REAL NOT NULL,
    criterion_type TEXT DEFAULT 'keyword',
    criterion_value TEXT,
    is_mandatory INTEGER DEFAULT 0,
    FOREIGN KEY(requisition_id) REFERENCES requisitions(requisition_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS candidates (
    candidate_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    linkedin_url TEXT,
    current_company TEXT,
    current_title TEXT,
    location TEXT,
    total_experience REAL DEFAULT 0,
    resume_path TEXT,
    resume_text TEXT,
    source TEXT,
    verification_status TEXT DEFAULT 'Unverified',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS applications (
    application_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    requisition_id TEXT NOT NULL,
    fit_score REAL DEFAULT 0,
    score_bucket TEXT,
    recommendation TEXT,
    suitability_reason TEXT,
    strengths TEXT,
    concerns TEXT,
    current_stage TEXT DEFAULT 'Sourced',
    application_status TEXT DEFAULT 'Active',
    override_decision TEXT,
    override_reason TEXT,
    applied_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(candidate_id, requisition_id),
    FOREIGN KEY(candidate_id) REFERENCES candidates(candidate_id),
    FOREIGN KEY(requisition_id) REFERENCES requisitions(requisition_id)
);

CREATE TABLE IF NOT EXISTS assessment_details (
    assessment_detail_id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL,
    criterion_name TEXT NOT NULL,
    weight REAL NOT NULL,
    awarded_score REAL NOT NULL,
    evidence TEXT,
    assessed_at TEXT NOT NULL,
    FOREIGN KEY(application_id) REFERENCES applications(application_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS stage_history (
    stage_history_id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL,
    previous_stage TEXT,
    new_stage TEXT NOT NULL,
    changed_by TEXT,
    change_reason TEXT,
    changed_at TEXT NOT NULL,
    FOREIGN KEY(application_id) REFERENCES applications(application_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS outreach (
    outreach_id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL,
    channel TEXT,
    message_type TEXT,
    subject TEXT,
    message_body TEXT,
    sent_status TEXT DEFAULT 'Draft',
    sent_at TEXT,
    follow_up_due_at TEXT,
    response_status TEXT,
    response_at TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(application_id) REFERENCES applications(application_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS interviews (
    interview_id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL,
    interview_stage TEXT,
    interview_date TEXT,
    interviewer_names TEXT,
    interview_status TEXT DEFAULT 'Scheduled',
    feedback_status TEXT DEFAULT 'Pending',
    recommendation TEXT,
    overall_rating REAL,
    feedback_notes TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(application_id) REFERENCES applications(application_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cas_versions (
    cas_id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL,
    version_number INTEGER NOT NULL,
    stage TEXT,
    cas_content TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    generated_by TEXT,
    file_path TEXT,
    FOREIGN KEY(application_id) REFERENCES applications(application_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS offers (
    offer_id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL UNIQUE,
    offer_status TEXT,
    proposed_ctc REAL,
    approved_ctc REAL,
    offer_date TEXT,
    acceptance_date TEXT,
    joining_date TEXT,
    actual_joining_date TEXT,
    drop_reason TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(application_id) REFERENCES applications(application_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reminders (
    reminder_id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL,
    reminder_type TEXT,
    recipient_type TEXT,
    recipient_email TEXT,
    due_at TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    sent_at TEXT,
    escalation_level INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    FOREIGN KEY(application_id) REFERENCES applications(application_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_log (
    audit_id TEXT PRIMARY KEY,
    user_id TEXT,
    action_type TEXT,
    entity_type TEXT,
    entity_id TEXT,
    old_value TEXT,
    new_value TEXT,
    action_timestamp TEXT NOT NULL
);
