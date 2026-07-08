# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Internal company web app ("hours") for employee timesheets, payments, food ordering, daily reports, and a management dashboard ("Esfa Eyes"). Django 5.2 + Django REST Framework monolith with server-rendered templates. All dates use the Jalali (Persian) calendar via `jdatetime`; timezone is `Asia/Tehran`; much of the UI text is Persian.

## Layout

The Django project lives in the `hours/` subdirectory (so `manage.py` is at `hours/manage.py`). The virtualenv is `.venv/` at the repo root (Python 3.12).

## Commands

Run everything from the `hours/` directory:

```bash
cd hours
../.venv/bin/python manage.py runserver            # dev server (site mounted at /hours/)
../.venv/bin/python manage.py livereload           # optional, in a second terminal (django-livereload-server)

# Tests (Django test runner; tests live in sheets/tests/)
../.venv/bin/python manage.py test sheets
../.venv/bin/python manage.py test sheets.tests.test_hour_approval_workflow.HourApprovalWorkflowTests.test_user_can_submit_sheet

# Management commands
../.venv/bin/python manage.py import_hours <xlsx> <year> <month> [--task_id ID]   # bulk hours import
../.venv/bin/python manage.py check_submissions --dry-run                          # esfa_eyes Telegram alerting

# Template linting (config in hours/pyproject.toml)
../.venv/bin/djlint sheets/templates/ --reformat
```

**Known issue:** the test suite currently fails during test-database creation — several `esfa_eyes` data migrations import the *live* `EsfaEyes` model (not `apps.get_model`), so they query columns added by later migrations. Fix or work around this before relying on test results.

## Local settings

`hours/hours/settings.py` has `DEBUG = False` and no `SECRET_KEY`; it ends with `from hours.local import *`. A gitignored `hours/hours/local.py` provides `SECRET_KEY`, `DEBUG = True`, and empty `LOGGING` for development. The DB is SQLite at `hours/db.sqlite3` (gitignored; `hours/fetch-db-from-server.sh` pulls a copy from the production server).

## Architecture

Two Django apps, both mounted under the `/hours/` URL prefix (`hours/hours/urls.py`):

### `sheets` — timesheets, payments, food, daily reports (the core app)

- **Custom user model** `sheets.User` (`AUTH_USER_MODEL`). Authorization is NOT Django groups/permissions — it's boolean role flags on the user (`is_HourVerifier`, `is_PaymentManager`, `is_FoodManager`, `is_FinancialManager`, ...) plus two self-referencing manager FKs (`manager_level_1`, `manager_level_2`). Enforcement is via `customDecorators.py` / `customPermissions.py` in each app.
- **`Sheet` model** — one per user per Jalali month. The month grid is a JSONField `data`: a list of per-day dicts with `"hh:mm"` string values (`Auto Hours`, `Remote`, `Rest`, per-project percentage columns like `"50%"`). `Sheet.transform()` converts it to a pandas DataFrame in minutes; `mean`/`total` are stored in minutes and recomputed on every `save()`. `Sheet.save()` and `normalize_sheet()` deliberately never persist an empty grid — they rebuild a blank month via `empty_sheet_data(year, month)` for the sheet's own period.
- **Approval workflow** — submitted → `manager_level_1_verified` → `manager_level_2_verified` → `supreme_verified`, with `*_by`/`*_at` audit fields and rejection tracking. Legacy fields `is_verified`/`is_supreme_verified` are intentionally kept and synchronized via `sync_legacy_verification_fields()`; don't remove them. The workflow is exercised by `sheets/tests/test_hour_approval_workflow.py`.
- Verifier scoping also uses `staff_group_tag` (on employees) vs. `verifier_group_tags` (comma-separated, on verifiers).
- **Excel import/export** uses pandas/openpyxl/XlsxWriter. Long-running imports go through the `import_hours` management command with a file-based task-status mechanism (`sheets/task_utils.py`, JSON files under `media/task_status/`) polled by the `import_status/<task_id>` endpoint — there is no Celery worker in use despite celery being in requirements.
- Page views are in `views.py`, JSON endpoints in `api_views.py` (large file, ~76K) as DRF `APIView`s.

### `esfa_eyes` — management KPI dashboard

- Single-row-per-year `EsfaEyes` model whose fields are JSONFields per business domain (`financial_info`, `products_info`, `kia_products_info`, ...). Default structures are built in `models.py` from schema classes in `esfa_eyes/schemas/`; per-field visibility is an embedded `who_can_see` list matched against user flags/names (`access_mappings`).
- `check_submissions` management command sends Telegram reminders/alerts to field owners when data is stale; it runs on the production server via the systemd units in `system_files/` (`esfa_checker.timer`, plus `esfa_backup.timer` for tiered SQLite backups).

### Frontend

Server-rendered Django templates (Bootstrap 5, RTL/Persian) with heavy inline JavaScript — `sheets/templates/hours.html` (~50K) embeds a jspreadsheet grid that talks to the `api/sheets/<year>/<month>` endpoint. There is no JS build step; static assets are vendored under each app's `static/`. `ManifestStaticFilesStorage` is used, so run `collectstatic` when deploying.

## Conventions

- `sheets/models.py` and much of the app code is indented with tabs — match the file you're editing.
- Time durations are minutes as ints in Python/DB, `"hh:mm"` strings in sheet JSON and the UI; money is plain int rials.
- Year/month URL params arrive as strings and are Jalali, not Gregorian.
