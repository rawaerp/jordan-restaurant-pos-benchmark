"""Turn result files into a Markdown comparison table (MIT).

    python score.py results/

Only fields that were actually measured (not null) are shown; everything else prints "-".
A result is marked 'verified' only when its `evidence` field is non-empty. Files whose name starts
with "_" (the template) are ignored. The script never fills in or estimates anything.
"""
import json
import pathlib
import statistics
import sys


def load(folder):
    for p in sorted(pathlib.Path(folder).glob("*.json")):
        if p.name.startswith("_"):
            continue
        try:
            yield p.name, json.loads(p.read_text(encoding="utf-8"))
        except ValueError as e:
            print(f"skip {p.name}: {e}", file=sys.stderr)


def cell(v):
    return "-" if v is None else ("yes" if v is True else "no" if v is False else str(v))


def row(name, d):
    s1, s2, s3, s4, s5, s6 = (d.get(k) or {} for k in ("s1_offline", "s2_rush", "s3_printer", "s4_jofotara", "s5_arabic", "s6_setup"))
    offline = "-" if s1.get("offline_completed") is None else f"{s1['offline_completed']}/20"
    verified = "verified" if str(d.get("evidence") or "").strip() else "unverified"
    return [d.get("system", name), d.get("tested_on", "-"), d.get("relationship", "-"), verified, offline,
            cell(s1.get("missing_after_sync")), cell(s1.get("duplicates_after_sync")),
            cell(s2.get("median_seconds")), cell(s2.get("p95_seconds")),
            cell(s3.get("sale_kept")), cell(s4.get("cashier_blocked")),
            cell(s5.get("receipt_arabic_ok")), cell(s6.get("minutes_to_first_sale"))]


HEAD = ["System", "Date", "Tester is", "Evidence", "S1 offline", "S1 missing", "S1 dupes", "S2 median s", "S2 p95 s",
        "S3 sale kept", "S4 cashier blocked", "S5 Arabic ok", "S6 minutes"]

if __name__ == "__main__":
    rows = [row(n, d) for n, d in load(sys.argv[1] if len(sys.argv) > 1 else "results")]
    if not rows:
        print("No result files yet (the template is ignored).")
        sys.exit(0)
    print("| " + " | ".join(HEAD) + " |")
    print("|" + "---|" * len(HEAD))
    for r in rows:
        print("| " + " | ".join(r) + " |")
