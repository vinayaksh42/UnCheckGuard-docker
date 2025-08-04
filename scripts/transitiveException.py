import json
import argparse
import subprocess
from collections import Counter
import glob
import os

def find_method_signature(data, method_signature):
    for class_methods in data:
        for methods in class_methods.values():
            for method in methods:
                if method['methodSignature'] == method_signature:
                    return method
    return None

def runAnalysisOnLibrary(libraryOld, libraryNew, matchedMethodsDir):
    libraryOldPath = "../client/dep_old/" + libraryOld + ".jar"
    libraryNewPath = "../client/dep_new/" + libraryNew + ".jar"

    jar_path = '../target/unexpectedException-1.0-SNAPSHOT.jar'

    # Fetch all JAR files in the depofdepOld folder
    depofdepOld_folder = "../client/depofdep_old"
    depofdepNew_folder = "../client/depofdep_new"
    jar_files = glob.glob(os.path.join(depofdepOld_folder, "*.jar"))

    # check if library is already analyzed
    # Invoke the JAR file for the older version of the library, passing JAR filenames as arguments
    subprocess.run(['java', '-Xmx8g', '-cp', jar_path, "org.vinayak.Main","callgraphBasedLibraryAnalysis", libraryOldPath, libraryOld, matchedMethodsDir] + jar_files)

    # Fetch all JAR files in the depofdepNew folder
    jar_files = glob.glob(os.path.join(depofdepNew_folder, "*.jar"))

    # Invoke the JAR file for newer version of the library
    subprocess.run(['java', '-Xmx8g', '-cp', jar_path, "org.vinayak.Main", "callgraphBasedLibraryAnalysis",libraryNewPath, libraryNew, matchedMethodsDir] + jar_files)

def compareOldandNew(libraryOld, libraryNew):
    jsonFilePathOld = '../LibraryResult/' + libraryOld + '.json'
    jsonFilePathNew = '../LibraryResult/' + libraryNew + '.json'

    with open(jsonFilePathOld, 'r') as file:
        dataOld = json.load(file)

    with open(jsonFilePathNew, 'r') as file:
        dataNew = json.load(file)

    new_exceptions = []

    for classes in dataNew:
        for methods in classes.values():
            for method in methods:
                old_method = find_method_signature(dataOld, method['methodSignature'])
                if old_method:
                    difference = list(Counter(method['unchecked_exceptions']) - Counter(old_method['unchecked_exceptions']))
                    new_exceptions.extend([{'methodSignature': method['methodSignature'], 'new_exceptions': difference}])

    new_exceptions = [entry for entry in new_exceptions if entry['new_exceptions']]

    for entry in new_exceptions:
        entry['new_exceptions'] = list(set(entry['new_exceptions']))

    with open(('../CompareResult/' + libraryOld + "#" + libraryNew + ".json"), 'w') as file:
        json.dump(new_exceptions, file, indent=4)


def main():
    parser = argparse.ArgumentParser(description='Process two library strings.')
    parser.add_argument('libraryOld', type=str, help='The old library string')
    parser.add_argument('libraryNew', type=str, help='The new library string')
    parser.add_argument('matchedMethodsDir', type=str, help='Methods to analyze')
    args = parser.parse_args()

    # generates the JSON files for the old and new version of the library
    runAnalysisOnLibrary(args.libraryOld, args.libraryNew, args.matchedMethodsDir)

    # comparing the old and new version of the library
    compareOldandNew(args.libraryOld, args.libraryNew)

if __name__ == "__main__":
    main()

