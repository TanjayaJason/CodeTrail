# CodeTrail

> A guided learning path through an unfamiliar codebase.

New contributors often do not know which files, concepts, and execution paths to study first in an unfamiliar repository.

## Why this project

Developers onboarding to open-source projects, students learning from code, and maintainers creating contributor guides.

CodeTrail is a portfolio project focused on a narrow, demonstrable workflow: useful AI assistance with visible evidence, predictable limits, and a clear local-first story.

## Product snapshot

- **Input:** Local repository path, optional learning goal (for example: understand API routing).
- **Output:** Repository map, learning steps, prerequisite links, referenced files/symbols, and suggested exploration questions.
- **MVP:** Scan a local Git repository, map its entry points and key modules, and generate an ordered learning path with file and symbol references plus short explanations.

## Planned architecture

Discover repository metadata and ignore rules first. Build a bounded index of tracked text files, symbols, imports, and project instructions. Select a small set of files for the chosen learning goal. Generate a structured learning path with every step tied to file/symbol anchors. Validate all paths against the repository and label inferred relationships. Default to local-only mode; remote model use must be explicit.

## Current status

**Planning scaffold.** The product requirements, design, project skill, and agent guidance are in place. Application implementation has not started.

## Getting started

The MVP is planned for Python 3.11+. Clone this repository and review the product and design docs before implementation. Runtime setup instructions will be added with the first working release.

For local LLM configuration, copy the variable names from .env and add your own values. .env is intentionally ignored by Git; never commit API keys.

## Roadmap

1. Implement the smallest end-to-end MVP described in the PRD.
2. Add representative fixtures and quality checks.
3. Document setup, limitations, and a short demo.
4. Revisit optional integrations only when they solve a demonstrated need.

## Safety and privacy

Prompt injection in source comments/docs, large repositories, unsupported languages, inaccurate dependency maps, and exposing private code to external APIs.

The design defaults to local processing where practical and minimizes what is sent to external model providers. Do not use real sensitive data in examples or screenshots.

## Project documents

- [Product requirements](docs/PRD.md)
- [Technical design](docs/DESIGN.md)
- [Project skill](.agents/skills/codetrail/SKILL.md)
- [Agent guidance](AGENTS.md)

## License

License not selected yet.
