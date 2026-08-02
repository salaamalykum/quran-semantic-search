# Data Provenance and Correction Standard

This project presents five Chinese Quran translations side by side for search, comparison, education, and research. Because translation text is religiously and legally sensitive, data changes use a stricter standard than ordinary UI changes.

## Included translators

- Ma Jian / 马坚
- Ma Jinpeng / 马金鹏
- Wang Jingzhai / 王静斋
- Tong Daozhang / 仝道章
- Ma Zhonggang / 马仲刚

Each translator dataset should contain 6,236 ayah records covering surahs 1 through 114.

## Required fields

Each JSON record must keep this shape:

```json
{
  "sura": 1,
  "aya": 1,
  "text": "translation text",
  "translator": "translator display name"
}
```

## Correction evidence

A correction should include at least one credible source:

- printed edition page scan or bibliographic reference,
- official publisher or recognized institutional source,
- maintainer-approved source note,
- comparison against a previously verified project source.

The maintainer may reject or defer corrections that lack verifiable source evidence, even if the proposed text appears plausible.

## Validation invariants

The validation script checks:

- all five translator JSON files exist in `pc/data/` and `mobile/data/`,
- each file has 6,236 unique `(sura, aya)` records,
- surah range is 1 through 114,
- text is non-empty except for explicitly documented source gaps,
- PC and mobile datasets match exactly,
- generated SSR pages exist for all 114 surahs,
- `sitemap.xml` contains the expected generated page URLs,
- RAG JSONL files are parseable and aligned with the verse count.

Run:

```bash
python3 scripts/validate_project.py
```

## Known source gaps

The following records currently exist in both PC and mobile datasets but have empty translation text. They should not be filled without source evidence:

| Translator | Surah | Ayah |
| --- | ---: | ---: |
| 马金鹏 | 53 | 14 |
| 马金鹏 | 70 | 30 |
| 马金鹏 | 78 | 22 |
| 马金鹏 | 80 | 35 |
| 马金鹏 | 80 | 36 |
| 马金鹏 | 83 | 5 |
| 马金鹏 | 84 | 17 |
| 马金鹏 | 84 | 18 |
| 马金鹏 | 89 | 7 |
| 马金鹏 | 94 | 3 |
| 马金鹏 | 96 | 10 |
| 仝道章 | 24 | 7 |

## Licensing boundary

The software is MIT licensed. Translation text may be governed by separate rights. See `NOTICE` before reuse, publication, redistribution, or model training.
