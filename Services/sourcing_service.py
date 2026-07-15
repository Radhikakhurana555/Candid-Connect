from __future__ import annotations

from utils.validators import split_lines


def build_sourcing_strategy(requisition: dict) -> dict:
    skills = split_lines(requisition.get("mandatory_skills", ""))
    preferred = split_lines(requisition.get("preferred_skills", ""))
    companies = split_lines(requisition.get("target_companies", ""))
    title = requisition.get("job_title", "")
    location = requisition.get("location", "")

    title_terms = [title]
    if "manager" in title.lower():
        title_terms.extend(["Senior Manager", "Associate Director"])
    if "associate" in title.lower():
        title_terms.extend(["Senior Associate", "Assistant Manager"])

    quoted_titles = " OR ".join(f'"{item}"' for item in dict.fromkeys(title_terms) if item)
    quoted_skills = " OR ".join(f'"{item}"' for item in skills)
    quoted_companies = " OR ".join(f'"{item}"' for item in companies)

    boolean_parts = []
    if quoted_titles:
        boolean_parts.append(f"({quoted_titles})")
    if quoted_skills:
        boolean_parts.append(f"({quoted_skills})")
    if quoted_companies:
        boolean_parts.append(f"({quoted_companies})")
    if location:
        boolean_parts.append(f'"{location}"')

    linkedin_boolean = " AND ".join(boolean_parts)
    google_query = f'site:linkedin.com/in {linkedin_boolean}'.strip()

    return {
        "primary_titles": list(dict.fromkeys(title_terms)),
        "mandatory_keywords": skills,
        "optional_keywords": preferred,
        "target_companies": companies,
        "linkedin_boolean": linkedin_boolean,
        "google_xray_query": google_query,
        "note": "Use these strings in authorised LinkedIn Recruiter or public search workflows. The app does not scrape LinkedIn.",
    }
