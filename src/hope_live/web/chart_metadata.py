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
            "Reconciled includes Sent to Payment Gateway, Sent to FSP, Distribution Successful, "
            "Partially Distributed and Transaction Successful. All other non-failed statuses are "
            "Pending Reconciliation. Only payments in accepted, finished or closed plans are included; "
            "failed, removed and conflicted payments are excluded. USD is entitlement USD."
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
            "individuals, families and children reached by household programmes."
        ),
        "source": _("HOPE payments and household registration data, aggregated by the country report."),
        "method": _(
            "Cash sums delivered quantity in USD. "
            "Individuals sums the registered household size of reached households; "
            "Families counts those households; Children sums the children "
            "recorded in household composition. Frontline (incentive) workers are reported "
            "separately and are not part of these series."
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
