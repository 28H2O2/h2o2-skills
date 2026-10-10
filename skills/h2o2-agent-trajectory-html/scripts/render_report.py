#!/usr/bin/env python3
"""Wrap validated H2O2 JSON into one offline HTML with escaped embedded JSON."""
import argparse
import json
from pathlib import Path
import copy
import re
from quality_check import check

HERE = Path(__file__).resolve().parent.parent

SECRET_RE = re.compile(r"(?i)(\b(?:API_KEY|SECRET_KEY|ACCESS_TOKEN|DB_PASSWORD|PASSWORD)\b\s*[:=]\s*[\"\']?)([^\s\"\',;<>]{6,})")

def redact_sensitive(value):
    if isinstance(value, str):
        # Conservative: redact *values* after explicit credential keys, never words/paths.
        return SECRET_RE.sub(lambda m: m.group(1) + "[REDACTED]", value)
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    if isinstance(value, dict):
        return {k: redact_sensitive(v) for k,v in value.items()}
    return value

def build(input_path, output_path, redact=True):
    data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    if not isinstance(data.get("cases"), list):
        raise ValueError("Expected top-level cases[]")
    errs,warns=check(data)
    if errs:
        raise ValueError('Report failed semantic QA: '+ '; '.join(errs[:5]))
    if warns:
        print(f'NOTICE: {len(warns)} semantic/editorial warnings; run scripts/quality_check.py --input ... to inspect them.')
    if redact:
        data = redact_sensitive(data)
    template = (HERE / "assets" / "report-template.html").read_text(encoding="utf-8")
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # Embed safely in <script type=application/json>; never interpolate raw logs into HTML.
    encoded = encoded.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e").replace("\u2028", "\\u2028")
    signature = (HERE / "assets" / "signature.html").read_text(encoding="utf-8")
    html = template.replace("__H2O2_REPORT_DATA__", encoded).replace("__H2O2_SIGNATURE__", signature)
    if html == template:
        raise ValueError("Missing template data marker")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(html, encoding="utf-8")
    return len(html.encode("utf-8"))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--no-redact", action="store_true", help="Unsafe unless the data is already reviewed and sanitized")
    a = ap.parse_args()
    print(f"Wrote {a.output} ({build(a.input, a.output, redact=not a.no_redact)} bytes)")
