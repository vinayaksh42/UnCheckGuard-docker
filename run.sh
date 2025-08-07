#!/bin/bash
set -e

# Optional: Recompile Java project
# echo "[INFO] Compiling Java project with Maven..."
# mvn clean package

mkdir -p "$RESULTS_DIR" "$MATCH_DIR" "$LIBRARY_RESULT_DIR" "$COMPARE_RESULT_DIR" "$CLIENT_DIR"


# Argument dispatcher
if [[ "$1" == "analyzeClient" ]]; then
    if [[ $# -ne 3 ]]; then
        echo "[ERROR] Usage: docker run ... find <clientRepo> <commitHash>"
        exit 1
    fi
    echo "[INFO] Running targeted analysis..."
    cd scripts
    python3 findUCBBC.py "$2" "$3"

elif [[ "$1" == "run" || $# -eq 0 ]]; then
    echo "[INFO] Running full research pipeline..."
    cd scripts
    python3 scriptRunner.py "$2"

else
    echo "[ERROR] Unknown command: $1"
    echo "Usage:"
    echo "  docker run ... run  <file.txt>          # Full pipeline"
    echo "  docker run ... find <repo> <commit>     # Targeted analysis"
    exit 1
fi
