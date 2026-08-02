# Contributing

Thank you for helping maintain a free Chinese Quran search platform. The highest-impact contributions are data correctness reports, accessibility fixes, search quality improvements, documentation, and deployment reliability.

## Local setup

No package installation is required for normal validation. Use Python 3.9+:

```bash
python3 scripts/validate_project.py
```

For local browsing:

```bash
python3 -m http.server 8080
```

Then open `http://localhost:8080/pc/index.html` or `http://localhost:8080/mobile/index.html`.

## Contribution types

- **Data correction:** report the surah, ayah, translator, current text, proposed correction, and source evidence.
- **Bug fix:** include browser/device, steps to reproduce, expected behavior, and screenshots when useful.
- **Search/UI improvement:** explain the user workflow improved and test on both PC and mobile paths.
- **Documentation:** keep instructions reproducible and avoid overstating legal or religious authority.
- **Maintenance automation:** prefer deterministic scripts and GitHub Actions that do not require secrets.

## Pull request workflow

1. Fork the repository and create a focused branch.
2. Make the smallest practical change for the issue.
3. Run `python3 scripts/validate_project.py`.
4. Update documentation when behavior, data generation, or deployment changes.
5. Open a Pull Request using the template.

Maintainers review PRs for correctness, respect for source material, accessibility, performance on low-bandwidth devices, and license/provenance risk.

## Data correction policy

Translation text is sensitive. Do not edit Quran translation data based only on memory or preference. A data PR must include one of:

- a scan/photo/page reference from a recognized printed edition,
- an official publisher/source URL,
- a clear comparison with an already accepted source in this repository,
- or maintainer-approved provenance notes.

When in doubt, open an issue before editing data.

## Release process

Releases should include:

- the validation result from `scripts/validate_project.py`,
- user-visible changes,
- data/source changes and provenance notes,
- deployment notes for `pc/`, `mobile/`, SSR pages, and `sitemap.xml`,
- known limitations or follow-up issues.

## Codex-assisted maintenance

Codex is suitable for repeatable maintainer work in this repository:

- PR review checklists and risk summaries,
- issue triage and reproduction steps,
- release note drafting,
- search/UI refactors with validation,
- security review of static-site scripts and GitHub Actions,
- documentation consistency checks.

Codex output must still be reviewed by a human maintainer, especially for Quran text, religious explanation, licensing, and security changes.
