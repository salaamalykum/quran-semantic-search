#!/usr/bin/env python3
"""Validate the static Quran search corpus and generated artifacts."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRANSLATORS = [
    ("mazhonggang", "马仲刚"),
    ("majinpeng", "马金鹏"),
    ("tongdaozhang", "仝道章"),
    ("wangjingzhai", "王静斋"),
    ("majian", "马坚"),
]
TOTAL_SURAHS = 114
EXPECTED_AYAHS = 6236
KNOWN_EMPTY_TEXT = {
    ("majinpeng", 53, 14),
    ("majinpeng", 70, 30),
    ("majinpeng", 78, 22),
    ("majinpeng", 80, 35),
    ("majinpeng", 80, 36),
    ("majinpeng", 83, 5),
    ("majinpeng", 84, 17),
    ("majinpeng", 84, 18),
    ("majinpeng", 89, 7),
    ("majinpeng", 94, 3),
    ("majinpeng", 96, 10),
    ("tongdaozhang", 24, 7),
}


def load_json(path: Path, errors: list[str]):
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        errors.append(f"Missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")
    return None


def validate_translation_file(
    surface: str,
    key: str,
    label: str,
    errors: list[str],
    observed_empty: set[tuple[str, int, int]],
):
    path = ROOT / surface / "data" / f"{key}.json"
    data = load_json(path, errors)
    if data is None:
        return None
    if not isinstance(data, list):
        errors.append(f"{path.relative_to(ROOT)} must contain a JSON array")
        return None
    if len(data) != EXPECTED_AYAHS:
        errors.append(
            f"{path.relative_to(ROOT)} has {len(data)} records; expected {EXPECTED_AYAHS}"
        )

    seen: set[tuple[int, int]] = set()
    surahs: set[int] = set()
    sample_errors = 0
    for idx, rec in enumerate(data):
        prefix = f"{path.relative_to(ROOT)}[{idx}]"
        if not isinstance(rec, dict):
            errors.append(f"{prefix} must be an object")
            continue
        sura = rec.get("sura")
        aya = rec.get("aya")
        text = rec.get("text")
        translator = rec.get("translator")

        if not isinstance(sura, int) or not 1 <= sura <= TOTAL_SURAHS:
            errors.append(f"{prefix} has invalid sura: {sura!r}")
            sample_errors += 1
        else:
            surahs.add(sura)

        if not isinstance(aya, int) or aya < 1:
            errors.append(f"{prefix} has invalid aya: {aya!r}")
            sample_errors += 1

        if isinstance(sura, int) and isinstance(aya, int):
            pair = (sura, aya)
            if pair in seen:
                errors.append(f"{path.relative_to(ROOT)} duplicates {sura}:{aya}")
                sample_errors += 1
            seen.add(pair)

        if not isinstance(text, str) or not text.strip():
            if isinstance(sura, int) and isinstance(aya, int):
                observed_empty.add((key, sura, aya))
            if not isinstance(sura, int) or not isinstance(aya, int) or (key, sura, aya) not in KNOWN_EMPTY_TEXT:
                errors.append(f"{prefix} has empty text")
                sample_errors += 1

        if translator != label:
            errors.append(f"{prefix} translator is {translator!r}; expected {label!r}")
            sample_errors += 1

        if sample_errors >= 20:
            errors.append(f"{path.relative_to(ROOT)} has more record errors; stopping sample")
            break

    if len(seen) != EXPECTED_AYAHS:
        errors.append(
            f"{path.relative_to(ROOT)} has {len(seen)} unique ayah keys; expected {EXPECTED_AYAHS}"
        )
    if surahs != set(range(1, TOTAL_SURAHS + 1)):
        missing = sorted(set(range(1, TOTAL_SURAHS + 1)) - surahs)
        extra = sorted(surahs - set(range(1, TOTAL_SURAHS + 1)))
        errors.append(
            f"{path.relative_to(ROOT)} surah coverage mismatch; missing={missing[:10]}, extra={extra[:10]}"
        )
    return data


def validate_data_wrappers(surface: str, key: str, canonical_data, errors: list[str]) -> None:
    path = ROOT / surface / "data" / f"{key}.data.js"
    if not path.exists():
        errors.append(f"Missing data wrapper: {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    pattern = rf"window\.QDATA\[['\"]{re.escape(key)}['\"]\]\s*=\s*(\[.*\]);?\s*$"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        errors.append(f"{path.relative_to(ROOT)} does not assign window.QDATA['{key}']")
        return
    try:
        wrapped_data = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        errors.append(f"{path.relative_to(ROOT)} contains invalid wrapped JSON: {exc}")
        return
    if canonical_data is not None and wrapped_data != canonical_data:
        errors.append(f"{path.relative_to(ROOT)} does not match {key}.json")


def validate_sura_names(errors: list[str]) -> None:
    for surface in ("pc", "mobile"):
        path = ROOT / surface / "sura-names.js"
        if not path.exists():
            errors.append(f"Missing sura names file: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        match = re.search(r"window\.SURA_NAMES\s*=\s*(\{.*?\});", text, re.DOTALL)
        if not match:
            errors.append(f"{path.relative_to(ROOT)} does not assign window.SURA_NAMES")
            continue
        try:
            names = json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(ROOT)} has invalid SURA_NAMES JSON: {exc}")
            continue
        keys = {int(k) for k in names.keys() if str(k).isdigit()}
        if keys != set(range(1, TOTAL_SURAHS + 1)):
            errors.append(f"{path.relative_to(ROOT)} must define all 114 surah names")


def validate_generated_pages(errors: list[str]) -> None:
    for surface in ("pc", "mobile"):
        sura_dir = ROOT / surface / "sura"
        if not sura_dir.exists():
            errors.append(f"Missing generated surah directory: {sura_dir.relative_to(ROOT)}")
            continue
        files = sorted(sura_dir.glob("*.html"), key=lambda p: int(p.stem) if p.stem.isdigit() else 9999)
        expected_names = {f"{idx}.html" for idx in range(1, TOTAL_SURAHS + 1)}
        actual_names = {p.name for p in files}
        missing = sorted(expected_names - actual_names, key=lambda x: int(x.split(".")[0]))
        extra = sorted(actual_names - expected_names)
        if missing or extra:
            errors.append(
                f"{sura_dir.relative_to(ROOT)} page mismatch; missing={missing[:10]}, extra={extra[:10]}"
            )
        for idx in range(1, TOTAL_SURAHS + 1):
            path = sura_dir / f"{idx}.html"
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            if "application/ld+json" not in text:
                errors.append(f"{path.relative_to(ROOT)} missing JSON-LD metadata")
            if f"第 {idx} 章" not in text:
                errors.append(f"{path.relative_to(ROOT)} missing visible/generated surah title")


def validate_sitemap(errors: list[str]) -> None:
    path = ROOT / "sitemap.xml"
    if not path.exists():
        errors.append("Missing sitemap.xml")
        return
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        errors.append(f"Invalid sitemap.xml: {exc}")
        return
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = {loc.text for loc in tree.findall(".//sm:loc", ns) if loc.text}
    expected = {
        f"https://salaamalykum.com/cn/qurancn/{surface}/sura/{idx}.html"
        for surface in ("pc", "mobile")
        for idx in range(1, TOTAL_SURAHS + 1)
    }
    missing = sorted(expected - locs)
    extra = sorted(locs - expected)
    if missing or extra:
        errors.append(f"sitemap.xml mismatch; missing={missing[:5]}, extra={extra[:5]}")


def validate_jsonl(path: Path, required_keys: set[str], errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"Missing JSONL file: {path.relative_to(ROOT)}")
        return
    count = 0
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            count += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{path.relative_to(ROOT)}:{line_no} invalid JSON: {exc}")
                continue
            missing = required_keys - set(rec)
            if missing:
                errors.append(f"{path.relative_to(ROOT)}:{line_no} missing keys {sorted(missing)}")
            metadata = rec.get("metadata")
            if not isinstance(metadata, dict) or not isinstance(metadata.get("sura"), int) or not isinstance(metadata.get("aya"), int):
                errors.append(f"{path.relative_to(ROOT)}:{line_no} missing numeric metadata.sura/aya")
            if len(errors) >= 50:
                errors.append("Too many JSONL errors; stopping")
                break
    if count != EXPECTED_AYAHS:
        errors.append(f"{path.relative_to(ROOT)} has {count} records; expected {EXPECTED_AYAHS}")


def main() -> int:
    errors: list[str] = []
    observed_empty: set[tuple[str, int, int]] = set()
    datasets: dict[str, dict[str, list[dict]]] = {"pc": {}, "mobile": {}}

    for surface in ("pc", "mobile"):
        for key, label in TRANSLATORS:
            data = validate_translation_file(surface, key, label, errors, observed_empty)
            if data is not None:
                datasets[surface][key] = data
            validate_data_wrappers(surface, key, data, errors)

    for key, _label in TRANSLATORS:
        pc_data = datasets["pc"].get(key)
        mobile_data = datasets["mobile"].get(key)
        if pc_data is not None and mobile_data is not None and pc_data != mobile_data:
            errors.append(f"pc/data/{key}.json and mobile/data/{key}.json differ")

    validate_sura_names(errors)
    validate_generated_pages(errors)
    validate_sitemap(errors)
    validate_jsonl(ROOT / "quran_rag_dataset.jsonl", {"instruction", "context", "response", "metadata"}, errors)
    validate_jsonl(ROOT / "quran_rag_alpaca.jsonl", {"instruction", "input", "output", "metadata"}, errors)

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validation passed:")
    print(f"- {len(TRANSLATORS)} complete translator datasets")
    print(f"- {EXPECTED_AYAHS} ayahs per translator")
    print("- PC and mobile datasets match")
    print("- 228 generated surah pages referenced by sitemap.xml")
    print("- RAG JSONL artifacts are parseable")
    if observed_empty:
        print(f"- {len(observed_empty)} known empty translation records are documented data gaps")
    return 0


if __name__ == "__main__":
    sys.exit(main())
