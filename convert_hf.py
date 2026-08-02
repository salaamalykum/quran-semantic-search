#!/usr/bin/env python3
"""Convert the canonical RAG JSONL file to Alpaca-style JSONL."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "quran_rag_dataset.jsonl"
TARGET = ROOT / "quran_rag_alpaca.jsonl"


def main() -> int:
    written = 0
    with SOURCE.open("r", encoding="utf-8") as src, TARGET.open("w", encoding="utf-8") as dst:
        for line_no, line in enumerate(src, start=1):
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            converted = {
                "instruction": record["instruction"],
                "input": record.get("context", ""),
                "output": record["response"],
                "metadata": record.get("metadata", {}),
            }
            dst.write(json.dumps(converted, ensure_ascii=False) + "\n")
            written += 1
    print(f"Wrote {written} Alpaca records to {TARGET.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
