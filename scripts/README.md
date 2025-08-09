# 📜 Scripts Overview

This folder contains Python scripts that make up the UnCheckGuard analysis pipeline.

## Script List

- **analysis_utils.py**  
  Save results, including combining match data into summary CSV files.

- **file_utils.py**  
  File and directory helper functions for creating, copying, and deleting files and folders.

- **findUCBBC.py**  
  Main driver script. Runs the complete pipeline for a single GitHub repository: clone → build → analyze old and new library versions → detect newly added unchecked exceptions → save results.

- **get_utils.py**  
  Utilities to clone a repository from GitHub, optionally checkout a specific commit, and retrieve the latest commit SHA.

- **matchResult.py**  
  Merges existing results CSV with match JSON files to produce a combined CSV.  
  *(Note: contains hardcoded file paths — mainly for offline merging.)*

- **maven_utils.py**  
  Helpers to find `pom.xml`, run Maven commands, and copy built artifacts and dependencies.

- **paths.py**  
  Central location for default directory paths used by the scripts.

- **scriptRunner.py**  
  Runs `findUCBBC.py` in batch mode for each repository listed in a text file.

- **searchMethodsToTest.py**  
  Matches client method calls to changed library methods to identify which client methods should be tested.

- **summarize_results.py**  
  Generates a summary from `results.csv`, reporting counts of libraries, client–library pairs, matched methods, potential BBC libraries, total library calls, and unique clients. Optionally outputs JSON.

- **transitiveException.py**  
  Analyzes two versions of a library (including dependencies) to find newly added unchecked exceptions.

