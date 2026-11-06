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
        "note": _("Top 10 countries plus an Other bucket; outstanding is shown beside it."),
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
            "Always shown in USD, independent of the amount/payment-count toggle. Top 10 "
            "countries plus an Other bucket."
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
        "source": _("HOPE households and payments — country report demographic feed."),
        "method": _(
            "Demographic rows come from households with at least one qualifying payment in the "
            "month. Payment plans must be accepted, finished or closed; failed, removed, "
            "conflicted and excluded payments are excluded. Households are counted distinctly. "
            "Beneficiary, child and PWD counts follow the household's recorded composition; "
            "missing composition or dates of birth understate the totals."
        ),
        "note": _(
            "Under the current legacy calculation, a household with more than one qualifying "
            "payment in a month can contribute its size, children and PWD counts once per "
            "payment; total households remains distinct. PWD figures may be under-reported where "
            "programmes do not collect them."
        ),
    },
    "demographic.sector": {
        "definition": _("Share of the reached population by programme sector."),
        "source": _("HOPE households and payments — country report demographic feed."),
        "method": _(
            "Uses the same demographic base as the reach timeline, grouped by programme sector. "
            "Shares are calculated from the active metric (individuals, households, children or "
            "persons with disabilities)."
        ),
        "note": _("Children and PWD under-reporting caveats also apply here."),
    },
    "demographic.country": {
        "definition": _("Share of the reached population by country."),
        "source": _("HOPE households and payments — country report demographic feed."),
        "method": _(
            "Uses the same demographic base as the reach timeline, grouped by business area "
            "country. Shares are calculated from the active metric."
        ),
        "note": _("The chart shows the top 10 countries. Children and PWD caveats apply."),
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
        "note": _(
            "Top 10 countries by total volume. Absolute values is the default; 100% share shows "
            "each country's reconciled and still-open split as percentages."
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
        "note": _(
            "Top 12 countries by completion volume, sorted by reconciliation rate. The dashed "
            "80% line is a reference guide, not a threshold."
        ),
    },
    "completion.verification": {
        "definition": _("Payment verification outcomes: selected, verified, pending and discrepancies."),
        "source": _("HOPE payments — verification records in the country report completion feed."),
        "method": _(
            "Counts payments by verification outcome for the selected period. The completion rate "
            "is successfully verified payments divided by payments selected for verification."
        ),
        "note": _("Appears once the completion feed provides verification rows (dimension type verification)."),
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
        "note": _("The chart shows the top 10 countries by total tickets."),
    },
    # ------------------------------------------------------------------
    # Landing
    # ------------------------------------------------------------------
    "landing.trends": {
        "definition": _(
            "Global delivery over time: cash disbursed, payment count, and the number of "
            "individuals, households and children reached by household programmes."
        ),
        "source": _("HOPE payments and household registration data, aggregated by the country report."),
        "method": _(
            "Total Cash Disbursed sums delivered quantity in USD. Payments Count counts payment "
            "records — not payment plans, unique recipients or only completed payments. "
            "Individuals Reached sums the registered household size of reached households; "
            "Households Reached counts those households; Children Reached sums the children "
            "recorded in household composition. Frontline (incentive) workers are reported "
            "separately and are not part of these series."
        ),
        "note": _(
            "All years is the default. Last 5 years shows the current year and the previous four. "
            "Selecting a year shows its monthly data. Where a year or month has no demographic "
            "record, the reached series are estimated from payment volume."
        ),
    },
}
