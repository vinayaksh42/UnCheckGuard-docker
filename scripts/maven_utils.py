import os
import subprocess
import sys
import shutil
from file_utils import delete_directory, create_directory, copy_directory, copy_file

def find_pom_file(directory):
    """
    Recursively searches for a pom.xml file within directory.
    Returns the full path to the file if found; otherwise, returns None.
    """
    for root, _, files in os.walk(directory):
        if "pom.xml" in files:
            return os.path.join(root, "pom.xml")
    return None

def run_maven_commands(pom_dir, commands):
    """
    Runs the specified Maven commands in the directory that contains the pom.xml.
    """
    for command in commands:
        print(f"Running Maven command: {' '.join(command)} in directory: {pom_dir}")
        try:
            subprocess.run(command, cwd=pom_dir, check=True)
        except subprocess.CalledProcessError:
            print(f"An error occurred while running Maven command: {' '.join(command)}")
            sys.exit(1)

def copy_artifacts(pom_dir, client_jar_dir, dep_to_copy):
    # Copy dependencies from 'target/dependency' to dep_old_dir
    dependency_src = os.path.join(pom_dir, "target", "dependency")
    create_directory(dep_to_copy)
    copy_directory(dependency_src, dep_to_copy)

    # Copy any .jar files from 'target' to client_jar_dir
    target_dir = os.path.join(pom_dir, "target")
    create_directory(client_jar_dir)
    jar_files = [f for f in os.listdir(target_dir) if f.endswith(".jar")]
    for jar_file in jar_files:
        src_path = os.path.join(target_dir, jar_file)
        dst_path = os.path.join(client_jar_dir, jar_file)
        copy_file(src_path, dst_path)