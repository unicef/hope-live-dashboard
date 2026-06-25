# Settings & Data Sync Configuration

This page describes how to configure the HOPE Live Dashboard, how settings are managed dynamically using **Django Constance**, and how the periodic daily aggregate download works.

---

## 1. Dynamic Settings (Django Constance)

Dynamic application settings are managed through **Django Constance**, allowing administrators to change settings directly via the Django Admin panel without requiring a code deploy or server restart.

Go to the **Django Admin Panel** -> **Constance** -> **Config** to edit the following:

### API Connection Settings
*   **`HOPE_COUNTRY_REPORT_API_URL`** (Type: `str`)
    The base API endpoint from which aggregate datasets are retrieved.
    *Default:* `https://reporting-hope-dev.unitst.org/api/`
*   **`HOPE_COUNTRY_REPORT_API_TOKEN`** (Type: `token`/`str`)
    The token used for authentication against the API endpoint (`Authorization: Token <TOKEN>`).

### Dataset Query IDs
These query IDs map to specific dataset types on the API server:
*   **`HOPE_COUNTRY_REPORT_QUERY_ID`** (Type: `int`)
    The query ID representing the Country Report Aggregate dataset.
    *Default:* `6`
*   **`HOPE_FINANCIAL_REPORT_QUERY_ID`** (Type: `int`)
    The query ID representing the Financial dataset.
    *Default:* `6`
*   **`HOPE_DEMOGRAPHIC_REPORT_QUERY_ID`** (Type: `int`)
    The query ID representing the Demographic dataset.
    *Default:* `7`
*   **`HOPE_COMPLETION_REPORT_QUERY_ID`** (Type: `int`)
    The query ID representing the Completion/Reconciliation dataset.
    *Default:* `8`
*   **`HOPE_GRIEVANCE_REPORT_QUERY_ID`** (Type: `int`)
    The query ID representing the Feedback/Grievance dataset.
    *Default:* `9`

---

## 2. Daily Data Synchronization

To keep the dashboards updated, a periodic sync job runs in the background to download fresh aggregate data.

### Scheduled Execution (Celery Beat)
Synchronization is scheduled via **Celery Beat** to run automatically once a day:
*   **Task**: `hope_live.analysis.tasks.schedule_sync_daily_aggregates`
*   **Schedule**: Runs daily at **2:00 AM UTC** (`crontab(hour=2, minute=0)`).
*   **Default Behavior**: By default, it retrieves data for the current year and the previous year.

### Manually Running a Sync
You can trigger the synchronization process manually through the Django Admin panel:
1.  Go to the **Sync Daily Aggregates Jobs** section in the Admin interface.
2.  Click **"Add Sync Daily Aggregates Job"**.
3.  Upon creation, the Celery task (`sync_daily_aggregates`) will automatically trigger and run in the background.

### Monitoring & Status Tracking
Every execution creates a `SyncDailyAggregatesJob` database record. Administrators can monitor progress and debug failures directly from the list view:
*   `task_status`: Displays the status of the Celery worker (e.g., `SUCCESS`, `FAILURE`, `PROGRESS`).
*   `error_message`: Captures error details if the download fails (e.g., connection timeout or authentication error).

---

## 3. Maintenance Commands

### Clearing Aggregates
If you need to delete all aggregates from the database to perform a fresh sync, superusers can click the **"Clear Daily Aggregates"** button on the `SyncDailyAggregatesJob` admin page. This triggers the background task `clear_daily_aggregates` and safely removes all local aggregate records.

### Updating Fertility Rates
The background task `update_fertility_rates` runs periodically to execute the `update_fertility_rates` management command. This updates the local fertility rates statistics from the static rates definition file (`fertility_rates.json`).
