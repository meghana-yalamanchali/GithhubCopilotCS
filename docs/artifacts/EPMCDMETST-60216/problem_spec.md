# Problem Specification: EPMCDMETST-60216

## Meta

- **Ticket:** EPMCDMETST-60216
- **Title:** Registered user: Validate todo task form with inline, accessible error messages
- **Status:** Approved specification
- **Source:** Jira ticket description. The linked Confluence page (2909540185) was unavailable because the configured credentials were unauthorized.
- **Date:** 2026-08-20

## Problem Statement

Authenticated users need immediate, accessible feedback when submitting incomplete or invalid Add Task form data. The application must validate task name and due date on form submission, display field-specific inline errors, focus the first invalid field, and prevent invalid requests from reaching the server. Server-side validation remains the authoritative validation layer.

## Requirements

1. Validate the Add Task form when the user submits it.
2. Require a non-empty task name. Treat whitespace-only input as empty.
3. Require a due date that is a valid calendar date and strictly later than the user's local current calendar date.
4. When client-side validation fails, prevent form submission and focus the first invalid control in form order.
5. Render a clear inline error beside each invalid field.
6. Set `aria-invalid="true"` on each invalid control and associate it with its error message using `aria-describedby`.
7. Announce new or updated validation errors to assistive technologies through an appropriate ARIA live mechanism.
8. Clear a field's invalid state and its inline error when that field passes validation on a subsequent form submission.
9. Use the native HTML5 `date` input control for supported browsers.
10. Preserve the existing endpoint, HTTP method, submitted field names, valid-submission behavior, and server-side validation.
11. Preserve a functional no-JavaScript path using the existing server-rendered form behavior.
12. Ensure validation messages are visible and readable without horizontal scrolling on supported mobile viewports.

## Acceptance Criteria

1. Given an authenticated user submits the Add Task form with one or both required fields empty, when validation runs, then no request is submitted, each missing field shows an inline required-field error, and focus moves to the first invalid field.
2. Given a user submits a non-empty task name with an empty due date, when validation runs, then only the due-date field is marked invalid and displays its required-field error.
3. Given a user supplies a malformed or impossible due date, when validation runs, then no request is submitted and an inline error explains that a valid calendar date is required.
4. Given a user supplies a due date that is today or in the past, when validation runs, then no request is submitted and an inline error states that the due date must be later than today.
5. Given validation errors are visible, when a keyboard or screen-reader user interacts with the form, then every invalid control has `aria-invalid="true"`, references its error through `aria-describedby`, and error content is announced to assistive technologies.
6. Given all fields satisfy validation, when the form is submitted, then it follows the current server submission path unchanged.
7. Given JavaScript is unavailable, when the user submits the form, then the existing server-side behavior and form contract continue to function.
8. Given validation errors are rendered on a mobile viewport, when the user views the form, then the messages wrap within the layout and do not introduce horizontal scrolling.

## Constraints

- Client-side validation is progressive enhancement and must not replace server-side validation.
- The native HTML5 date control is the approved UI control; a custom date picker is out of scope.
- The client-side due-date comparison uses the user's local calendar date.
- The implementation must retain the established form route, request contract, and data persistence behavior.
- The linked Confluence source is currently inaccessible; this specification is based on the Jira ticket description and approved clarifications.
- The feature must work with keyboard navigation and common screen-reader interaction patterns.

## Non-Goals

1. Replacing the native HTML5 date control with a custom date picker or date parsing component.
2. Changing task persistence, authentication, authorization, task-list display, server routes, or the form request contract.
3. Adding asynchronous or server-backed validation before form submission.
4. Adding validation for task-name length, duplicate tasks, prohibited characters, descriptions, or other task properties not named in this ticket.
5. Redesigning the dashboard beyond the styling needed for accessible, mobile-readable errors.

## Assumptions

| Assumption | risk_if_wrong |
| --- | --- |
| “Later” means strictly later than the user's local current calendar date; today is invalid. | high |
| Native browser parsing and UI for `input[type="date"]` are sufficient for supported browsers. | medium |
| Browser-local date determines whether a selected due date is future-dated; server-time-zone normalization is not required for client-side feedback. | medium |
| Error copy is English-only and follows existing application wording because no localization system is identified. | low |
| Server-side validation is implemented by this ticket and remains authoritative for direct requests and the no-JavaScript path. | low |
| HTML `required` attributes remain present where applicable so browser and no-JavaScript behavior remain operable. | low |
| The inaccessible Confluence source contains no requirements beyond the Jira story and approved clarifications. | high |
| Rollout occurs through the next normal application deployment without a feature flag or data migration. | low |

## Edge Cases

1. Both required fields are blank: display both errors and focus task name first.
2. A browser-native date control rejects text before JavaScript receives a parseable date: use the control's validity state to show the valid-calendar-date error.
3. A browser permits entry of an impossible date such as February 30: block submission and display the valid-calendar-date error.
4. A previously invalid field becomes valid: remove its invalid ARIA state and associated error on the next validation run.
5. A task name contains only whitespace: treat it as missing.
6. Error messages are added or updated while a screen reader is active: make them programmatically discoverable from the relevant control and announce the change.
7. Error content is longer than the available mobile width: wrap it within the form without horizontal scrolling.

## Backward Compatibility

**Verdict: Compatible.** This is an additive client-side enhancement. It preserves the existing endpoint, HTTP behavior, field names, valid-submission flow, server-side validation authority, and no-JavaScript operation. No API, persistence, authentication, or migration changes are required.

## Glossary

- **Add Task form:** The authenticated user's dashboard form used to create a todo item.
- **Client-side validation:** Validation performed in the browser before a form request is sent.
- **Server-side validation:** Validation enforced by the application server; it remains the authoritative source of truth.
- **Inline error:** A field-specific validation message rendered adjacent to its related form control.
- **ARIA:** Accessible Rich Internet Applications attributes that expose state and relationships to assistive technologies.
- **ARIA live region:** A page region whose content updates are announced by assistive technologies.
- **No-JavaScript path:** The existing submission behavior available when browser JavaScript is disabled or unavailable.