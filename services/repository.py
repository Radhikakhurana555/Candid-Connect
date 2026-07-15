from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from database.db import execute, fetch_all, fetch_one

REPOSITORY_PATCH_VERSION = "2026-07-15-v2"

__all__ = [
    "create_requisition",
    "find_duplicate_requisition",
    "list_requisitions",
    "get_requisition",
    "get_criteria",
    "create_candidate",
    "find_duplicate_candidate",
    "find_candidate_by_linkedin",
    "list_candidates",
    "create_application",
    "list_applications",
    "get_application",
    "save_assessment",
    "get_assessment_details",
    "record_stage_change",
    "update_application_stage",
    "list_stage_history",
    "save_outreach",
    "list_outreach",
    "schedule_interview",
    "list_interviews",
    "save_interview_feedback",
    "save_cas",
    "list_cas_versions",
    "upsert_offer",
    "list_offers",
    "get_offer",
    "create_reminder",
    "list_reminders",
    "mark_reminder_done",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:10].upper()}"


def create_requisition(payload: dict[str, Any], criteria: list[dict[str, Any]]) -> str:
    req_id = new_id("REQ")
    execute(
        """
        INSERT INTO requisitions (
            requisition_id, job_title, business_segment, location, hiring_manager,
            recruiter, experience_min, experience_max, mandatory_skills,
            preferred_skills, target_companies, job_description, application_link,
            status, created_at, target_closure_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            req_id, payload["job_title"], payload["business_segment"], payload.get("location"),
            payload.get("hiring_manager"), payload.get("recruiter"), payload.get("experience_min", 0),
            payload.get("experience_max", 40), payload.get("mandatory_skills", ""),
            payload.get("preferred_skills", ""), payload.get("target_companies", ""),
            payload.get("job_description", ""), payload.get("application_link", ""),
            payload.get("status", "Open"), now_iso(), payload.get("target_closure_date"),
        ),
    )
    for criterion in criteria:
        execute(
            """
            INSERT INTO scoring_criteria (
                criteria_id, requisition_id, criterion_name, weight,
                criterion_type, criterion_value, is_mandatory
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                new_id("CRT"), req_id, criterion["criterion_name"], criterion["weight"],
                criterion.get("criterion_type", "keyword"), criterion.get("criterion_value", ""),
                1 if criterion.get("is_mandatory") else 0,
            ),
        )
    return req_id



def find_duplicate_requisition(
    job_title: str,
    business_segment: str,
    location: str | None = None,
) -> dict[str, Any] | None:
    """Return an existing open requisition with the same core identity."""
    return fetch_one(
        """
        SELECT *
        FROM requisitions
        WHERE LOWER(TRIM(job_title)) = LOWER(TRIM(?))
          AND LOWER(TRIM(business_segment)) = LOWER(TRIM(?))
          AND LOWER(TRIM(COALESCE(location, ''))) =
              LOWER(TRIM(COALESCE(?, '')))
          AND status = 'Open'
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (job_title, business_segment, location or ""),
    )

def list_requisitions(open_only: bool = False) -> list[dict[str, Any]]:
    query = "SELECT * FROM requisitions"
    params: tuple[Any, ...] = ()
    if open_only:
        query += " WHERE status = ?"
        params = ("Open",)
    query += " ORDER BY created_at DESC"
    return fetch_all(query, params)


def get_requisition(req_id: str) -> dict[str, Any] | None:
    return fetch_one("SELECT * FROM requisitions WHERE requisition_id = ?", (req_id,))


def get_criteria(req_id: str) -> list[dict[str, Any]]:
    return fetch_all(
        "SELECT * FROM scoring_criteria WHERE requisition_id = ? ORDER BY rowid",
        (req_id,),
    )


def create_candidate(payload: dict[str, Any]) -> str:
    candidate_id = new_id("CAN")
    execute(
        """
        INSERT INTO candidates (
            candidate_id, full_name, email, phone, linkedin_url, current_company,
            current_title, location, total_experience, resume_path, resume_text,
            source, verification_status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            candidate_id, payload["full_name"], payload.get("email"), payload.get("phone"),
            payload.get("linkedin_url"), payload.get("current_company"), payload.get("current_title"),
            payload.get("location"), payload.get("total_experience", 0), payload.get("resume_path"),
            payload.get("resume_text", ""), payload.get("source", "Manual"),
            payload.get("verification_status", "Unverified"), now_iso(),
        ),
    )
    return candidate_id



