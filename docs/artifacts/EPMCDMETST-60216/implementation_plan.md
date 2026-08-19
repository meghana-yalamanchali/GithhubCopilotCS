# Implementation Plan: EPMCDMETST-60216

## Meta

- **Ticket:** EPMCDMETST-60216
- **Title:** Registered user: Validate todo task form with inline, accessible error messages
- **Status:** Approved for implementation planning
- **Execution mode:** Dependency-ordered, five waves
- **Design input:** [design_spec.md](design_spec.md) version 1.1
- **Review input:** [design_review.md](design_review.md) follow-up decision: Pass with non-blocking operational risks

## Pre-Implementation Baseline

- The application is a Flask project with source in `main.py`, the dashboard in `templates/index.html`, and styles in `static/style.css`.
- The current Add Task `POST /` branch directly indexes request fields, manually splits dates, and mutates `items` without authoritative validation.
- No test runner, browser test runner, dependency manifest, or CI workflow is present.
- Existing form contract to retain: `POST /`, `newItem`, `duedate`, native `type="date"`, authenticated route behavior, and redirect after a valid submission.

## File Plan

| Path | Change | Component ID | Wave | Purpose | Verify command |
| --- | --- | --- | --- | --- | --- |
| `requirements-dev.txt` | New | CMP-TEST-PY | 1 | Declare Flask test dependencies including `pytest`. | `python -m pip install -r requirements-dev.txt` |
| `package.json` | New | CMP-TEST-BROWSER | 1 | Declare Playwright browser-test scripts and dependency. | `npm install` |
| `main.py` | Modify | CMP-SERVER-VALIDATION | 2 | Add configurable application clock, strict server validation, and safe invalid-response rendering. | `python -m compileall main.py` |
| `templates/index.html` | Modify | CMP-DASHBOARD-FORM | 2 | Add semantic form hooks, labels, stable error regions, values, and deferred validation asset. | `python -m pytest tests/test_home.py` |
| `playwright.config.js` | New | CMP-TEST-BROWSER | 2 | Configure the browser test runner and application web server. | `npx playwright test --list` |
| `static/task-form-validation.js` | New | CMP-CLIENT-VALIDATION | 3 | Validate form submissions, render ARIA state, and focus the first invalid control. | `npx playwright test tests/browser/task-form.spec.js` |
| `static/style.css` | Modify | CMP-FORM-STYLES | 3 | Add accessible invalid and focus styles plus mobile-safe error wrapping. | `npx playwright test tests/browser/task-form.spec.js` |
| `tests/test_home.py` | New | CMP-TEST-PY | 4 | Test direct invalid and valid Flask POST behavior, persistence, and clock boundaries. | `python -m pytest tests/test_home.py` |
| `tests/browser/task-form.spec.js` | New | CMP-TEST-BROWSER | 4 | Test client validation, accessibility state, focus, valid submission, and narrow viewport behavior. | `npx playwright test tests/browser/task-form.spec.js` |
| `.github/workflows/validation.yml` | New | CMP-CI | 5 | Run required compile, Flask, and Playwright checks in CI. | `git diff --check` |

## Dependency Waves

### Wave 1: Establish Test Tooling

1. **`requirements-dev.txt` — New — CMP-TEST-PY**
   - Add the Python development/test dependencies needed to run focused Flask tests.
   - Verify: `python -m pip install -r requirements-dev.txt`.
2. **`package.json` — New — CMP-TEST-BROWSER**
   - Add the Playwright dependency and a targeted browser-test script.
   - Verify: `npm install`.

### Wave 2: Define the Server and Form Contract

1. **`main.py` — Modify — CMP-SERVER-VALIDATION**
   - Add `APP_TIMEZONE` configuration with `UTC` default and a per-request application-clock helper for the date heading and validation.
   - Use safe form lookups; reject blank or whitespace-only names and non-exact, invalid, today, or past dates before any mutation.
   - Preserve submitted safe values and fixed field errors when re-rendering; retain the valid redirect and item model.
   - Verify: `python -m compileall main.py`.
2. **`templates/index.html` — Modify — CMP-DASHBOARD-FORM**
   - Preserve the request contract and native required controls; add labels, form/input/error IDs, server error state, and a deferred client script.
   - Verify: `python -m pytest tests/test_home.py`.
