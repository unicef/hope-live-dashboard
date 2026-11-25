"""Definitions and calculation notes for dashboard charts.

The strings are rendered by ``includes/chart_info.html`` through the
``chart_info`` template tag. Keeping them here avoids duplicating the same
explanation in several templates and gives xgettext one place to extract from.
"""

from django.utils.translation import gettext_lazy as _

CHART_INFO = {
    # ------------------------------------------------------------------
    # Financial
    # ------------------------------------------------------------------
    "financial.timeline": {
        "definition": _("Cash disbursed or payments over time, using the selected metric and chart filters."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Payments are dated by delivery date, then entitlement date, then status date. "
            "Only payments in accepted, finished or closed payment plans are included; failed, "
            "removed and conflicted payments are excluded. USD uses delivered quantity when "
            "present, otherwise entitlement quantity. Payments count counts payment records."
        ),
        "note": _(
            "The metric toggle switches between USD and payment count. The selected programme "
            "cohort and chart filters apply. Quantity (QTY) is retained for reconciliation and "
            "is not displayed as a separate metric on this page."
        ),
    },
    "financial.pipeline": {
        "definition": _("Payment pipeline from total payment volume through delivered to reconciled."),
        "source": _("HOPE payments and the completion reconciliation rate."),
        "method": _(
            "In pipeline is the total payment volume for the active metric — the funnel's "
            "starting population, not only pending payments. Delivered counts Distribution "
            "Successful, Partially Distributed and Transaction Successful. Reconciled is "
            "delivered multiplied by the reconciliation rate from the completion dataset for the "
            "same period and cohort."
        ),
        "note": _(
            "Pending in pipeline is shown below the chart as a subset of in-pipeline, not as a separate failure stage."
        ),
    },
    "financial.sector": {
        "definition": _("Cash disbursed or payments by programme sector."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Payment rows are grouped by programme sector using the same date and status filters "
            "as the financial timeline. USD uses delivered quantity when present, otherwise "
            "entitlement quantity; payments count counts payment records."
        ),
    },
    "financial.delivery": {
        "definition": _("Cash disbursed or payments by delivery mechanism."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Payment rows are grouped by the delivery mechanism name using the same date and "
            "status filters as the financial timeline."
        ),
    },
    "financial.region": {
        "definition": _("Cash disbursed or payments by UNICEF region."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Payment rows are grouped by the business area region name using the same date and "
            "status filters as the financial timeline."
        ),
        "note": _(
            "Bars are ordered by value and shaded from dark (highest) to light (lowest). Axis "
            "abbreviations are defined in the footnote below the chart; full region names appear "
            "in the tooltip."
        ),
    },
    "financial.country": {
        "definition": _("Cash disbursed (paid) or payments by country."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Payment rows are grouped by the business area country slug using the same date and "
            "status filters as the financial timeline."
        ),
        "note": _(
            "All countries with financial data in the period are shown. Outstanding by country is shown beside it."
        ),
    },
    "financial.program": {
        "definition": _("Cash disbursed or payments by programme."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Payment rows are grouped by programme name using the same date and status filters as "
            "the financial timeline."
        ),
        "note": _("The chart shows the top 10 programmes, plus an Other bucket."),
    },
    "financial.fsp": {
        "definition": _("Cash disbursed or payments by financial service provider."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Payment rows are grouped by financial service provider name using the same date and "
            "status filters as the financial timeline."
        ),
        "note": _("The chart shows the top 10 providers, plus an Other bucket."),
    },
    "financial.outstanding_country": {
        "definition": _("Outstanding payment amount by country, in USD."),
        "source": _("HOPE payments — country report financial feed (status dimension)."),
        "method": _(
            "Sums the entitlement quantity in USD for payments still in pending statuses "
            "(SENT TO PAYMENT GATEWAY, SENT TO FSP, PENDING), grouped by country. Payments in "
            "successful statuses have already been paid and are excluded."
        ),
        "note": _(
            "Always shown in USD, independent of the amount/payment-count toggle. All countries "
            "with outstanding amounts are shown."
        ),
    },
    "financial.implementing_partner": {
        "definition": _("Cash disbursed or payments by implementing partner."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Payment rows are grouped by the programme's implementing partner using the same "
            "date and status filters as the financial timeline."
        ),
        "note": _(
            "The card appears once the financial feed provides the implementing-partner "
            "dimension. Top 10 partners plus an Other bucket."
        ),
    },
    # ------------------------------------------------------------------
    # Demographic
    # ------------------------------------------------------------------
    "demographic.reached": {
        "definition": _("People reached in households with at least one qualifying payment in the period."),
        "source": _("HOPE households and payments — country report demographic feed."),
        "method": _(
            "A household counts once per period when it has a qualifying payment. Individuals, "
            "children and persons with disabilities come from the household's recorded "
            "composition. Date basis: payment delivery date, then entitlement date, then payment "
            "status date. Only accepted, finished or closed plans are included; failed, removed, "
            "conflicted and excluded payments are excluded."
        ),
        "note": _(
            "Children and PWD figures rely on recorded household fields, so missing composition "
            "or dates of birth understate the totals."
        ),
    },
    "demographic.children": {
        "definition": _("Children reached in households with at least one qualifying payment in the period."),
        "source": _("HOPE households and payments — country report demographic feed."),
        "method": _(
            "Sums each household's recorded children count (the household composition count "
            "where available, otherwise the beneficiary-recorded children count). Households "
            "with no recorded count contribute zero."
        ),
        "note": _(
            "Where household composition has not been recalculated or children's dates of birth "
            "are missing, the figure is understated. An improved estimate based on household "
            "members is being added to the feed."
        ),
    },
    "demographic.timeline": {
        "definition": _("Individuals, households, children or persons with disabilities reached over time."),
        "source": _("HOPE household, social-worker and payment data — country report demographic feed."),
        "method": _(
            "Metrics are calculated from payees with at least one qualifying payment in the "
            "selected period. Qualifying payments must belong to accepted, finished or closed "
            "payment plans; failed, removed, conflicted and excluded payments are not included. "
            "For household payees, individuals, children and persons with disabilities are "
            "derived from the recorded household composition. For social-worker payees, one "
            "record represents one worker, so the beneficiary count is the workforce count and "
            "household, child and disability metrics do not apply. Organisation payees are "
            "included only where payee-level demographic data is available. Date basis: payment "
            "delivery date, then entitlement date, then payment status date."
        ),
        "note": _(
            "Under the current legacy calculation, a household with more than one qualifying "
            "payment in a month can contribute its size, children and PWD counts once per "
            "payment; total households remains distinct. Missing composition or dates of birth "
            "understate the totals, and PWD figures may be under-reported where programmes do "
            "not collect them."
        ),
    },
    "demographic.sector": {
        "definition": _("Share of the reached population by programme sector."),
        "source": _("HOPE household, social-worker and payment data — country report demographic feed."),
        "method": _(
            "Uses the same payee and qualifying-payment base as the reach timeline, grouped by "
            "programme sector. Shares are calculated from the active metric (individuals, "
            "households, children or persons with disabilities). Household metrics use recorded "
            "composition; social-worker programmes report workforce counts separately."
        ),
        "note": _("Children and PWD under-reporting caveats also apply here."),
    },
    "demographic.country": {
        "definition": _("Share of the reached population by country."),
        "source": _("HOPE household, social-worker and payment data — country report demographic feed."),
        "method": _(
            "Uses the same payee and qualifying-payment base as the reach timeline, grouped by "
            "business area country. Shares are calculated from the active metric. Household "
            "metrics use recorded composition; social-worker programmes report workforce counts "
            "separately."
        ),
        "note": _("All countries with data in the period are shown. Children and PWD caveats apply."),
    },
    "demographic.region": {
        "definition": _("Share of the reached population by region."),
        "source": _("HOPE household, social-worker and payment data — country report demographic feed."),
        "method": _(
            "Uses the same payee and qualifying-payment base as the reach timeline, grouped by "
            "business-area region. Shares are calculated from the active metric (individuals, "
            "households, children or persons with disabilities)."
        ),
        "note": _("This is an intermediate view between the global cards and the country chart."),
    },
    # ------------------------------------------------------------------
    # Completion
    # ------------------------------------------------------------------
    "completion.timeline": {
        "definition": _("Reconciled and still-open payments or amount over time."),
        "source": _("HOPE payments — country report completion feed."),
        "method": _(
            "Reconciled uses the completion feed's RECONCILED reconciliation status. Open covers "
            "every other non-failed reconciliation status. Only payments in accepted, finished or "
            "closed plans are included; failed, removed and conflicted payments are excluded. USD "
            "is entitlement USD."
        ),
        "note": _(
            "Reconciled is green and Pending Reconciliation is amber across the timeline and country charts. "
            "The status mapping is applied when the report rows are loaded; Pending Reconciliation includes "
            "pending and other non-reconciled statuses."
        ),
    },
    "completion.country": {
        "definition": _("Reconciled and still-open payments by country."),
        "source": _("HOPE payments — country report completion feed."),
        "method": _(
            "Uses the same completion base as the reconciliation timeline, grouped by business "
            "area country. Each bar is the stacked total of reconciled and still-open values for "
            "the active metric."
        ),
        # xgettext:no-python-format
        "note": _(
            "All countries with completion data are shown. Absolute values is the default; 100% "
            "share shows each country's reconciled and pending split as percentages."
        ),
    },
    "completion.rates": {
        "definition": _("Reconciliation and delivery success rates by country."),
        "source": _("HOPE payments — financial and completion feeds."),
        "method": _(
            "Reconciliation rate is reconciled divided by reconciled plus pending reconciliation in the "
            "completion feed. Delivery success rate is successful statuses divided by successful "
            "plus pending statuses in the financial feed. Only countries present in both feeds "
            "are shown."
        ),
        # xgettext:no-python-format
        "note": _(
            "All countries present in both feeds are shown, sorted by reconciliation rate. The "
            "dashed 80% line is a reference guide, not a threshold."
        ),
    },
    "completion.verification": {
        "definition": _("Payment verification outcomes: selected, verified, pending and discrepancies."),
        "source": _("HOPE payment verification plans — country report completion feed."),
        "method": _(
            "Uses the verification-plan summaries: selected is the sample size, verified is the "
            "received count, pending is the sample size minus the responded count, and "
            "discrepancies are not-received plus received-with-issues. The date basis is the "
            "verification-plan activation date, falling back to the completion date."
        ),
        "note": _(
            "The completion rate is verified payments divided by selected payments. The panel "
            "appears when verification plans exist for the period."
        ),
    },
    # ------------------------------------------------------------------
    # Grievance
    # ------------------------------------------------------------------
    "grievance.timeline": {
        "definition": _("Grievance ticket volume over time, split into closed/resolved and open/active."),
        "source": _("HOPE grievances — country report grievance feed."),
        "method": _(
            "Counts tickets by created date. Ignored tickets are excluded and business area must "
            "be set. Closed covers the Closed and Resolved statuses; Open & Active covers New, "
            "Assigned, In Progress, On Hold and For Approval."
        ),
        "note": _(
            "HOPE integer status codes are mapped to labels before charting. System flags are a "
            "separate source and are excluded by default; use the ticket-source toggle to include "
            "them."
        ),
    },
    "grievance.status": {
        "definition": _("Grievance tickets by status."),
        "source": _("HOPE grievances — country report grievance feed."),
        "method": _("Counts tickets by the status value for the active ticket source and period."),
        "note": _(
            "Not specified means the source status field was blank. The doughnut is used until "
            "resolution-time data is available, when it is replaced by Average Grievance "
            "Resolution Time by Category."
        ),
    },
    "grievance.resolution": {
        "definition": _("Average grievance resolution time by category."),
        "source": _("HOPE grievances — country report grievance feed."),
        "method": _(
            "Average days between ticket creation and last update for closed tickets (status 6) "
            "created in the selected period, grouped by category. updated_at is used as the "
            "closure proxy because HOPE does not expose a dedicated closure timestamp."
        ),
        "note": _(
            "Only closed tickets with both timestamps are included. The status doughnut is shown "
            "instead until resolution rows exist."
        ),
    },
    "grievance.priority": {
        "definition": _("Grievance tickets by priority."),
        "source": _("HOPE grievances — country report grievance feed."),
        "method": _("Counts tickets by the priority value for the selected period and country."),
        "note": _(
            "Priority is an optional field in HOPE, so many tickets have none; these are "
            "reported as Not Set (source value 0)."
        ),
    },
    "grievance.category": {
        "definition": _("Grievance tickets by category."),
        "source": _("HOPE grievances — country report grievance feed."),
        "method": _("Counts tickets by the category value for the selected period and country."),
        "note": _("The chart shows the top 10 categories. Not specified means the category was blank."),
    },
    "grievance.subcategory": {
        "definition": _("Grievance tickets by subcategory."),
        "source": _("HOPE grievances — country report grievance feed."),
        "method": _(
            "Counts tickets by the subcategory value (stored as issue_type in HOPE) for "
            "categories that define subcategories: Data Change, Sensitive Grievance, "
            "Grievance Complaint and Needs Adjudication."
        ),
        "note": _(
            "The chart shows the top 10 subcategories. Payment Verification, feedback, "
            "referral, system-flagging and beneficiary categories have no subcategory and are "
            "excluded, so the chart total is lower than total tickets. HOPE calls this field "
            "Subcategory."
        ),
    },
    "grievance.country": {
        "definition": _("Grievance tickets by country, split into closed/resolved and open/active."),
        "source": _("HOPE grievances — country report grievance feed."),
        "method": _(
            "Uses the same ticket base as the grievance timeline, grouped by business area "
            "country. Each bar is the stacked total of closed/resolved and open/active tickets."
        ),
        "note": _("All countries with tickets in the period are shown; long country names wrap on the axis."),
    },
    # ------------------------------------------------------------------
    # Landing
    # ------------------------------------------------------------------
    "landing.trends": {
        "definition": _(
            "Global delivery over time: cash disbursed and the number of "
            "individuals, families, children and social workers reached."
        ),
        "source": _("HOPE payments and household registration data, aggregated by the country report."),
        "method": _(
            "Cash sums delivered quantity in USD. "
            "Individuals sums the registered household size of reached households; "
            "Families counts those households; Children sums the children "
            "recorded in household composition; Social Workers counts frontline workers "
            "reached through social-worker programmes."
        ),
        "note": _(
            "All years is the default and shows annual totals. Selecting a single year shows its monthly breakdown."
        ),
    },
    "landing.sector": {
        "definition": _("Share of cash assistance delivered by programme sector."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Sums delivered quantity in USD for the selected year and country, grouped by "
            "programme sector. The chart shows the largest sectors and groups the remainder "
            "as Other."
        ),
        "note": _("Percentages are of total cash delivered in the selected scope."),
    },
    "landing.mechanism": {
        "definition": _("Share of cash assistance delivered by payment mechanism."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Sums delivered quantity in USD for the selected year and country, grouped by "
            "delivery mechanism. The chart shows the largest mechanisms and groups the "
            "remainder as Other."
        ),
        "note": _("Payment mechanism is the HOPE delivery mechanism attached to the payment."),
    },
    "landing.children": {
        "definition": _("Children reached through household programmes in the current data."),
        "source": _("HOPE household registration and payment data — country report demographic feed."),
        "method": _(
            "Sums the children recorded in the composition of reached households. A household is "
            "counted when it has at least one qualifying payment in the period; the children count "
            "follows the household's recorded composition."
        ),
        "note": _(
            "Where household composition or children's dates of birth are missing, the figure is "
            "understated. This is not an estimate of all children in need."
        ),
    },
    "landing.households": {
        "definition": _("Families with at least one qualifying payment in the selected period."),
        "source": _("HOPE household registration and payment data — country report demographic feed."),
        "method": _(
            "Counts reached households distinctly. Qualifying payments must belong to accepted, "
            "finished or closed payment plans; failed, removed, conflicted and excluded payments "
            "are not included."
        ),
        "note": _(
            "Families are counted from standard (household) programmes; social-worker "
            "programmes are reported separately."
        ),
    },
    "landing.individuals": {
        "definition": _("People reached through household programmes in the current data."),
        "source": _("HOPE household registration and payment data — country report demographic feed."),
        "method": _(
            "Sums the registered household size of reached households. A household is counted when "
            "it has at least one qualifying payment in the period, using the delivery date, then "
            "the entitlement date, then the payment status date."
        ),
        "note": _("Frontline (incentive) workers are reported separately and are not part of this figure."),
    },
    "landing.assistance": {
        "definition": _("Cash disbursed directly to beneficiaries in the current data."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Sums delivered quantity in USD, grouped by sector to avoid double counting. "
            "Entitlement quantity is used only when a delivery amount is not recorded."
        ),
        "note": _("The figure covers direct cash transfers, not the full operational budget."),
    },
    "landing.payments": {
        "definition": _("Number of cash transfers delivered in the current data."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Sums payment records grouped by sector to avoid double counting. A payment record "
            "is not a unique recipient or a payment plan."
        ),
        "note": _("Average transfer value divides cash disbursed by the number of payment records."),
    },
    "landing.social_workers": {
        "definition": _("Frontline social workers assisted through social-worker programmes."),
        "source": _("HOPE social-worker programme records — country report demographic feed."),
        "method": _(
            "Sums the beneficiaries recorded for social-worker programmes. In these programmes "
            "each record represents one worker, so the beneficiary total is the workforce count."
        ),
        "note": _("Social-worker programmes are not part of household, children or persons-with-disabilities counts."),
    },
}


