from typing import Any

from django.db import migrations

RISK_DEFINITIONS = [
    {
        "risk_code": "NO_FC_ASSIGNED",
        "module": "Payment Operations",
        "name": "No FC Assigned",
        "category": "fiduciary",
        "default_severity": "critical",
        "description": "Approved payment plans without a valid Fund Commitment recorded.",
        "threshold": "Flag when the number is greater than zero.",
    },
    {
        "risk_code": "EXCEEDED_DISPERSION_DATE",
        "module": "Payment Operations",
        "name": "Exceeded Dispersion Date",
        "category": "operational",
        "default_severity": "warning",
        "description": "Payment plans past their defined dispersion end date.",
        "threshold": "Country configurable.",
    },
    {
        "risk_code": "LOW_RECONCILIATION_RATE",
        "module": "Payment Reconciliation",
        "name": "<40% Reconciliation",
        "category": "fiduciary",
        "default_severity": "caution",
        "description": "Payment plans with a reconciliation rate below 40%.",
        "threshold": "Country configurable.",
    },
    {
        "risk_code": "EXCEEDING_RECONCILIATION_WINDOW",
        "module": "Payment Reconciliation",
        "name": "Exceeding Reconciliation Window",
        "category": "fiduciary",
        "default_severity": "normal",
        "description": "Payment plans past their defined reconciliation deadline.",
        "threshold": "Country configurable.",
    },
    {
        "risk_code": "NOT_READY_FOR_PAYMENT",
        "module": "Targeting",
        "name": "Not Ready for Payment",
        "category": "operational",
        "default_severity": "caution",
        "description": "Payment readiness issues (draft or TP open).",
        "threshold": "Country configurable.",
    },
    {
        "risk_code": "ACTIVE_ADJUDICATION_TICKETS",
        "module": "Payment Operations",
        "name": "Active Adjudication Tickets",
        "category": "fiduciary",
        "default_severity": "caution",
        "description": "Payments for individuals with open adjudication tickets.",
        "threshold": "Country configurable.",
    },
    {
        "risk_code": "UNFINISHED_VERIFICATION_PLANS",
        "module": "Verification",
        "name": "Unfinished Verification Plans",
        "category": "fiduciary",
        "default_severity": "warning",
        "description": "Payment verification plans not completed.",
        "threshold": "Country configurable.",
    },
    {
        "risk_code": "HIGH_FAILED_VERIFICATION_RATE",
        "module": "Verification",
        "name": ">30% Failed Verification",
        "category": "fiduciary",
        "default_severity": "critical",
        "description": "High payment verification failure rate.",
        "threshold": "Country configurable.",
    },
    {
        "risk_code": "MISSING_ID_DOCUMENTS",
        "module": "Registration",
        "name": "Missing ID Documents",
        "category": "compliance",
        "default_severity": "critical",
        "description": "Individuals registered without identity documents.",
        "threshold": "Country configurable.",
    },
    {
        "risk_code": "POSSIBLE_DUPLICATES",
        "module": "Population",
        "name": "Possible Duplicates",
        "category": "fiduciary",
        "default_severity": "critical",
        "description": "Records flagged as potential duplicates requiring manual review.",
        "threshold": "Country configurable.",
    },
    {
        "risk_code": "PENDING_MERGE_5D",
        "module": "Registration",
        "name": "Pending Merge >5 Days",
        "category": "operational",
        "default_severity": "warning",
        "description": "Records awaiting deduplication merge for more than 5 days.",
        "threshold": "Country configurable.",
    },
    {
        "risk_code": "RDIS_WITH_ERRORS",
        "module": "Registration",
        "name": "RDIs with Errors",
        "category": "operational",
        "default_severity": "critical",
        "description": "Registration Data Imports containing validation errors.",
        "threshold": "Flag when the number is greater than zero.",
    },
    {
        "risk_code": "UNRESOLVED_GRIEVANCES_30D",
        "module": "Grievance",
        "name": "Unresolved >30 Days",
        "category": "compliance",
        "default_severity": "critical",
        "description": "Complaints that remain unresolved beyond the 30-day SLA.",
        "threshold": "Country configurable.",
    },
    {
        "risk_code": "UNASSIGNED_CASES",
        "module": "Grievance",
        "name": "Unassigned Cases",
        "category": "operational",
        "default_severity": "warning",
        "description": "Grievances submitted but not yet assigned.",
        "threshold": "Country configurable.",
    },
]


def seed_risk_definitions(apps: Any, schema_editor: Any) -> None:
    RiskDefinition = apps.get_model("analysis", "RiskDefinition")
    for data in RISK_DEFINITIONS:
        RiskDefinition.objects.update_or_create(risk_code=data["risk_code"], defaults=data)


def unseed_risk_definitions(apps: Any, schema_editor: Any) -> None:
    RiskDefinition = apps.get_model("analysis", "RiskDefinition")
    RiskDefinition.objects.filter(risk_code__in=[d["risk_code"] for d in RISK_DEFINITIONS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("analysis", "0008_risk_program_and_catalog"),
    ]

    operations = [
        migrations.RunPython(seed_risk_definitions, unseed_risk_definitions),
    ]
