# Security Policy

## Supported project surface

This is a static web application and dataset repository. Security-sensitive areas include:

- JavaScript search/highlighting logic in `pc/` and `mobile/`,
- generated SSR HTML under `pc/sura/` and `mobile/sura/`,
- GitHub Actions workflows,
- data files that are rendered into HTML,
- deployment configuration and documentation.

## Reporting a vulnerability

Please do not open a public issue for a vulnerability that could put users or maintainers at risk. Email `bropeace@protonmail.com` with:

- a short description,
- affected files or URLs,
- reproduction steps,
- impact,
- suggested mitigation if known.

The maintainer will acknowledge good-faith reports as soon as practical and prioritize fixes based on user impact.

## Security expectations

- No secrets, API keys, analytics tokens, or private credentials should be committed.
- GitHub Actions should use least-privilege permissions.
- User-provided search input must not be able to execute script.
- Generated HTML should escape dynamic text unless the source is intentionally trusted and documented.
- External links should use `rel="noopener noreferrer"` when opening new tabs.

## Why deeper security review matters

The project serves religious study and can be mirrored by community organizations. A compromised static site, poisoned dataset, or unsafe workflow could spread incorrect scripture text or expose maintainers. The repository is a good candidate for Codex-assisted review and, if available, conditional Codex Security coverage.
