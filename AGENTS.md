# AGENTS.md — Instructions for Codex (Repo Standard)

## Golden rules
- Minimal diffs, small coherent patches. No unrelated refactors.
- No guessing: never invent files/paths/APIs/packages. Verify in repo.
- No regressions: forms/routing/auth/analytics/SEO/i18n/conversion must not degrade.
- Security+privacy by default (OWASP mindset): no secrets, no PII logs, no unsafe HTML.
- A11y by default: semantic HTML, keyboard-first, visible focus, reduced motion.
- Performance by default: protect CLS/LCP/INP; optimize images; avoid bloat/3rd-party scripts.
- After EVERY patch: run Full Project Health Check (see below), then provide commit+push commands.

## Patch discipline
- Default max patch size: <= 8 files OR <= 300 changed lines.
- If exceeding is necessary: explain why and keep it as small as possible.

## Full Project Health Check (run after every patch)
Run repo-standard commands. If a command does not exist, locate the correct one in package.json/scripts or tooling docs.

Required categories:
1) typecheck
2) lint
3) format check
4) tests (unit/integration/e2e if present)
5) build (affected apps; prefer full workspace build when safe)
6) smoke run (dev/preview)
7) manual QA: mobile/tablet/desktop + keyboard-only + slow network + error cases
8) a11y tooling if present (or strict checklist)
9) perf tooling if present (or CWV-safe review + measurement plan)
10) security checks if present (audit/SAST) + baseline review

Do not proceed to next patch until failures are fixed.

## Proven cleanup (remove only what is truly unnecessary)
- Delete only with proof (tsc/eslint unused, dep graph/import tracing, build/tests evidence, repo docs).
- Never delete by “looks unused”.
- Protected unless proven safe: forms/routing/auth/analytics/security/a11y/i18n dynamic keys/observability.

## Branching + commits
- Use repo commit convention; fallback to Conventional Commits.
- If workflow unknown: work on feature branch codex/<slug>.
- After each patch, output commands:
  git status
  git diff
  git add -A (or specific paths)
  git commit -m "<message>"
  git push -u origin <branch>

## Repo map (fill in during first scan)
- Sites locations:
  - site1:
  - site2:
  - site3:
  - site4:
  - site5:
- Core UI package:
- Brand tokens source of truth:
- Analytics conventions:
- Auth/security conventions:
- Do-not-touch areas:
- How to run:
- How to test:
- How to build: