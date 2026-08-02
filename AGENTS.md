# Codex Instructions

This repository is a static Chinese Quran search platform with generated datasets. Treat Quran translation text as sensitive source material.

## Validate

Run this before proposing or landing changes:

```bash
python3 scripts/validate_project.py
```

For generated artifacts, also run the relevant generator:

```bash
python3 ssr_generator.py
python3 generate_rag_dataset.py
python3 scripts/validate_project.py
```

## Editing rules

- Do not edit translation data without source evidence in the PR or issue.
- Keep `pc/` and `mobile/` behavior aligned.
- Avoid adding build systems, package managers, trackers, or external services unless the benefit is clear.
- Keep the site usable as static files and through a simple HTTP server.
- Prefer standard-library Python for maintenance scripts.
- Do not commit secrets, analytics tokens, or private credentials.

## Review focus

- Data completeness: five translators, 114 surahs, 6,236 ayahs each.
- Search safety: user input must not create executable HTML.
- Accessibility: controls should be usable on mobile and desktop.
- Deployment: GitHub Actions should use least-privilege permissions.
- Documentation: claims about copyright, religious authority, or adoption must be truthful and sourced.
