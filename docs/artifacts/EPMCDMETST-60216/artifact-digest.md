# Artifact Digest: EPMCDMETST-60216

## Ticket

- **ID:** EPMCDMETST-60216
- **Title:** Registered user: Validate todo task form with inline, accessible error messages
- **Date:** 2026-08-20

## Artifact Status

| Artifact | Status | Summary |
| --- | --- | --- |
| [problem_spec.md](problem_spec.md) | Approved | Defines accessible, progressive client-side validation with authoritative server validation and a preserved no-JavaScript path. |
| [design_spec.md](design_spec.md) | Amended, pending re-review | Defines the JavaScript event model, strict server date validation, configurable application clock, and executable test tooling. |
| [design_review.md](design_review.md) | Superseded pending re-review | Its blocking findings are addressed in design specification version 1.1 and require reviewer confirmation. |

## Review Conditions

The amended design resolves the following conditions; a reviewer must verify the changes before implementation:

1. JavaScript sets `form.noValidate` only after attaching the form controller, retaining native constraints without JavaScript.
2. The server accepts only exact `YYYY-MM-DD` values and evaluates dates in configurable `APP_TIMEZONE`, defaulting to `UTC`.
3. Server-side validation is mandatory before parsing or persistence.
4. The implementation must add `pytest`, Playwright, targeted tests, and CI validation commands.

## Planning Readiness

The required source artifacts are present. The amended design requires a re-review before implementation planning can be approved.

## Implementation Plan

- **Plan:** [implementation_plan.md](implementation_plan.md)
- **File count:** 10 files (7 new, 3 modified)
- **Dependency waves:** 5
- **Execution mode:** Dependency-ordered implementation with required local and CI verification.
- **Key risks:** Browser/server date-boundary differences, native constraint-event handling, global in-memory test isolation, and the existing hard-coded Flask secret.
- **Review conditions:** Satisfied by design specification version 1.1 and the follow-up review decision; non-blocking operational risks remain tracked.