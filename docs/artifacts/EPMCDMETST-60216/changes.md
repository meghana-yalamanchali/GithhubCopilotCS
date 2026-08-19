# Implementation Changes: EPMCDMETST-60216

## Changed Files

| Path | Change | Rationale |
| --- | --- | --- |
| `main.py` | Modified | Adds strict server-side validation, `APP_TIMEZONE` (`UTC` default), per-request dashboard dates, and safe invalid-form rendering before persistence. |
| `templates/index.html` | Modified | Adds labels, stable field error regions, server-rendered values/error state, and the deferred controller asset while preserving the form contract. |
| `static/style.css` | Modified | Adds scoped focus, invalid, error, and responsive form styles. |
| `static/task-form-validation.js` | Created | Provides form-scoped progressive client validation, ARIA state, inline messages, and first-invalid focus. |
| `requirements-dev.txt` | Created | Declares Flask, pytest, and cross-platform IANA timezone data. |
| `package.json` | Created | Declares Playwright browser testing. |
| `playwright.config.js` | Created | Configures the Flask web server and one-worker Playwright execution. |
| `tests/test_home.py` | Created | Covers direct authenticated POST rejection, persistence safety, valid redirect, and timezone policy. |
| `tests/browser/task-form.spec.js` | Created | Covers client submit blocking, ARIA state, focus, correction clearing, valid pass-through, and narrow layout. |
| `.github/workflows/validation.yml` | Created | Runs compile, Flask, and Playwright validation in CI. |

## Validation Commands

```text
py -3 -m compileall main.py tests
py -3 -m pytest tests/test_home.py
npx playwright test tests/browser/task-form.spec.js
```

Completed on 2026-08-20: `py -3 -m compileall main.py tests` passed, `py -3 -m pytest tests/test_home.py` passed (9 tests), and `npx playwright test tests/browser/task-form.spec.js` passed (5 tests).

## Remaining Risks

- Client-side due-date validation uses the browser's local calendar date while the server is authoritative in `APP_TIMEZONE`; near a time-zone boundary, a browser-accepted date can be server-rejected and shown as a server error.
- The current Flask session secret remains hard-coded and must be moved to deployment-managed configuration before production release.
- Native date input behavior and live-region announcements still need the manual keyboard and screen-reader check described in the approved implementation plan.