def find_duplicate_candidate(
    email: str | None = None,
    phone: str | None = None,
    linkedin_url: str | None = None,
    full_name: str | None = None,
    current_company: str | None = None,
) -> dict[str, Any] | None:
    """Find a candidate by LinkedIn, email, phone, or name/company."""
    if linkedin_url and linkedin_url.strip():
        match = fetch_one(
            """
            SELECT * FROM candidates
            WHERE LOWER(TRIM(linkedin_url)) = LOWER(TRIM(?))
            LIMIT 1
            """,
            (linkedin_url.strip(),),
        )
        if match:
            return match

    if email and email.strip():
        match = fetch_one(
            """
            SELECT * FROM candidates
            WHERE LOWER(TRIM(email)) = LOWER(TRIM(?))
            LIMIT 1
            """,
            (email.strip(),),
        )
        if match:
            return match

    if phone and phone.strip():
        incoming_phone = "".join(ch for ch in phone if ch.isdigit())
        if incoming_phone:
            for candidate in fetch_all(
                "SELECT * FROM candidates WHERE phone IS NOT NULL AND TRIM(phone) != ''"
            ):
                stored_phone = "".join(
                    ch for ch in (candidate.get("phone") or "") if ch.isdigit()
                )
                if stored_phone == incoming_phone:
                    return candidate

    if full_name and full_name.strip() and current_company and current_company.strip():
        match = fetch_one(
            """
            SELECT * FROM candidates
            WHERE LOWER(TRIM(full_name)) = LOWER(TRIM(?))
              AND LOWER(TRIM(COALESCE(current_company, ''))) = LOWER(TRIM(?))
            LIMIT 1
            """,
            (full_name.strip(), current_company.strip()),
        )
        if match:
            return match

    return None

def find_candidate_by_linkedin(url: str) -> dict[str, Any] | None:
    return fetch_one("SELECT * FROM candidates WHERE linkedin_url = ?", (url,))


def list_candidates() -> list[dict[str, Any]]:
    return fetch_all("SELECT * FROM candidates ORDER BY created_at DESC")


def create_application(candidate_id: str, req_id: str) -> str:
    existing = fetch_one(
        "SELECT application_id FROM applications WHERE candidate_id = ? AND requisition_id = ?",
        (candidate_id, req_id),
    )
    if existing:
        return existing["application_id"]
    app_id = new_id("APP")
    timestamp = now_iso()
    execute(
        """
        INSERT INTO applications (
            application_id, candidate_id, requisition_id, current_stage,
            application_status, created_at, updated_at
        ) VALUES (?, ?, ?, 'Sourced', 'Active', ?, ?)
        """,
        (app_id, candidate_id, req_id, timestamp, timestamp),
    )
    record_stage_change(app_id, None, "Sourced", "System", "Application created")
    return app_id


def list_applications(req_id: str | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT a.*, c.full_name, c.email, c.linkedin_url, c.current_company,
               c.current_title, c.location, c.total_experience, c.verification_status,
               r.job_title, r.business_segment, r.hiring_manager, r.application_link
        FROM applications a
        JOIN candidates c ON c.candidate_id = a.candidate_id
        JOIN requisitions r ON r.requisition_id = a.requisition_id
    """
    params: tuple[Any, ...] = ()
    if req_id:
        query += " WHERE a.requisition_id = ?"
        params = (req_id,)
    query += " ORDER BY a.updated_at DESC"
    return fetch_all(query, params)


def get_application(app_id: str) -> dict[str, Any] | None:
    return fetch_one(
        """
        SELECT a.*, c.*, r.job_title, r.business_segment, r.hiring_manager,
               r.recruiter, r.job_description, r.application_link,
               r.mandatory_skills, r.preferred_skills, r.target_companies,
               r.experience_min, r.experience_max
        FROM applications a
        JOIN candidates c ON c.candidate_id = a.candidate_id
        JOIN requisitions r ON r.requisition_id = a.requisition_id
        WHERE a.application_id = ?
        """,
        (app_id,),
    )


def save_assessment(app_id: str, result: dict[str, Any]) -> None:
    execute("DELETE FROM assessment_details WHERE application_id = ?", (app_id,))
    for item in result["details"]:
        execute(
            """
            INSERT INTO assessment_details (
                assessment_detail_id, application_id, criterion_name, weight,
                awarded_score, evidence, assessed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                new_id("ASD"), app_id, item["criterion_name"], item["weight"],
                item["awarded_score"], item["evidence"], now_iso(),
            ),
        )
    execute(
        """
        UPDATE applications SET fit_score = ?, score_bucket = ?, recommendation = ?,
            suitability_reason = ?, strengths = ?, concerns = ?, updated_at = ?
        WHERE application_id = ?
        """,
        (
            result["fit_score"], result["score_bucket"], result["recommendation"],
            result["suitability_reason"], json.dumps(result["strengths"]),
            json.dumps(result["concerns"]), now_iso(), app_id,
        ),
    )


