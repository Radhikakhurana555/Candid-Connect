from __future__ import annotations

import re
from typing import Any

from utils.validators import clamp, split_lines


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def _terms(value: str) -> list[str]:
    return split_lines(value)


def _match_ratio(terms: list[str], haystack: str) -> tuple[float, list[str], list[str]]:
    if not terms:
        return 1.0, [], []
    text = _normalise(haystack)
    matched = [term for term in terms if _normalise(term) in text]
    missing = [term for term in terms if term not in matched]
    return len(matched) / len(terms), matched, missing


def get_bucket(score: float) -> tuple[str, str]:
    if score > 75:
        return "Strong Fit", "Proceed with outreach"
    if score >= 50:
        return "Potential Fit", "Recruiter review required"
    return "Reject", "Do not progress unless overridden"


def assess_candidate(application: dict[str, Any], criteria: list[dict[str, Any]]) -> dict[str, Any]:
    resume_text = " ".join(
        [
            application.get("resume_text", ""), application.get("current_title", ""),
            application.get("current_company", ""), application.get("location", ""),
        ]
    )
    details: list[dict[str, Any]] = []
    strengths: list[str] = []
    concerns: list[str] = []
    mandatory_failures: list[str] = []

    for criterion in criteria:
        name = criterion["criterion_name"]
        weight = float(criterion["weight"])
        ctype = criterion.get("criterion_type") or "keyword"
        value = criterion.get("criterion_value") or ""
        mandatory = bool(criterion.get("is_mandatory"))
        ratio = 0.0
        evidence = "No evidence found."

        if ctype == "experience":
            candidate_years = float(application.get("total_experience") or 0)
            try:
                required = float(value or application.get("experience_min") or 0)
            except ValueError:
                required = float(application.get("experience_min") or 0)
            ratio = min(candidate_years / required, 1.0) if required > 0 else 1.0
            evidence = f"Candidate experience: {candidate_years:g} years; benchmark: {required:g} years."
        elif ctype == "location":
            accepted = _terms(value) or [application.get("location", "")]
            ratio, matched, missing = _match_ratio(accepted, application.get("location", ""))
            evidence = f"Matched location: {', '.join(matched) or 'None'}; expected: {', '.join(accepted)}."
        else:
            terms = _terms(value)
            ratio, matched, missing = _match_ratio(terms, resume_text)
            evidence = f"Matched: {', '.join(matched) or 'None'}"
            if missing:
                evidence += f"; not evidenced: {', '.join(missing)}"

        awarded = round(weight * clamp(ratio, 0, 1), 2)
        details.append(
            {
                "criterion_name": name,
                "weight": weight,
                "awarded_score": awarded,
                "evidence": evidence,
            }
        )
        if ratio >= 0.7:
            strengths.append(f"{name}: {evidence}")
        elif ratio < 0.5:
            concerns.append(f"{name}: {evidence}")
            if mandatory:
                mandatory_failures.append(name)

    total_weight = sum(item["weight"] for item in details) or 1
    raw_score = sum(item["awarded_score"] for item in details)
    score = round((raw_score / total_weight) * 100, 1)
    bucket, recommendation = get_bucket(score)

    if mandatory_failures and bucket == "Strong Fit":
        bucket = "Potential Fit"
        recommendation = "Hold for recruiter validation of mandatory criteria"
        concerns.insert(0, f"Mandatory criteria requiring validation: {', '.join(mandatory_failures)}")

    reason = (
        f"The candidate achieved {score}/100 against the role-specific criteria and falls in the "
        f"{bucket} bucket. "
    )
    if strengths:
        reason += "Strongest alignment: " + "; ".join(strengths[:2]) + ". "
    if concerns:
        reason += "Key validation areas: " + "; ".join(concerns[:2]) + "."

    return {
        "fit_score": score,
        "score_bucket": bucket,
        "recommendation": recommendation,
        "suitability_reason": reason,
        "strengths": strengths,
        "concerns": concerns,
        "mandatory_failures": mandatory_failures,
        "details": details,
    }