# KPI and risk entries kept separate from the chart entries above so the
# methodology drawer can present cards and charts in one consistent order.
CHART_INFO.update(
    {
        "financial.kpi_total_paid": {
            "definition": _("Cash delivered to beneficiaries for successful payment statuses."),
            "source": _("HOPE payments — country report financial feed."),
            "method": _(
                "Sums USD for Distribution Successful, Partially Distributed and Transaction "
                "Successful statuses. Uses delivered quantity when present, otherwise entitlement "
                "quantity, under the selected period, country and cohort."
            ),
            "note": _("This is the Delivered amount, not the reconciled amount."),
        },
        "financial.kpi_payment_records": {
            "definition": _("Number of payment records in the selected period and filters."),
            "source": _("HOPE payments — country report financial feed."),
            "method": _(
                "Counts payment records once from the active breakdown: sector by default, "
                "programme, delivery mechanism or FSP when one of those filters is active."
            ),
            "note": _(
                "Not payment plans, unique recipients, or only completed payments. Do not add "
                "this count across different breakdowns."
            ),
        },
        "financial.kpi_outstanding": {
            "definition": _("Entitlement amount for payments still pending."),
            "source": _("HOPE payments — country report financial feed."),
            "method": _(
                "Sums USD for SENT TO PAYMENT GATEWAY, SENT TO FSP and PENDING statuses under "
                "the selected period, country and cohort."
            ),
            "note": _("This is the Outstanding amount in the payment pipeline, not a failure rate."),
        },
        "demographic.kpi_individuals": {
            "definition": _("People reached through standard household programmes in the period."),
            "source": _("HOPE household and payment data — country report demographic feed."),
            "method": _(
                "Sums total_beneficiaries for STANDARD programme sector rows. Each household is "
                "counted through its recorded composition for the selected period."
            ),
            "note": _("Period reach, not annual unique people. Social-worker programmes are reported separately."),
        },
        "demographic.kpi_households": {
            "definition": _("Households reached through standard programmes in the period."),
            "source": _("HOPE household and payment data — country report demographic feed."),
            "method": _("Sums total_households for STANDARD programme sector rows in the selected period."),
            "note": _("Households, not payment records or unique payment plans."),
        },
        "demographic.kpi_pwd": {
            "definition": _("Confirmed persons with disabilities reached in the period."),
            "source": _("HOPE household and payment data — country report demographic feed."),
            "method": _("Sums total_pwd for STANDARD programme sector rows in the selected period."),
            "note": _("Some programmes do not collect disability data, so this is a minimum."),
        },
        "completion.kpi_reconciled": {
            "definition": _("Payments or amount with reconciliation status Reconciled in the period."),
            "source": _("HOPE payments — country report completion feed."),
            "method": _("Sums the active metric for rows whose reconciliation status is RECONCILED."),
            "note": _("Uses the completion reconciliation status, not the financial delivery status."),
        },
        "completion.kpi_pending": {
            "definition": _("Payments or amount with reconciliation status Open in the period."),
            "source": _("HOPE payments — country report completion feed."),
            "method": _("Sums the active metric for rows whose reconciliation status is OPEN or PENDING."),
            "note": _("Pending Reconciliation covers all non-reconciled statuses in the completion feed."),
        },
        "completion.kpi_rate": {
            "definition": _("Share of completion-feed records that are reconciled."),
            "source": _("HOPE payments — country report completion feed."),
            "method": _("Reconciled divided by Reconciled plus Pending Reconciliation for the active metric."),
            "note": _("This is a completion-feed rate, not the financial delivery success rate."),
        },
        "grievance.kpi_total": {
            "definition": _("Grievance tickets in the selected period and source."),
            "source": _("HOPE grievances — country report grievance feed."),
            "method": _("Sums ticket_count for the active ticket source, country and period."),
            "note": _("Use Include system flags to count system-generated tickets as well."),
        },
        "risk.kpi_total": {
            "definition": _("Total flagged operational risk issues in scope."),
            "source": _("HOPE risk feed."),
            "method": _(
                "Sums issue_count across risk indicators under the active period, country, "
                "programme, category and module filters."
            ),
            "note": _("A flag count, not a count of unique people or payments."),
        },
        "risk.kpi_critical": {
            "definition": _("Risk issues at critical severity."),
            "source": _("HOPE risk feed."),
            "method": _("Sums issue_count where severity is critical, at or above the 150% threshold."),
            "note": _("Critical is the highest severity band in the risk status guide."),
        },
        "risk.status_guide": {
            "definition": _("Severity thresholds used by the risk dashboard."),
            "source": _("HOPE risk feed."),
            "method": _("Critical is 150% or more, Warning is 100–149%, Caution is 80–99%, and Normal is below 80%."),
            "note": _("Thresholds compare the indicator value with its reference; they are not payment success rates."),
        },
        "risk.modules": {
            "definition": _("Distribution of risk issues by operational module."),
            "source": _("HOPE risk feed."),
            "method": _("Sums issue_count by module and shows each module's share of the filtered total."),
            "note": _("Click a module to narrow the operational cards; the percentage is of the filtered total."),
        },
        "risk.timeline": {
            "definition": _("Daily volume of flagged risk issues."),
            "source": _("HOPE risk feed."),
            "method": _("Sums issue_count by date for the active filters."),
            "note": _("The timeline shows when flags were reported, not when the underlying operational issue began."),
        },
        "risk.indicators": {
            "definition": _("Itemized risk indicators by country and programme."),
            "source": _("HOPE risk feed."),
            "method": _(
                "One row per risk code, country and programme. Issue counts are summed; severity, "
                "percentage, trend and description come from the latest record in the period."
            ),
            "note": _("The table respects the active country, programme, category and module filters."),
        },
        "risk.cards": {
            "definition": _("Operational risk cards grouped by module."),
            "source": _("HOPE risk feed."),
            "method": _(
                "Issue counts are summed by risk code; severity, percentage, trend and description "
                "come from the latest record. Cards are grouped under their operational module."
            ),
            "note": _("Select a module in Risk distribution by module to focus the cards."),
        },
    }
)


