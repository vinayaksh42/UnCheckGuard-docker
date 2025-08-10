#!/bin/bash
set -Eeuo pipefail

# Default dirs if not provided by environment
: "${RESULTS_DIR:=/app/results}"
: "${MATCH_DIR:=/app/Match}"
: "${LIBRARY_RESULT_DIR:=/app/LibraryResult}"
: "${COMPARE_RESULT_DIR:=/app/CompareResult}"
: "${CLIENT_DIR:=/app/client}"

mkdir -p "$RESULTS_DIR" "$MATCH_DIR" "$LIBRARY_RESULT_DIR" "$COMPARE_RESULT_DIR" "$CLIENT_DIR"

print_usage() {
  echo "Usage:"
  echo "  docker run ... run  <file.txt>                # Batch Analysis"
  echo "  docker run ... analyzeClient <repo> <commit>  # Targeted Analysis"
}

summarize() {
  local csv="${RESULTS_DIR}/results.csv"
  local out="${RESULTS_DIR}/summary.json"
  if [[ -f "$csv" ]]; then
    echo "[INFO] Summarizing results at end of run..."
    python3 /app/scripts/summarize_results.py --csv "$csv" --out "$out" || {
      echo "[WARN] Summary script failed; continuing." >&2
    }
  else
    echo "[WARN] No results.csv found at ${csv}; skipping summary."
  fi
}

case "${1:-}" in
  ""|--help|-h|help)
    print_usage
    exit 0
    ;;

  analyzeClient)
    if [[ $# -ne 3 ]]; then
      echo "[ERROR] Wrong number of arguments for analyzeClient."
      print_usage
      exit 1
    fi
    echo "[INFO] Running targeted analysis for repo '$2' at commit '$3'..."
    rm -rf "$RESULTS_DIR"
    mkdir -p "$RESULTS_DIR"
    cd /app/scripts
    python3 -u findUCBBC.py "$2" "$3"
    summarize
    ;;

  run|"")
    if [[ "${1:-}" == "run" && $# -lt 2 ]]; then
      echo "[ERROR] Please provide the path to the repos list file."
      print_usage
      exit 1
    fi
    local_list_file="${2:-}"
    echo "[INFO] Running full research pipeline..."
    rm -rf "$RESULTS_DIR"
    mkdir -p "$RESULTS_DIR"
    cd /app/scripts
    python3 -u scriptRunner.py "$local_list_file"
    summarize
    ;;

  *)
    echo "[ERROR] Unknown command: $1"
    print_usage
    exit 1
    ;;
esac
