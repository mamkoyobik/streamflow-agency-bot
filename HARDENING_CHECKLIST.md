# Hardening Checklist (TG + WhatsApp)

Use this checklist on every feature/change before deploy.

## 1) Input/Validation Safety
- Validate and normalize all user fields through shared rules (`application_rules.py`).
- Enforce length limits on every text field.
- Enforce age 18+ via birthdate check.
- Reject unsupported media/input types with safe fallback response.

## 2) State Machine Safety
- Handle stale callbacks safely (no crashes, return to valid menu).
- For each step, define behavior for invalid text/photo/button.
- Ensure restart/reset commands always recover flow.

## 3) Transport/API Safety
- Keep webhook auth checks enabled (`INFOBIP_WEBHOOK_SECRET`).
- Keep rate-limit responses (`429` + `Retry-After`) for public API endpoints.
- Keep idempotency/deduplication on inbound webhook events.

## 4) Persistence Safety
- Persist state atomically and recover from partial state.
- Keep source marker (`telegram`/`site`/`whatsapp`) and stage marker (`quick`/`full`) consistent.
- Never trust client-side values without server re-validation.

## 5) Operational Safety
- Run quality gate before every push:
  - `python3 scripts/quality_gate.py`
- Deploy only if quality gate is green.
- After deploy, verify:
  - TG `/start`, menu, submit flow
  - WhatsApp start/menu/submit flow
  - Admin approve/reject/menu callbacks
  - Cross-post publish to all language channels

## 6) Incident Safety
- On runtime exception: keep bot alive, send safe user fallback, log traceback.
- On external API failure: retry where safe, fail gracefully where not safe.
- On unknown input: do not drop session, show guided next step.
