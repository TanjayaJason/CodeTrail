# Agent instructions

You are the CodeTrail project agent. Build a read-only repository learning-path generator. Read docs/PRD.md and docs/DESIGN.md before implementation. Respect ignore rules, never execute code from scanned repositories, and validate every reference. Make remote inference explicit. Never commit scanned repositories or .env.

## Repository conventions

- Treat docs/PRD.md as the scope boundary and docs/DESIGN.md as the current technical plan.
- Keep changes focused and explain any departure from those documents.
- Do not add secrets, private user data, or generated large artifacts.
- Do not claim features work until they are implemented and verified.

## Current owner preference

Local tests and dependency installation are authorized. Do not make live LLM calls. Record the checks actually run in README and STATUS.md; keep live model behavior marked unverified. Synthetic examples are allowed; never commit user input or real personal data.
