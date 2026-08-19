# Design Review: EPMCDMETST-60216

## Meta

- **Reviewer:** GitHub Copilot (DesignReview)
- **Date:** 2026-08-20
- **Ticket:** EPMCDMETST-60216
- **Mode:** B - artifact and code validation
- **Inputs:** [problem specification](docs/artifacts/EPMCDMETST-60216/problem_spec.md), [design specification](docs/artifacts/EPMCDMETST-60216/design_spec.md), application source, template, stylesheet, and README.
- **Repository snapshot:** branch `main`, commit `1332727c5b868ad86e721a8629e04acef9572e78`.
- **Tools used:** workspace file reads, file discovery, VS Code diagnostics, and Git metadata reads.
- **Scoring rubric:** each dimension is scored from 0 (unacceptable) to 5 (fully addressed). Weighted overall: Architecture 20%, Correctness 25%, Security 20%, Performance 10%, Testability 15%, Maintainability 10%. Gate mapping: >=4 Pass, 3-3.9 Conditional, <3 Fail.
- **Scores:** Architecture 3/5; Correctness 1/5; Security 3/5; Performance 5/5; Testability 1/5; Maintainability 3/5. **Weighted overall: 2.4/5 (Fail).**

## Summary

The design appropriately keeps validation form-scoped, preserves the request contract, and adds an essential server-side validation boundary missing from the current application. However, its explicit requirement to retain native `required` validation while relying only on a `submit` handler prevents custom validation from running for native constraint-invalid submissions. The design therefore cannot reliably satisfy the inline-error, ARIA, and focus acceptance criteria. Resolve the blocking client event-flow decision, define the server date policy, and select executable test tooling before implementation approval.

## Codebase Validation

Read-only checks performed:

```text
VS Code diagnostics:
- main.py: no errors found
- templates/index.html: no errors found
- static/style.css: no errors found

Test/tooling discovery:
- No test_*.py, *_test.py, pytest.ini, pyproject.toml, requirements*.txt,
  package.json, Playwright configuration, tox.ini, lint configuration, or CI workflow found.
```

The review environment did not expose a workspace terminal command runner, so Python compilation, Flask route execution, browser tests, and a dependency scan could not be run. The absence of discovered test/tooling files is not a passing runtime result.

Relevant implementation evidence: the authenticated `POST /` path accesses both request fields by key, splits and integer-converts the date, then appends the item without validation ([main.py](main.py#L59-L92)). The current form retains only native `required` constraints and no custom error/script hooks ([templates/index.html](templates/index.html#L40-L44)).

## Findings

### Architecture

1. **[High] The client-validation control flow conflicts with native constraint validation.** The design requires `required` on both controls and says not to set `novalidate` ([design specification](docs/artifacts/EPMCDMETST-60216/design_spec.md#L51-L53), [implementation guidance](docs/artifacts/EPMCDMETST-60216/design_spec.md#L143-L146)), while the controller attaches only a `submit` handler ([controller design](docs/artifacts/EPMCDMETST-60216/design_spec.md#L63-L65)). For a native constraint-invalid form, the browser can block submission before dispatching `submit`. Consequently, the handler cannot consistently render both controlled error messages, set `aria-invalid`/`aria-describedby`, or focus the first invalid field. This breaks the proposed sequence and acceptance criteria.

   **Required remediation:** choose and specify one complete event model. The simplest is to preserve semantic `required` attributes but set `form.noValidate = true` when the controller initializes, then perform all validation and rendering in the submit handler; without JavaScript, native validation and the server fallback remain active. Alternatively, define an `invalid` capture-phase implementation that renders all fields, controls focus, and prevents duplicate native messaging. Add browser coverage for empty controls to prove the selected model.

2. **[Medium] The server-side date parser is insufficiently specified as a wire-format enforcement rule.** The design calls for a strict calendar-date parser but does not state the exact accepted grammar or a required round-trip check for the server ([server validation](docs/artifacts/EPMCDMETST-60216/design_spec.md#L101-L110)); the contract says the wire format is `YYYY-MM-DD` ([HTTP contract](docs/artifacts/EPMCDMETST-60216/design_spec.md#L133-L140)). Direct requests can bypass native controls. Define server acceptance as an exact four-digit-year, two-digit-month, two-digit-day format followed by a calendar parse, and reject every other representation before persistence.

### Correctness

3. **[High] The authoritative date-comparison policy remains ambiguous at the client/server boundary.** The browser must judge dates using the user's local date, while the proposed server path uses the server's local date unless another policy is created ([controller date rule](docs/artifacts/EPMCDMETST-60216/design_spec.md#L76-L83), [server validation](docs/artifacts/EPMCDMETST-60216/design_spec.md#L105-L106)). Near midnight or across time zones, a browser-accepted request may be server-rejected, or the reverse. The design itself records this as unresolved ([flags](docs/artifacts/EPMCDMETST-60216/design_spec.md#L255-L258)).

   **Required remediation:** formally select an application time zone, make it configurable, use it for all server comparisons and dashboard date presentation, and document the expected difference from the browser-local preflight. Add boundary tests around midnight in a non-server client time zone.

4. **[High] Current direct POST behavior is unsafe, and implementation must include the specified server change.** The current route directly indexes potentially absent fields and manually converts date fragments before appending ([main.py](main.py#L63-L82)). A missing or malformed direct request can raise `KeyError` or `ValueError`; whitespace names are persisted. The design recognizes this as blocking ([flags](docs/artifacts/EPMCDMETST-60216/design_spec.md#L250-L254)), but it must be an explicit in-scope prerequisite rather than an optional compatibility flag.

   **Required remediation:** make server validation a required deliverable: use safe form lookups, construct the field-error map before parsing or mutation, re-render the authenticated dashboard with submitted values, and assert item count remains unchanged on every rejection path.

### Security

5. **[Medium] The design correctly identifies the existing hard-coded session secret but leaves its operational resolution outside the implementation gate.** The application assigns a source-controlled secret ([main.py](main.py#L7-L8)); the design marks this as a separate deployment risk ([security controls](docs/artifacts/EPMCDMETST-60216/design_spec.md#L240-L242)). This ticket need not broaden into a credentials redesign, but production release should not proceed until the secret is environment-managed and dependency metadata supports the recommended security scan.

### Performance

No material performance concern found. The proposed static, deferred, form-scoped script and synchronous local validation are proportionate to this small form ([dashboard template](docs/artifacts/EPMCDMETST-60216/design_spec.md#L57-L59), [controller design](docs/artifacts/EPMCDMETST-60216/design_spec.md#L63-L65)). Score: **5/5**.

### Testability

6. **[High] Required test coverage is named but not executable because no test stack, dependency manifest, or CI configuration exists.** The design correctly lists route and browser assertions ([testing strategy](docs/artifacts/EPMCDMETST-60216/design_spec.md#L170-L223)), but leaves runner selection and setup for later ([quality gates](docs/artifacts/EPMCDMETST-60216/design_spec.md#L224-L237)). Discovery confirmed none of the expected test/configuration files. The acceptance criteria, especially focus order, ARIA relationship updates, and no-overflow behavior, cannot be objectively signed off without concrete tooling.

   **Required remediation:** define and include the Python test runner, browser runner, dependency manifest, scripts/commands, and CI workflow in the implementation plan. At minimum, add direct Flask POST tests for all rejection and success paths plus browser tests for the native-invalid event path selected in Finding 1.

### Maintainability

7. **[Low] The design leaves the dashboard date-display source inconsistent with the new authoritative validation clock.** `curr_day` and its component globals are computed at module import ([main.py](main.py#L17-L26)), while the design proposes a current server date for POST validation. A long-running process can display yesterday's heading while applying today's validation rule. This is not introduced by the ticket, but it becomes visible once the feature makes date rules explicit.

   **Recommended remediation:** calculate the display date and validation date from the same application-clock helper per request, or document why they intentionally differ. Keep this focused and avoid changing persistence behavior.

## Sign-Off

**Reviewer:** GitHub Copilot (DesignReview)

**Formal decision: Fail.** Do not begin implementation against the current specification. Amend the design to resolve Finding 1's native-validation event model, convert server validation into a mandatory scope item with an exact wire-format and time-zone policy, and commit to an executable Flask/browser test setup. Re-review is recommended after those decisions are incorporated; the existing progressive-enhancement, accessibility-state, and fixed-message direction can then proceed with a focused implementation.

## Follow-Up Review

**Date:** 2026-08-20
**Reviewed design version:** 1.1

The amended design resolves each blocking finding from this review:

1. The client controller preserves HTML `required` attributes but sets `form.noValidate = true` only after JavaScript attaches. The submit handler therefore controls all JavaScript-enabled submissions, while browser-native validation remains available without JavaScript.
2. The server accepts only values matching exact `YYYY-MM-DD` grammar and a successful calendar parse. It evaluates dates using configurable `APP_TIMEZONE`, defaulting to `UTC`, and explicitly documents browser/server boundary behavior.
3. Server-side validation before parsing and persistence is now mandatory ticket scope.
4. The implementation must add `pytest`, Playwright, their targeted test suites, and CI commands that execute both suites.

The hard-coded Flask secret and inaccurate README entry-point reference remain non-blocking risks outside this validation feature's core behavior. Their disposition must be recorded before production release and in normal documentation maintenance, respectively.

**Follow-up decision: Pass with non-blocking operational risks.** Implementation planning may proceed, provided the plan includes every required test, CI, server-validation, and browser-validation deliverable from design specification version 1.1.
