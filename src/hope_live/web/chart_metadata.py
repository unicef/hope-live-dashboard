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
            "cohort and chart filters apply."
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
    },
    "financial.country": {
        "definition": _("Cash disbursed or payments by country."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Payment rows are grouped by the business area country slug using the same date and "
            "status filters as the financial timeline."
        ),
        "note": _("The chart shows the top 10 countries ranked by the active metric."),
    },
    "financial.program": {
        "definition": _("Cash disbursed or payments by programme."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Payment rows are grouped by programme name using the same date and status filters as "
            "the financial timeline."
        ),
        "note": _("The chart shows the top 10 programmes ranked by the active metric."),
    },
    "financial.fsp": {
        "definition": _("Cash disbursed or payments by financial service provider."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Payment rows are grouped by financial service provider name using the same date and "
            "status filters as the financial timeline."
        ),
        "note": _("The chart shows the top 10 providers ranked by the active metric."),
    },
    "financial.beneficiary_group": {
        "definition": _("Cash disbursed or payments by beneficiary group."),
        "source": _("HOPE payments — country report financial feed."),
        "method": _(
            "Payment rows are grouped by the programme's beneficiary group label using the same "
            "date and status filters as the financial timeline."
        ),
        "note": _("The chart shows the top 10 groups ranked by the active metric."),
    },
    # ------------------------------------------------------------------
    # Demographic
    # ------------------------------------------------------------------
    "demographic.timeline": {
        "definition": _("Individuals, households, children or persons with disabilities reached over time."),
        "source": _("HOPE households and payments — country report demographic feed."),
        "method": _(
            "Demographic rows come from households with at least one qualifying payment in the "
            "month. Payment plans must be accepted, finished or closed; failed, removed, "
            "conflicted and excluded payments are excluded. Households are counted distinctly. "
            "Beneficiary, child and PWD counts follow the programme-collected household fields; "
            "children may be estimated with fertility multipliers where a programme does not "
            "collect them."
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
        "note": _("Children estimates and the PWD under-reporting caveat also apply here."),
    },
    "demographic.country": {
        "definition": _("Share of the reached population by country."),
        "source": _("HOPE households and payments — country report demographic feed."),
        "method": _(
            "Uses the same demographic base as the reach timeline, grouped by business area "
            "country. Shares are calculated from the active metric."
        ),
        "note": _("The chart shows the top 10 countries. Children estimates and PWD caveats apply."),
    },
    "demographic.beneficiary_group": {
        "definition": _("Reached population by beneficiary group."),
        "source": _("HOPE households and payments — country report demographic feed."),
        "method": _(
            "Uses the same demographic base as the reach timeline, grouped by the programme's "
            "beneficiary group label. Values follow the active metric."
        ),
        "note": _("The chart shows the top 10 groups. Children estimates and PWD caveats apply."),
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
            "Still open. Only payments in accepted, finished or closed plans are included; "
            "failed, removed and conflicted payments are excluded. USD is entitlement USD."
        ),
        "note": _(
            "The status mapping is applied when the report rows are loaded. Still open includes "
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
        "note": _("The chart shows the top 10 countries by total volume."),
    },
    "completion.beneficiary_group": {
        "definition": _("Reconciled payments by beneficiary group."),
        "source": _("HOPE payments — country report completion feed."),
        "method": _(
            "Uses the same completion base as the reconciliation timeline, grouped by the "
            "programme's beneficiary group label. Values follow the active metric."
        ),
        "note": _("The chart shows the top 10 groups."),
    },
    "completion.quadrant": {
        "definition": _("Delivery success rate versus reconciliation rate by country."),
        "source": _("HOPE payments — financial and completion feeds."),
        "method": _(
            "Reconciliation rate is reconciled divided by reconciled plus still open in the "
            "completion feed. Delivery success rate is successful statuses divided by successful "
            "plus pending statuses in the financial feed. Bubble size is total reconciled volume. "
            "Only countries present in both feeds are plotted."
        ),
        "note": _("The dashed 80% lines are reference guides, not thresholds."),
    },
    # ------------------------------------------------------------------
    # Grievance
    # ------------------------------------------------------------------
    "grievance.timeline": {
        "definition": _("Grievance ticket volume over time, split into closed/resolved and open/active."),
        "source": _("HOPE grievances — country report grievance feed."),
        "method": _(
            "Counts tickets by created date. Ignored tickets are excluded and business area must "
            "be set. A ticket is resolved/closed when its status contains RESOLVED or CLOSED; all "
            "other statuses are open/active."
        ),
        "note": _("HOPE integer status codes are mapped to labels before charting."),
    },
    "grievance.status": {
        "definition": _("Grievance tickets by status."),
        "source": _("HOPE grievances — country report grievance feed."),
        "method": _("Counts tickets by the status value for the selected period and country."),
        "note": _("Unknown means the source status field was blank."),
    },
    "grievance.priority": {
        "definition": _("Grievance tickets by priority."),
        "source": _("HOPE grievances — country report grievance feed."),
        "method": _("Counts tickets by the priority value for the selected period and country."),
        "note": _("Not Set is shown when the source priority is 0."),
    },
    "grievance.category": {
        "definition": _("Grievance tickets by category."),
        "source": _("HOPE grievances — country report grievance feed."),
        "method": _("Counts tickets by the category value for the selected period and country."),
        "note": _("The chart shows the top 10 categories. Unknown means the category was blank."),
    },
    "grievance.subcategory": {
        "definition": _("Grievance tickets by subcategory."),
        "source": _("HOPE grievances — country report grievance feed."),
        "method": _("Counts tickets by the issue-type value for the selected period and country."),
        "note": _(
            "The chart shows the top 10 subcategories. Unknown means the issue type was blank. "
            "HOPE calls this field Subcategory."
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
}