CHART_GUIDANCE = {
    "financial.kpi_total_paid": {
        "formula": _("Sum USD for Distribution Successful + Partially Distributed + Transaction Successful statuses."),
        "how_to_read": _(
            "This is the Delivered amount. It is not the reconciled amount and it matches the "
            "Delivered segment of the payment pipeline."
        ),
    },
    "financial.kpi_payment_records": {
        "formula": _("Count payment records once from the active breakdown; sector is the default."),
        "how_to_read": _("Not unique recipients, payment plans, or only completed payments."),
    },
    "financial.kpi_outstanding": {
        "formula": _("Sum USD for SENT TO PAYMENT GATEWAY + SENT TO FSP + PENDING statuses."),
        "how_to_read": _("This is the Outstanding amount in the payment pipeline."),
    },
    "financial.timeline": {
        "formula": _("Sum the selected metric by delivery date; fall back to entitlement date, then status date."),
        "how_to_read": _("The line shows the selected metric over time under the active filters."),
    },
    "financial.pipeline": {
        "formula": _(
            "Total payment volume = Delivered + Outstanding + Other statuses. "
            "Estimated reconciled = Delivered × reconciliation rate. "
            "Awaiting reconciliation = Delivered − Estimated reconciled."
        ),
        "how_to_read": _(
            "The payment-status breakdown is actual financial data. Reconciliation is a separate "
            "estimate from the completion feed. The cards show Delivered and Outstanding; there "
            "is no reconciled card. The stages are not independent buckets."
        ),
    },
    "financial.sector": {
        "formula": _("Group the selected metric by programme sector."),
        "how_to_read": _("The metric toggle switches between USD and payment records."),
    },
    "financial.delivery": {
        "formula": _("Group the selected metric by delivery mechanism."),
        "how_to_read": _("The metric toggle switches between USD and payment records."),
    },
    "financial.region": {
        "formula": _("Group the selected metric by UNICEF region."),
        "how_to_read": _("Bars are ordered by value and shaded from highest to lowest."),
    },
    "financial.country": {
        "formula": _("Group the selected metric by country."),
        "how_to_read": _("Outstanding by country is shown separately and is always in USD."),
    },
    "financial.outstanding_country": {
        "formula": _("Sum USD for pending statuses by country."),
        "how_to_read": _("Always USD, independent of the amount/payment-count toggle."),
    },
    "financial.program": {
        "formula": _("Group the selected metric by programme."),
        "how_to_read": _("Top 10 programmes plus an Other bucket."),
    },
    "financial.fsp": {
        "formula": _("Group the selected metric by financial service provider."),
        "how_to_read": _("Top 10 providers plus an Other bucket."),
    },
    "financial.implementing_partner": {
        "formula": _("Group the selected metric by implementing partner."),
        "how_to_read": _("The card appears when the feed provides the implementing-partner dimension."),
    },
    "demographic.kpi_individuals": {
        "formula": _("Sum total_beneficiaries for STANDARD programme sector rows."),
        "how_to_read": _("Period reach, not annual unique people. Social workers are reported separately."),
    },
    "demographic.kpi_households": {
        "formula": _("Sum total_households for STANDARD programme sector rows."),
        "how_to_read": _("Households, not payment records or unique payment plans."),
    },
    "demographic.children": {
        "formula": _("Sum the recorded children in reached households."),
        "how_to_read": _("Missing household composition understates the count; this is period reach."),
    },
    "demographic.kpi_pwd": {
        "formula": _("Sum total_pwd for STANDARD programme sector rows."),
        "how_to_read": _("Some programmes do not collect disability data, so treat this as a minimum."),
    },
    "demographic.reached": {
        "formula": _(
            "Count households with at least one qualifying payment; individuals, children and PWD "
            "come from household composition."
        ),
        "how_to_read": _("Qualifying payments must belong to accepted, finished or closed plans."),
    },
    "demographic.timeline": {
        "formula": _("Show the selected demographic metric by period."),
        "how_to_read": _(
            "Social-worker programmes report workforce counts separately; household metrics do not apply to them."
        ),
    },
    "demographic.sector": {
        "formula": _("Share of the selected metric by programme sector."),
        "how_to_read": _("Shares use the active metric and respect the cohort and country filters."),
    },
    "demographic.country": {
        "formula": _("Share of the selected metric by country."),
        "how_to_read": _("All countries with data in the period are shown."),
    },
    "demographic.region": {
        "formula": _("Share of the selected metric by UNICEF region."),
        "how_to_read": _("An intermediate view between the global cards and the country chart."),
    },
    "completion.kpi_reconciled": {
        "formula": _("Sum the active metric for reconciliation status RECONCILED."),
        "how_to_read": _("Uses the completion reconciliation status, not the financial delivery status."),
    },
    "completion.kpi_pending": {
        "formula": _("Sum the active metric for reconciliation status OPEN/PENDING."),
        "how_to_read": _("Pending Reconciliation covers all non-reconciled statuses in the completion feed."),
    },
    "completion.kpi_rate": {
        "formula": _("Reconciled ÷ (Reconciled + Pending Reconciliation) for the active metric."),
        "how_to_read": _("This is a completion-feed rate, not the financial delivery success rate."),
    },
    "completion.timeline": {
        "formula": _("Show Reconciled and Open amounts or counts by period."),
        "how_to_read": _("Reconciled is the completion reconciliation status; Open is every other non-failed status."),
    },
    "completion.country": {
        "formula": _("Show Reconciled and Open by country, stacked."),
        "how_to_read": _("Absolute values is the default; percentages show the split within each country."),
    },
    "completion.rates": {
        "formula": _(
            "Reconciliation rate = Reconciled ÷ (Reconciled + Pending Reconciliation). "
            "Delivery success = successful ÷ (successful + pending financial statuses)."
        ),
        "how_to_read": _("The dashed 80% line is a reference guide, not a threshold."),
    },
    "completion.verification": {
        "formula": _(
            "Selected = sample size; verified = received; pending = sample − responded; "
            "discrepancies = not received + received with issues."
        ),
        "how_to_read": _("Completion rate = verified ÷ selected. The panel appears when verification plans exist."),
    },
    "grievance.kpi_total": {
        "formula": _("Sum ticket_count for the active ticket source and filters."),
        "how_to_read": _("System flags are excluded by default; use the ticket-source toggle to include them."),
    },
    "grievance.timeline": {
        "formula": _("Count open/active and closed/resolved tickets by created date."),
        "how_to_read": _("Closed covers Closed and Resolved; Open & Active covers the remaining workflow statuses."),
    },
    "grievance.status": {
        "formula": _("Count tickets by status for the active source and period."),
        "how_to_read": _("The doughnut is replaced by resolution time when resolution rows exist."),
    },
    "grievance.resolution": {
        "formula": _("Average days from ticket creation to last update for closed tickets, grouped by category."),
        "how_to_read": _("updated_at is the closure proxy; tickets without both timestamps are excluded."),
    },
    "grievance.priority": {
        "formula": _("Count tickets by priority value."),
        "how_to_read": _("Priority is optional in HOPE; missing values appear as Not Set."),
    },
    "grievance.category": {
        "formula": _("Count tickets by category."),
        "how_to_read": _("Top 10 categories are shown. Not specified means the category was blank."),
    },
    "grievance.subcategory": {
        "formula": _("Count tickets by subcategory for categories that define one."),
        "how_to_read": _(
            "Payment Verification, feedback, referral, system-flagging and beneficiary categories have no subcategory."
        ),
    },
    "grievance.country": {
        "formula": _("Stack closed/resolved and open/active tickets by country."),
        "how_to_read": _("Uses the same ticket base as the grievance timeline."),
    },
    "risk.kpi_total": {
        "formula": _("Sum issue_count across risk indicators under the active filters."),
        "how_to_read": _("A flag count, not a count of unique people or payments."),
    },
    "risk.kpi_critical": {
        "formula": _("Sum issue_count where severity is critical, at or above 150%."),
        "how_to_read": _("Critical is the highest severity band in the risk status guide."),
    },
    "risk.status_guide": {
        "formula": _("Critical ≥150%; Warning 100–149%; Caution 80–99%; Normal <80%."),
        "how_to_read": _("Thresholds compare the indicator with its reference; they are not payment success rates."),
    },
    "risk.modules": {
        "formula": _("Share of issue_count by operational module."),
        "how_to_read": _("Click a module to narrow the operational cards; percentages are of the filtered total."),
    },
    "risk.timeline": {
        "formula": _("Sum issue_count by date for the active filters."),
        "how_to_read": _("Shows when flags were reported, not when the underlying issue began."),
    },
    "risk.indicators": {
        "formula": _(
            "One row per risk code × country × programme; sum issue_count and use the latest "
            "severity, percentage and trend."
        ),
        "how_to_read": _("Respects the active country, programme, category and module filters."),
    },
    "risk.cards": {
        "formula": _(
            "Sum issue_count by risk code; use the latest percentage, severity, trend and description; group by module."
        ),
        "how_to_read": _("Select a module in Risk distribution by module to focus the cards."),
    },
}
