import os

RESULTS_DIR = os.environ.get("RESULTS_DIR", "results")
MATCH_DIR = os.environ.get("MATCH_DIR", "Match")
LIBRARY_RESULT_DIR = os.environ.get("LIBRARY_RESULT_DIR", "LibraryResult")
COMPARE_RESULT_DIR = os.environ.get("COMPARE_RESULT_DIR", "CompareResult")
CLIENT_DIR = os.environ.get("CLIENT_DIR", "cleint")

def path(*args):
    return os.path.join(*args)
