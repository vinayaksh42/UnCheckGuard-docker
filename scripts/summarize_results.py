
#!/usr/bin/env python3
"""
summarize_results.py

Reads an UnCheckGuard results CSV and prints summary metrics.
Also summarizes semantic-version change types (major/minor/patch)
for unique (LibraryOld, LibraryNew) pairs that have >0 matched methods.

Usage:
  python summarize_results.py --csv ./results/results.csv --out ./results/summary.json
"""
import argparse
import json
import re
from pathlib import Path
from typing import Tuple, Optional, Dict

import pandas as pd


COL_CLIENT = "ClientName"
COL_OWNER_REPO = "OwnerRepo"
COL_LIB_OLD = "LibraryOld"
COL_LIB_NEW = "LibraryNew"
COL_MATCHED = "NumberOfMatchedMethods"
COL_USAGE = "Number of Times the Library is Used in the Client"



def parse_name_and_version(s: str) -> Tuple[str, Tuple[int, int, int]]:
    """Try to split 'httpcore-4.4.16' -> ('httpcore', (4,4,16))."""
    if not isinstance(s, str):
        return str(s), (0, 0, 0)
    s = s.strip()

    # Greedy name, then a version like 1, 1.2, 1.2.3, 1.2.3.4
    m = re.match(r'^(?P<name>.+)-(?P<ver>\d+(?:\.\d+){0,3})(?:[._-]?[A-Za-z0-9]+)?$', s)
    if not m:
        # Sometimes artifacts look like group:artifact:version; try colon form
        m2 = re.match(r'^(?P<name>.+)[:](?P<artifact>.+)[:](?P<ver>\\d+(?:\\.\\d+){0,3}).*$', s)
        if m2:
            name = f"{m2.group('name')}:{m2.group('artifact')}"
            ver = m2.group('ver')
        else:
            return s, (0, 0, 0)
    else:
        name = m.group('name')
        ver = m.group('ver')

    parts = ver.split('.')
    # Ensure three numeric components
    nums = []
    for i in range(3):
        try:
            nums.append(int(parts[i]))
        except (IndexError, ValueError):
            nums.append(0)
    return name, tuple(nums)  # type: ignore


def semver_change_type(v_old: Tuple[int, int, int], v_new: Tuple[int, int, int]) -> str:
    if v_old != v_new:
        if v_new[0] != v_old[0]:
            return "major"
        if v_new[1] != v_old[1]:
            return "minor"
        if v_new[2] != v_old[2]:
            return "patch"
    return "none"


def summarize(df: pd.DataFrame) -> dict:
    # 1) Count of libraries analyzed = unique LibraryOld
    libraries_analyzed = int(df[COL_LIB_OLD].nunique())

    # 2) Count unique (ClientName, LibraryOld) pairs
    client_library_pairs = int(df[[COL_CLIENT, COL_LIB_OLD]].drop_duplicates().shape[0])

    # 3) Total NumberOfMatchedMethods (sum)
    total_matched_methods = int(df[COL_MATCHED].fillna(0).astype(int).sum())

    # 4) Libraries with >0 matched methods (unique LibraryOld among rows with >0)
    libs_with_bbc = int(
        df.loc[df[COL_MATCHED].fillna(0).astype(int) > 0, COL_LIB_OLD].nunique()
    )

    # 5) Total "Number of Times the Library is Used in the Client" (sum)
    total_library_usage = int(df[COL_USAGE].fillna(0).astype(int).sum())

    # 6) Total number of unique clients
    unique_clients_by_ownerrepo = int(df[COL_OWNER_REPO].nunique())
    unique_clients_by_clientname = int(df[COL_CLIENT].nunique())

    # --- SemVer summary for unique LibraryOld-LibraryNew pairs with >0 matched methods ---
    # Aggregate matched methods per (old,new) pair and keep only those with >0
    pair_agg = (
        df.groupby([COL_LIB_OLD, COL_LIB_NEW], dropna=False)[COL_MATCHED]
        .sum(min_count=1)
        .reset_index()
    )
    pair_agg[COL_MATCHED] = pair_agg[COL_MATCHED].fillna(0).astype(int)
    impactful_pairs = pair_agg.loc[pair_agg[COL_MATCHED] > 0].copy()

    semver_rows = []
    counts = {"major": 0, "minor": 0, "patch": 0, "none": 0, "unknown": 0}

    for _, row in impactful_pairs.iterrows():
        old = str(row[COL_LIB_OLD])
        new = str(row[COL_LIB_NEW])
        mm = int(row[COL_MATCHED])

        name_old, v_old = parse_name_and_version(old)
        name_new, v_new = parse_name_and_version(new)

        if v_old == (0, 0, 0) or v_new == (0, 0, 0):
            change = "unknown"
        else:
            change = semver_change_type(v_old, v_new)

        counts[change] = counts.get(change, 0) + 1
        semver_rows.append({
            "library_old": old,
            "library_new": new,
            "matched_methods_sum": mm,
            "parsed_old": {"name": name_old, "version": list(v_old)},
            "parsed_new": {"name": name_new, "version": list(v_new)},
            "change_type": change,
        })

    return {
        "libraries_analyzed": libraries_analyzed,
        "client_library_pairs": client_library_pairs,
        "total_matched_methods": total_matched_methods,
        "libraries_with_potential_bbc": libs_with_bbc,
        "total_library_usage_calls": total_library_usage,
        "unique_clients_by_ownerrepo": unique_clients_by_ownerrepo,
        "unique_clients_by_clientname": unique_clients_by_clientname,
        "semver_change_counts_for_pairs_with_matches": counts,
        "semver_changes_for_pairs_with_matches": semver_rows,
    }


def print_human(summary: Dict) -> None:
    print("\\n=== UnCheckGuard Run Summary ===")
    print(f"libraries_analyzed: {summary['libraries_analyzed']}")
    print(f"client_library_pairs: {summary['client_library_pairs']}")
    print(f"total_matched_methods: {summary['total_matched_methods']}")
    print(f"libraries_with_potential_bbc: {summary['libraries_with_potential_bbc']}")
    print(f"total_library_usage_calls: {summary['total_library_usage_calls']}")
    print(f"unique_clients_by_ownerrepo: {summary['unique_clients_by_ownerrepo']}")
    print(f"unique_clients_by_clientname: {summary['unique_clients_by_clientname']}")

    counts = summary["semver_change_counts_for_pairs_with_matches"]
    total_pairs = sum(counts.values())
    print("\\n--- Semantic Version Change Types (for LibraryOld→LibraryNew pairs with >0 matches) ---")
    print(f"total_pairs: {total_pairs}")
    for k in ["major", "minor", "patch", "none", "unknown"]:
        print(f"{k}: {counts.get(k,0)}")


def main():
    ap = argparse.ArgumentParser(description="Summarize UnCheckGuard results CSV (with SemVer breakdown).")
    ap.add_argument("--csv", required=True, help="Path to results.csv")
    ap.add_argument("--out", help="Optional path to write JSON summary")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    summary = summarize(df)

    # Pretty print to stdout
    print_human(summary)

    # Optionally write JSON
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(summary, indent=2))
        print(f"\\nSaved JSON summary to: {out_path}")

if __name__ == "__main__":
    main()
