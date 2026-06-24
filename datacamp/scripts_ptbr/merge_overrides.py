# -*- coding: utf-8 -*-
"""Mescla traducoes PT (overrides) nos arquivos gerados pelo futurecoder.
Idempotente. Rodar antes do npm build (ou via build_ptbr.sh)."""
import json
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / ".futurecoder-src" / "frontend" / "src"
OVR = Path(__file__).resolve().parents[1] / ".futurecoder-src" / "translations" / "pt_overrides"


def merge_terms():
    terms_path = SRC / "terms.json"
    ovr_path = OVR / "terms_br.json"
    if not (terms_path.exists() and ovr_path.exists()):
        return 0
    terms = json.loads(terms_path.read_text(encoding="utf-8"))
    ovr = json.loads(ovr_path.read_text(encoding="utf-8"))
    n = 0
    for k, v in ovr.items():
        if v and terms.get(k) != v:
            terms[k] = v
            n += 1
    terms_path.write_text(json.dumps(terms, ensure_ascii=False, indent=1), encoding="utf-8")
    return n


def merge_pages():
    pages_path = SRC / "book" / "pages.json.load_by_url"
    ovr_path = OVR / "pages_br.json"
    if not (pages_path.exists() and ovr_path.exists()):
        return 0
    pages = json.loads(pages_path.read_text(encoding="utf-8"))
    ovr = json.loads(ovr_path.read_text(encoding="utf-8"))
    n = 0

    def walk(obj):
        nonlocal n
        if isinstance(obj, dict):
            for key in ("text", "final_text"):
                t = obj.get(key)
                if isinstance(t, str) and t in ovr and ovr[t]:
                    obj[key] = ovr[t]
                    n += 1
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(pages)
    pages_path.write_text(json.dumps(pages, ensure_ascii=False), encoding="utf-8")
    return n


if __name__ == "__main__":
    print("terms mesclados:", merge_terms())
    print("pages mescladas:", merge_pages())
