from __future__ import annotations

from database.db import fetch_all, fetch_one


def safe_percentage(numerator: int | float, denominator: int | float) -> float:
    return round((numerator / denominator) * 100, 1) if denominator else 0.0


def dashboard_metrics() -> dict:
    counts = fetch_one(
        """
        SELECT
            (SELECT COUNT(*) FROM requisitions WHERE status = 'Open') AS open_positions,
            (SELECT COUNT(*) FROM applications WHERE application_status = 'Active') AS active_candidates,
            (SELECT COUNT(*) FROM interviews WHERE interview_status = 'Scheduled') AS scheduled_interviews,
            (SELECT COUNT(*) FROM offers WHERE offer_status IN ('Draft', 'Approval Pending', 'Released')) AS offers_in_progress,
            (SELECT COUNT(*) FROM reminders WHERE status = 'Pending' AND due_at <= datetime('now')) AS overdue_reminders
        """
    ) or {}
    return counts


def funnel_counts() -> dict:
    total = fetch_one("SELECT COUNT(*) AS count FROM applications") or {"count": 0}
    contacted = fetch_one(
        "SELECT COUNT(DISTINCT application_id) AS count FROM outreach WHERE sent_status = 'Sent'"
    ) or {"count": 0}
    interviewed = fetch_one(
        "SELECT COUNT(DISTINCT application_id) AS count FROM interviews WHERE interview_status = 'Completed'"
    ) or {"count": 0}
    offers = fetch_one(
        "SELECT COUNT(*) AS count FROM offers WHERE offer_status IN ('Released', 'Accepted', 'Joined')"
    ) or {"count": 0}
    joined = fetch_one(
        "SELECT COUNT(*) AS count FROM applications WHERE current_stage = 'Joined'"
    ) or {"count": 0}
    return {
        "Sourced": total["count"],
        "Contacted": contacted["count"],
        "Interviewed": interviewed["count"],
        "Offered": offers["count"],
        "Joined": joined["count"],
    }


def conversion_metrics() -> dict:
    funnel = funnel_counts()
    return {
        "Sourced to Interview": safe_percentage(funnel["Interviewed"], funnel["Sourced"]),
        "Interview to Offer": safe_percentage(funnel["Offered"], funnel["Interviewed"]),
        "Offer to Joining": safe_percentage(funnel["Joined"], funnel["Offered"]),
        "Sourcing to Joining": safe_percentage(funnel["Joined"], funnel["Sourced"]),
    }


def hires_by_segment() -> list[dict]:
    return fetch_all(
        """
        SELECT r.business_segment, COUNT(*) AS hires
        FROM applications a
        JOIN requisitions r ON r.requisition_id = a.requisition_id
        WHERE a.current_stage = 'Joined'
        GROUP BY r.business_segment
        ORDER BY hires DESC
        """
    )


def rejections_by_stage() -> list[dict]:
    return fetch_all(
        """
        SELECT COALESCE(previous_stage, 'Unknown') AS stage, COUNT(*) AS rejected
        FROM stage_history
        WHERE new_stage = 'Rejected'
        GROUP BY previous_stage
        ORDER BY rejected DESC
        """
    )
