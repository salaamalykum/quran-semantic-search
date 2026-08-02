# Codex for Open Source Application Support

This document maps the repository to the public Codex for Open Source review criteria and provides concise draft answers for the application form.

## Project qualification

`salaamalykum/quran-semantic-search` is a public, free, non-profit Chinese Quran search platform. It gives Chinese-language Muslims, educators, imams, and researchers side-by-side access to five major Chinese translations with offline-capable PC and mobile interfaces.

The project matters even if it is not a conventional developer dependency: it preserves and operationalizes an important Chinese Islamic digital humanities corpus, serves a global Chinese-reading Muslim community, and is intentionally free of ads and paywalls.

## Repository usage and ecosystem importance

- Public GitHub repository: `https://github.com/salaamalykum/quran-semantic-search`
- Live PC entry: `https://salaamalykum.com/cn/qurancn/pc/`
- Live mobile entry: `https://salaamalykum.com/cn/qurancn/mobile/`
- Five Chinese Quran translation datasets with 6,236 records each; known empty source gaps are documented in `docs/DATA_PROVENANCE.md`.
- Static architecture that can be mirrored by mosques, schools, study groups, and low-bandwidth communities.
- JSONL/RAG artifacts useful for Chinese religious-language search, retrieval, and evaluation research.

## Active maintenance evidence now visible in the repository

- `CONTRIBUTING.md`: contribution workflow, data correction evidence standard, release process.
- `SECURITY.md`: vulnerability reporting and security review scope.
- `MAINTAINERS.md`: maintainer role and responsibilities.
- `ROADMAP.md`: near-term reliability and data-provenance priorities.
- `.github/ISSUE_TEMPLATE/`: structured bug, feature, and data-correction intake.
- `.github/workflows/validate.yml`: deterministic validation on pull requests and pushes.
- `scripts/validate_project.py`: corpus coverage, known-gap, and generated artifact checks.
- `CHANGELOG.md`: release-note surface for ongoing maintenance.

## How Codex credits would be used

Codex would reduce the maintainer burden in work that directly benefits the public project:

- pull request review and risk summaries,
- issue triage and reproducible bug reports,
- release notes and changelog drafting,
- JavaScript search safety review,
- generated HTML/data validation improvements,
- documentation consistency checks,
- maintenance automation for GitHub Actions and static deployment.

Human maintainers will continue to review religious text, source provenance, licensing, and final release decisions.

## Why this benefits OpenAI

- Demonstrates Codex supporting a real non-profit, non-English, faith/community OSS project.
- Shows Codex value beyond mainstream infrastructure repositories: cultural preservation, accessibility, and digital humanities.
- Produces concrete examples of Codex-assisted PR review, issue triage, release workflow, and security hardening.
- Helps keep a public-interest project free while improving quality, safety, and maintainability.
- Provides a challenging multilingual search/data-maintenance case where correctness matters.

## Codex Security fit

The site is static, but security still matters because generated HTML renders religious text at scale and community mirrors may reuse the repository. Useful checks include XSS risks in search highlighting, generated HTML escaping, GitHub Actions permissions, dependency-free script safety, and data-integrity protections.

## Draft application answers

### Role

Primary maintainer of `salaamalykum/quran-semantic-search`: I maintain the code, data pipeline, public deployment, issue triage, documentation, release quality, and community-facing support for this free non-profit Chinese Quran search platform.

### Why does this repository qualify? (500 characters max)

Free non-profit Chinese Quran search platform serving Chinese-reading Muslims, educators, imams, and researchers worldwide. It preserves five major Chinese translation datasets in a searchable, offline-capable PC/mobile site, with documented source gaps and open RAG/JSONL artifacts for Chinese religious-language research.

### How will you use API credits? (500 characters max)

Use Codex/API credits for OSS maintenance: PR review, issue triage, release notes, security review of static JS/SSR HTML, validation automation, data-provenance tooling, and low-cost semantic-search experiments. Human maintainers will review all Quran text, licensing, and release decisions.

### Anything else? (500 characters max)

This project is intentionally ad-free, paywall-free, and non-profit. Server and maintenance costs are borne personally so Chinese-language Muslims and researchers can access the tool anywhere. Codex support would directly improve reliability, safety, and maintainer capacity for a public-interest religious OSS project.