def get_assessment_details(app_id: str) -> list[dict[str, Any]]:
    return fetch_all(
        "SELECT * FROM assessment_details WHERE application_id = ? ORDER BY rowid",
        (app_id,),
    )


def record_stage_change(app_id: str, previous: str | None, new: str, changed_by: str, reason: str) -> None:
    execute(
        """
        INSERT INTO stage_history (
            stage_history_id, application_id, previous_stage, new_stage,
            changed_by, change_reason, changed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (new_id("STG"), app_id, previous, new, changed_by, reason, now_iso()),
    )


def update_stage(app_id: str, new_stage: str, changed_by: str, reason: str) -> None:
    current = fetch_one("SELECT current_stage FROM applications WHERE application_id = ?", (app_id,))
    if not current:
        raise ValueError("Application not found")
    previous = current["current_stage"]
    execute(
        "UPDATE applications SET current_stage = ?, updated_at = ? WHERE application_id = ?",
        (new_stage, now_iso(), app_id),
    )
    record_stage_change(app_id, previous, new_stage, changed_by, reason)


def get_stage_history(app_id: str) -> list[dict[str, Any]]:
    return fetch_all(
        "SELECT * FROM stage_history WHERE application_id = ? ORDER BY changed_at DESC",
        (app_id,),
    )


def save_outreach(payload: dict[str, Any]) -> str:
    outreach_id = new_id("OUT")
    execute(
        """
        INSERT INTO outreach (
            outreach_id, application_id, channel, message_type, subject,
            message_body, sent_status, sent_at, follow_up_due_at,
            response_status, response_at, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            outreach_id, payload["application_id"], payload.get("channel"), payload.get("message_type"),
            payload.get("subject"), payload.get("message_body"), payload.get("sent_status", "Draft"),
            payload.get("sent_at"), payload.get("follow_up_due_at"), payload.get("response_status"),
            payload.get("response_at"), now_iso(),
        ),
    )
    return outreach_id


def list_outreach(app_id: str | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT o.*, c.full_name, r.job_title
        FROM outreach o
        JOIN applications a ON a.application_id = o.application_id
        JOIN candidates c ON c.candidate_id = a.candidate_id
        JOIN requisitions r ON r.requisition_id = a.requisition_id
    """
    params: tuple[Any, ...] = ()
    if app_id:
        query += " WHERE o.application_id = ?"
        params = (app_id,)
    query += " ORDER BY o.created_at DESC"
    return fetch_all(query, params)


def save_interview(payload: dict[str, Any]) -> str:
    interview_id = new_id("INT")
    execute(
        """
        INSERT INTO interviews (
            interview_id, application_id, interview_stage, interview_date,
            interviewer_names, interview_status, feedback_status,
            recommendation, overall_rating, feedback_notes, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            interview_id, payload["application_id"], payload.get("interview_stage"),
            payload.get("interview_date"), payload.get("interviewer_names"),
            payload.get("interview_status", "Scheduled"), payload.get("feedback_status", "Pending"),
            payload.get("recommendation"), payload.get("overall_rating"),
            payload.get("feedback_notes"), now_iso(),
        ),
    )
    return interview_id


