"""
Review Synthesizer - Phase 2

Aggregates findings from multiple code review assistants into:
- A weighted Vibe Score (0-100)
- A human-readable summary
- Actionable recommendations

Weighting:
  Security & Compliance: 3x (critical for enterprise)
  Performance: 2x
  Architecture & Testing: 1.5x
  Style & Documentation: 1x
"""

from typing import List, Dict, Any, Optional

# Domain weights for Vibe Score calculation
DOMAIN_WEIGHTS = {
    "security": 3.0,
    "pci-dss": 3.0,
    "gdpr": 3.0,
    "soc2": 3.0,
    "fhir": 3.0,
    "compliance": 3.0,
    "performance": 2.0,
    "caching": 2.0,
    "architecture": 1.5,
    "api-design": 1.5,
    "microservices": 1.5,
    "event-driven": 1.5,
    "testing": 1.5,
    "docker": 1.5,
    "kubernetes": 1.5,
    "database": 1.5,
    "react": 1.0,
    "accessibility": 1.0,
    "refactoring": 1.0,
    "code-review": 1.0,
    "ux-content": 1.0,
}

# Severity penalties (subtracted from base score of 100)
SEVERITY_PENALTIES = {
    "critical": 15,
    "high": 8,
    "medium": 3,
    "low": 1,
}


def compute_vibe_score(findings: List[Dict[str, Any]], assistants_used: List[str]) -> int:
    """
    Compute a Vibe Score (0-100) from review findings.

    Base score starts at 100. Each finding subtracts a penalty based on
    severity, weighted by the assistant's domain importance.
    """
    if not findings:
        return 100

    total_penalty = 0.0
    total_weight = 0.0

    for finding in findings:
        severity = finding.get("severity", "low")
        assistant = finding.get("assistant", "")

        # Determine weight from assistant domain
        weight = 1.0
        for domain, w in DOMAIN_WEIGHTS.items():
            if domain in assistant.lower():
                weight = w
                break

        penalty = SEVERITY_PENALTIES.get(severity, 1)
        total_penalty += penalty * weight
        total_weight += weight

    # Normalize: cap penalty so score stays in 0-100
    score = max(0, min(100, round(100 - total_penalty)))
    return score


def synthesize_findings(
    findings: List[Dict[str, Any]],
    assistants_used: List[str]
) -> Dict[str, Any]:
    """
    Synthesize review findings into a structured summary.

    Returns:
        {
            "vibe_score": int (0-100),
            "grade": str ("A+", "A", "B", "C", "D", "F"),
            "summary": str,
            "by_severity": {"critical": int, "high": int, "medium": int, "low": int},
            "by_assistant": {assistant_id: {"count": int, "worst_severity": str}},
            "top_issues": [{"title": str, "severity": str, "assistant": str}],
            "recommendations": [str],
        }
    """
    vibe_score = compute_vibe_score(findings, assistants_used)

    # Count by severity
    by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for f in findings:
        sev = f.get("severity", "low")
        if sev in by_severity:
            by_severity[sev] += 1

    # Group by assistant
    by_assistant: Dict[str, Dict[str, Any]] = {}
    for f in findings:
        aid = f.get("assistant", "unknown")
        if aid not in by_assistant:
            by_assistant[aid] = {"count": 0, "worst_severity": "low"}
        by_assistant[aid]["count"] += 1
        if _severity_rank(f.get("severity", "low")) > _severity_rank(by_assistant[aid]["worst_severity"]):
            by_assistant[aid]["worst_severity"] = f.get("severity", "low")

    # Top issues (critical and high, sorted by severity)
    top_issues = sorted(
        [{"title": f.get("title", ""), "severity": f.get("severity", "low"), "assistant": f.get("assistant", "")}
         for f in findings if f.get("severity") in ("critical", "high")],
        key=lambda x: _severity_rank(x["severity"]),
        reverse=True
    )[:5]

    # Grade
    grade = _score_to_grade(vibe_score)

    # Summary text
    total = len(findings)
    summary = _build_summary(total, by_severity, grade, assistants_used)

    # Recommendations
    recommendations = _build_recommendations(by_severity, by_assistant)

    return {
        "vibe_score": vibe_score,
        "grade": grade,
        "summary": summary,
        "by_severity": by_severity,
        "by_assistant": by_assistant,
        "top_issues": top_issues,
        "recommendations": recommendations,
    }


def _severity_rank(severity: str) -> int:
    return {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(severity, 0)


def _score_to_grade(score: int) -> str:
    if score >= 95:
        return "A+"
    elif score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    return "F"


def _build_summary(total: int, by_severity: Dict, grade: str, assistants: List[str]) -> str:
    parts = []
    if total == 0:
        return f"Clean build. {len(assistants)} assistants found no issues. Grade: {grade}."

    parts.append(f"{total} finding{'s' if total != 1 else ''} from {len(assistants)} assistant{'s' if len(assistants) != 1 else ''}")

    issues = []
    if by_severity["critical"]:
        issues.append(f"{by_severity['critical']} critical")
    if by_severity["high"]:
        issues.append(f"{by_severity['high']} high")
    if by_severity["medium"]:
        issues.append(f"{by_severity['medium']} medium")
    if by_severity["low"]:
        issues.append(f"{by_severity['low']} low")

    if issues:
        parts.append(f"({', '.join(issues)})")

    parts.append(f"Grade: {grade}.")

    if by_severity["critical"] > 0:
        parts.append("Critical issues must be resolved before approval.")
    elif by_severity["high"] > 0:
        parts.append("High-priority issues should be addressed.")

    return " ".join(parts)


def _build_recommendations(by_severity: Dict, by_assistant: Dict) -> List[str]:
    recs = []
    if by_severity["critical"] > 0:
        recs.append("Fix all critical issues before proceeding to approval")
    if by_severity["high"] > 2:
        recs.append("Multiple high-severity issues detected -- consider a focused remediation pass")

    # Domain-specific recommendations
    for assistant, data in by_assistant.items():
        if data["worst_severity"] in ("critical", "high") and data["count"] >= 3:
            domain = assistant.replace("enhanced_", "").replace("_", " ").title()
            recs.append(f"{domain} review flagged {data['count']} issues -- this area needs attention")

    if not recs:
        recs.append("Code quality is good. Proceed to stakeholder approval.")

    return recs
