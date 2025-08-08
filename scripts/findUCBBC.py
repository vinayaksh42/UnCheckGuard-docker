import os
import sys
import subprocess
import shutil
import json

from file_utils import delete_directory, create_directory, delete_directory_contents, copy_directory, copy_file, copy_jars_only
from get_utils import clone_repository, get_commit_sha
from maven_utils import find_pom_file, run_maven_commands, copy_artifacts
from analysis_utils import download_depofdep, saveResults
from paths import path, RESULTS_DIR, MATCH_DIR, LIBRARY_RESULT_DIR, COMPARE_RESULT_DIR, CLIENT_DIR  # ✅ new import

JAVA_VERSION = {
    "1.8": os.environ.get("JAVA8_HOME", "/usr/lib/jvm/java-8-openjdk-amd64"),
    "11": os.environ.get("JAVA11_HOME", "/usr/lib/jvm/java-11-openjdk-amd64"),
}

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 findUCBBC.py <owner/repo> <commit_sha>")
        sys.exit(1)

    owner_repo = sys.argv[1]
    commit_sha = sys.argv[2] if len(sys.argv) > 2 else get_commit_sha(owner_repo)
    repo_url = "https://github.com/" + owner_repo

    # ✅ Define all working paths using path()
    base_client = CLIENT_DIR
    clone_dir = path(base_client, "cloned_repo")
    dep_old_dir = path(base_client, "dep_old")
    dep_new_dir = path(base_client, "dep_new")
    depofdep_old_dir = path(base_client, "depofdep_old")
    depofdep_new_dir = path(base_client, "depofdep_new")
    client_jar_dir = path(base_client, "client_jar")
    client_results_dir = path(base_client, "client_results")
    matched_methods_dir = path(base_client, "matched_methods")
    temp_file = path(base_client, "client_temp")

    jar_path = path("../target", "unexpectedException-1.0-SNAPSHOT.jar")

    # Output directories
    final_result = RESULTS_DIR
    result_dir = COMPARE_RESULT_DIR
    match_dir = MATCH_DIR
    library_dir = LIBRARY_RESULT_DIR

    # ✅ Ensure output directories exist
    for d in [result_dir, library_dir, match_dir, base_client,final_result]:
        create_directory(d)

    setup_dirs = [
        clone_dir, dep_old_dir, dep_new_dir, depofdep_old_dir, depofdep_new_dir,
        client_jar_dir, client_results_dir, temp_file, matched_methods_dir
    ]
    for directory in setup_dirs:
        delete_directory(directory)
        create_directory(directory)

    commit_sha = sys.argv[2] if len(sys.argv) > 2 else get_commit_sha(owner_repo)

    # 1 - Clone Repository
    clone_repository(repo_url, clone_dir, commit_sha)

    # 2 - Check if the repository is a Maven project
    pom_path = find_pom_file(clone_dir)
    if pom_path:
        # check the current java version
        os.environ["JAVA_HOME"] = JAVA_VERSION.get("1.8")
        print("Maven project detected!")
        print(f"Found pom.xml at: {pom_path}")

        pom_dir = os.path.dirname(pom_path)

        commands = [
            ["mvn", "clean", "package", "-DskipTests", "-fn"],
            ["mvn", "dependency:copy-dependencies"]
        ]
        
        # 3 - Run Maven commands to build the project
        run_maven_commands(pom_dir,commands)

        # 4 - Copy the artifacts to the dep_old
        copy_artifacts(pom_dir, client_jar_dir, dep_old_dir)

        commands = [
            ["mvn", "org.codehaus.mojo:versions-maven-plugin:2.18.0:use-latest-versions"],
            ["mvn", "clean", "package", "-DskipTests", "-fn"],
            ["mvn", "dependency:copy-dependencies"]
        ]

        # 5 - Run Maven commands to update the dependencies
        run_maven_commands(pom_dir, commands)

        # 6 - Copy the artifacts to the dep_new
        copy_jars_only(pom_dir, dep_new_dir)

        client_name = ""

        # 7 - Run the analysis on the client jar file
        jar_files = [f for f in os.listdir(client_jar_dir) if f.endswith(".jar") and "original" not in f]
        if len(jar_files) == 1:
            print(f"Found the client jar file: {jar_files[0]}")
            client_name = jar_files[0].split(".jar")[0]
            print(f"Running the analysis on the client jar file: {jar_files[0]}")
            create_directory(client_results_dir)
            subprocess.run(['java', '-Xmx8g', '-cp', jar_path, "org.vinayak.Main","analyzeClient", "../client/client_jar/" + jar_files[0], client_name])
        else:
            print("Error: No client jar file found or multiple client jar files found.")
            sys.exit(1)


        
        jar_files_old = [f for f in os.listdir(dep_old_dir) if f.endswith(".jar")]
        jar_files_new = [f for f in os.listdir(dep_new_dir) if f.endswith(".jar")]

        with open(path(client_results_dir, f"{client_name}.json")) as client_file:
            client_data = json.load(client_file)
        
        external_calls = set()
        for entry in client_data:
            for class_name, methods in entry.items():
                for method_info in methods:
                    external_calls.update(method_info["external_method_calls"])

        # 8 - Compare the dependencies
        for jar_file_old in jar_files_old:
            # Remove .jar and split.
            old_parts = jar_file_old.replace(".jar", "").split("-")
            # Strip out snapshot and remove the last chunk (often the version).
            old_parts = [p for p in old_parts if p.lower() != "snapshot"]
            if len(old_parts) > 1:
                old_parts = old_parts[:-1]
            old_base = "-".join(old_parts)

            match = False
            jar_file_new = ""
            for jar_file_temp_new in jar_files_new:
                new_parts = jar_file_temp_new.replace(".jar", "").split("-")
                new_parts = [p for p in new_parts if p.lower() != "snapshot"]
                if len(new_parts) > 1:
                    new_parts = new_parts[:-1]
                new_base = "-".join(new_parts)

                if old_base == new_base:
                    match = True
                    jar_file_new = jar_file_temp_new
                    break

            if not match:
                print(f"No matching jar file found for {jar_file_old}")
                continue

            if jar_file_new == jar_file_old:
                continue
            print(f"Analyzing library: {jar_file_old}")

            libraryOld = jar_file_old.split(".jar")[0]
            libraryNew = jar_file_new.split(".jar")[0]

            libraryOldPath = "../client/dep_old/" + libraryOld + ".jar"

            subprocess.run(['java', '-Xmx8g', '-cp', jar_path, "org.vinayak.Main","analyzeLibraryMethods", libraryOldPath, libraryOld])

            with open(temp_file + "/" + libraryOld + ".json") as lib_file:
                library_methods = set(json.load(lib_file))
            used_library_methods = external_calls.intersection(library_methods)

            # save the matched methods in a json file under the object matchedMethods
            temp_matched_methods_path = matched_methods_dir + "/" + jar_file_old.split(".jar")[0] + "#" + "MatchedMethods" + ".json"
            with open(matched_methods_dir + "/" + jar_file_old.split(".jar")[0] + "#" + "MatchedMethods" + ".json", "w") as file:
                json.dump(list(used_library_methods), file)

            if not used_library_methods:
                print(f"No methods from library {jar_file_old} are used in the client")
                continue

            # 9B - Download the dependencies of the dependencies
            # download_depofdep(jar_file_new, depofdep_new_dir)
            # download_depofdep(jar_file_old, depofdep_old_dir)
        
            print(f"Running analysis on library: {libraryOld} and {libraryNew}")
            # 10B - Run the analysis on the library
            os.environ["JAVA_HOME"] = JAVA_VERSION.get("11")
            subprocess.run(['python3', 'transitiveException.py', libraryOld, libraryNew, temp_matched_methods_path])
            final_result_name = libraryOld + "#" + libraryNew  +  "#" + client_name + '.json'
            # 11B - Search methods in the client that might have a BBC due to the newly added unchecked exception
            subprocess.run(['python3', 'searchMethodsToTest.py', '../client/client_results/' + client_name + '.json', '../CompareResult/' + libraryOld + "#" + libraryNew + ".json" , '../Match/' + final_result_name])
            # 12B - save the results in a csv file, save the client repo url, library names, library version, matched methods, git commit sha, and the time of the analysis
            saveResults(libraryOld, libraryNew, client_name, owner_repo, commit_sha, final_result, final_result_name,match_dir)

        # for directory in setup_dirs:
        #     delete_directory(directory)

    else:
        print("No Maven project detected in this repository (pom.xml not found).")
        # Cleanup the cloned repository if no pom.xml is found.
        print("Cleaning up cloned repository...")
        shutil.rmtree(clone_dir)

if __name__ == "__main__":
    main()