def list_interviews(app_id: str | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT i.*, c.full_name, r.job_title
        FROM interviews i
        JOIN applications a ON a.application_id = i.application_id
        JOIN candidates c ON c.candidate_id = a.candidate_id
        JOIN requisitions r ON r.requisition_id = a.requisition_id
    """
    params: tuple[Any, ...] = ()
    if app_id:
        query += " WHERE i.application_id = ?"
        params = (app_id,)
    query += " ORDER BY i.interview_date DESC"
    return fetch_all(query, params)


def update_interview_feedback(interview_id: str, payload: dict[str, Any]) -> None:
    execute(
        """
        UPDATE interviews SET interview_status = ?, feedback_status = ?, recommendation = ?,
            overall_rating = ?, feedback_notes = ? WHERE interview_id = ?
        """,
        (
            payload.get("interview_status", "Completed"), payload.get("feedback_status", "Submitted"),
            payload.get("recommendation"), payload.get("overall_rating"),
            payload.get("feedback_notes"), interview_id,
        ),
    )


def save_cas(app_id: str, stage: str, content: str, generated_by: str, file_path: str | None = None) -> int:
    existing = fetch_one(
        "SELECT COALESCE(MAX(version_number), 0) AS version FROM cas_versions WHERE application_id = ?",
        (app_id,),
    )
    version = int(existing["version"]) + 1
    execute(
        """
        INSERT INTO cas_versions (
            cas_id, application_id, version_number, stage, cas_content,
            generated_at, generated_by, file_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (new_id("CAS"), app_id, version, stage, content, now_iso(), generated_by, file_path),
    )
    return version


def list_cas_versions(app_id: str) -> list[dict[str, Any]]:
    return fetch_all(
        "SELECT * FROM cas_versions WHERE application_id = ? ORDER BY version_number DESC",
        (app_id,),
    )


def upsert_offer(app_id: str, payload: dict[str, Any]) -> None:
    existing = fetch_one("SELECT offer_id FROM offers WHERE application_id = ?", (app_id,))
    if existing:
        execute(
            """
            UPDATE offers SET offer_status = ?, proposed_ctc = ?, approved_ctc = ?,
                offer_date = ?, acceptance_date = ?, joining_date = ?, actual_joining_date = ?,
                drop_reason = ?, updated_at = ? WHERE application_id = ?
            """,
            (
                payload.get("offer_status"), payload.get("proposed_ctc"), payload.get("approved_ctc"),
                payload.get("offer_date"), payload.get("acceptance_date"), payload.get("joining_date"),
                payload.get("actual_joining_date"), payload.get("drop_reason"), now_iso(), app_id,
            ),
        )
    else:
        execute(
            """
            INSERT INTO offers (
                offer_id, application_id, offer_status, proposed_ctc, approved_ctc,
                offer_date, acceptance_date, joining_date, actual_joining_date,
                drop_reason, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                new_id("OFF"), app_id, payload.get("offer_status"), payload.get("proposed_ctc"),
                payload.get("approved_ctc"), payload.get("offer_date"), payload.get("acceptance_date"),
                payload.get("joining_date"), payload.get("actual_joining_date"),
                payload.get("drop_reason"), now_iso(),
            ),
        )


def list_offers() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT o.*, c.full_name, r.job_title, r.business_segment
        FROM offers o
        JOIN applications a ON a.application_id = o.application_id
        JOIN candidates c ON c.candidate_id = a.candidate_id
        JOIN requisitions r ON r.requisition_id = a.requisition_id
        ORDER BY o.updated_at DESC
        """
    )


def get_offer(app_id: str) -> dict[str, Any] | None:
    return fetch_one("SELECT * FROM offers WHERE application_id = ?", (app_id,))


def create_reminder(payload: dict[str, Any]) -> str:
    reminder_id = new_id("REM")
    execute(
        """
        INSERT INTO reminders (
            reminder_id, application_id, reminder_type, recipient_type,
            recipient_email, due_at, status, escalation_level, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            reminder_id, payload["application_id"], payload.get("reminder_type"),
            payload.get("recipient_type"), payload.get("recipient_email"), payload["due_at"],
            payload.get("status", "Pending"), payload.get("escalation_level", 0), now_iso(),
        ),
    )
    return reminder_id


def list_reminders() -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT rm.*, c.full_name, r.job_title
        FROM reminders rm
        JOIN applications a ON a.application_id = rm.application_id
        JOIN candidates c ON c.candidate_id = a.candidate_id
        JOIN requisitions r ON r.requisition_id = a.requisition_id
        ORDER BY rm.due_at
        """
    )


def mark_reminder_done(reminder_id: str) -> None:
    execute("UPDATE reminders SET status = 'Completed' WHERE reminder_id = ?", (reminder_id,))
