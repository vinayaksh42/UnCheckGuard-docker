
#!/usr/bin/env python3
"""
summarize_results.py

Reads an UnCheckGuard results CSV and prints summary metrics.
Optionally writes a JSON summary file.

Usage:
  python summarize_results.py --csv ./results/results.csv --out ./results/summary.json
"""
import argparse
import json
from pathlib import Path

import pandas as pd


def summarize(df: pd.DataFrame) -> dict:
    # Normalize column names for easy access
    # We'll keep original names with spaces as they appear in CSV
    col_lib_old = "LibraryOld"
    col_client = "ClientName"
    col_owner_repo = "OwnerRepo"
    col_matched = "NumberOfMatchedMethods"
    col_usage = "Number of Times the Library is Used in the Client"

    # 1) Count of libraries analyzed = unique LibraryOld
    libraries_analyzed = int(df[col_lib_old].nunique())

    # 2) Count unique (ClientName, LibraryOld) pairs
    client_library_pairs = int(df[[col_client, col_lib_old]].drop_duplicates().shape[0])

    # 3) Total NumberOfMatchedMethods (sum)
    total_matched_methods = int(df[col_matched].fillna(0).astype(int).sum())

    # 4) Libraries with >0 matched methods (unique LibraryOld among rows with >0)
    libs_with_bbc = int(
        df.loc[df[col_matched].fillna(0).astype(int) > 0, col_lib_old].nunique()
    )

    # 5) Total "Number of Times the Library is Used in the Client" (sum)
    total_library_usage = int(df[col_usage].fillna(0).astype(int).sum())

    # 6) Total number of unique clients
    unique_clients_by_ownerrepo = int(df[col_owner_repo].nunique())
    unique_clients_by_clientname = int(df[col_client].nunique())

    return {
        "libraries_analyzed": libraries_analyzed,
        "client_library_pairs": client_library_pairs,
        "total_matched_methods": total_matched_methods,
        "libraries_with_potential_bbc": libs_with_bbc,
        "total_library_usage_calls": total_library_usage,
        "unique_clients_by_ownerrepo": unique_clients_by_ownerrepo,
        "unique_clients_by_clientname": unique_clients_by_clientname,
    }


def main():
    ap = argparse.ArgumentParser(description="Summarize UnCheckGuard results CSV.")
    ap.add_argument("--csv", required=True, help="Path to results.csv")
    ap.add_argument("--out", help="Optional path to write JSON summary")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    summary = summarize(df)

    # Pretty print to stdout
    print("\n=== UnCheckGuard Run Summary ===")
    for k, v in summary.items():
        print(f"{k}: {v}")

    # Optionally write JSON
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(summary, indent=2))
        print(f"\nSaved JSON summary to: {out_path}")

if __name__ == "__main__":
    main()