3. **`playwright.config.js` — New — CMP-TEST-BROWSER**
   - Start the Flask application for browser tests and set deterministic test defaults.
   - Verify: `npx playwright test --list`.

### Wave 3: Add Browser Validation and Visual States

1. **`static/task-form-validation.js` — New — CMP-CLIENT-VALIDATION**
   - On controller attachment, set `form.noValidate = true`; retain native behavior when JavaScript is unavailable.
   - Validate both fields on submit, render fixed inline errors and ARIA relationships, prevent invalid posts, focus the first invalid control, and clear passed-field state on later submits.
   - Verify: `npx playwright test tests/browser/task-form.spec.js`.
2. **`static/style.css` — Modify — CMP-FORM-STYLES**
   - Scope form layout, visible focus, invalid-state, and wrapping rules to the dashboard Add Task form without redesigning other pages.
   - Verify: `npx playwright test tests/browser/task-form.spec.js`.

### Wave 4: Implement Acceptance Tests

1. **`tests/test_home.py` — New — CMP-TEST-PY**
   - Cover authenticated direct posts with missing, whitespace, malformed, impossible, today, past, and future values; assert rejected requests do not append items.
   - Cover valid redirect/persistence and configured application-clock boundary behavior.
   - Verify: `python -m pytest tests/test_home.py`.
2. **`tests/browser/task-form.spec.js` — New — CMP-TEST-BROWSER**
   - Cover blank fields, field-specific errors, ARIA attributes, error associations, live regions, focus order, correction clearing, valid pass-through, and no horizontal scroll at a narrow viewport.
   - Verify: `npx playwright test tests/browser/task-form.spec.js`.

### Wave 5: Enforce the Pipeline

1. **`.github/workflows/validation.yml` — New — CMP-CI**
   - Install declared Python and Node dependencies, install Playwright browsers, and run compile, Flask, and browser checks.
   - Verify: `git diff --check`.

## Acceptance-Criteria Mapping

| Acceptance criteria | Implementing components and files | Evidence |
| --- | --- | --- |
| AC-001, AC-002, AC-003, AC-004 | CMP-DASHBOARD-FORM, CMP-CLIENT-VALIDATION; `templates/index.html`, `static/task-form-validation.js` | Playwright invalid-submit cases and focus assertions. |
| AC-005 | CMP-DASHBOARD-FORM, CMP-CLIENT-VALIDATION, CMP-FORM-STYLES; template, script, stylesheet | Playwright ARIA, live-region, and visible-error checks. |
| AC-006 | CMP-CLIENT-VALIDATION, CMP-SERVER-VALIDATION; script and `main.py` | Playwright valid pass-through and Flask valid redirect tests. |
| AC-007 | CMP-SERVER-VALIDATION, CMP-DASHBOARD-FORM; `main.py`, template | Direct Flask POST rejection tests. |
| AC-008 | CMP-FORM-STYLES, CMP-TEST-BROWSER; stylesheet and browser suite | Narrow-viewport horizontal-scroll assertion. |

## Risks and Mitigation

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Browser-local preflight differs from the authoritative server clock near midnight. | A browser-accepted value can be rejected by the server. | Document `APP_TIMEZONE`, render the server error, and test application-clock boundaries. |
| Native constraint validation suppresses submit events. | Custom errors and focus may not render. | Set `form.noValidate` only after the JavaScript controller attaches; preserve `required` for no-JavaScript operation. |
| Global in-memory list leaks state between Flask tests. | Test cases become order-dependent. | Isolate and reset global state in test setup/teardown. |
| Hard-coded Flask secret remains. | Production session-security exposure. | Treat environment-managed secret configuration as a separate release prerequisite. |

## Review Conditions

- **Status:** Satisfied by design specification version 1.1 and the follow-up review.
- The implementation must not substitute native date controls, alter route or field names, bypass server validation, or change valid redirect semantics.
- The test tooling and CI files listed above are required deliverables, not follow-up work.

## Pipeline Continuation

1. Implement waves in order; complete every listed verification command before advancing.
2. Run the complete local gate after Wave 5:

```text
python -m compileall main.py tests
python -m pytest tests/test_home.py
npx playwright test tests/browser/task-form.spec.js
```

3. Record the manual keyboard, screen-reader, native-date-control, contrast, and narrow-viewport accessibility check in the pull request.
4. Preserve the approved branch and commit history for the implementation handoff.