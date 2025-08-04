#!/usr/bin/env python3

import os
import sys
import textwrap
import subprocess
import re
import requests
import shutil


def create_maven_project_and_download_jars(
    dep_group_id, 
    dep_artifact_id, 
    dep_version,
    project_dir="my-maven-project",
    proj_group_id="com.example",
    proj_artifact_id="my-app",
    proj_version="1.0-SNAPSHOT"
):
    """
    1) Creates a simple Maven project folder structure with a minimal pom.xml.
    2) Adds the provided dependency (GAV) to the pom.xml.
    3) Invokes Maven to download all the required JAR files (direct + transitive).
    4) Places the downloaded dependencies into project_dir/libs/.
    """

    # Step A: Create the project directory (if it doesn't already exist)
    os.makedirs(project_dir, exist_ok=True)

    # Step B: Generate a minimal POM that includes the desired dependency
    pom_content = textwrap.dedent(f"""\
    <project xmlns="http://maven.apache.org/POM/4.0.0"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
                                 http://maven.apache.org/xsd/maven-4.0.0.xsd">
      <modelVersion>4.0.0</modelVersion>

      <!-- Basic project coordinates (adjust as needed) -->
      <groupId>{proj_group_id}</groupId>
      <artifactId>{proj_artifact_id}</artifactId>
      <version>{proj_version}</version>

      <dependencies>
        <dependency>
          <groupId>{dep_group_id}</groupId>
          <artifactId>{dep_artifact_id}</artifactId>
          <version>{dep_version}</version>
        </dependency>
      </dependencies>

    </project>
    """)

    pom_path = os.path.join(project_dir, "pom.xml")
    with open(pom_path, "w", encoding="utf-8") as pom_file:
        pom_file.write(pom_content)

    # Step C: Create standard Maven src directory structure
    for subdir in [
        "src/main/java",
        "src/main/resources",
        "src/test/java",
        "src/test/resources"
    ]:
        os.makedirs(os.path.join(project_dir, subdir), exist_ok=True)

    print(f"Created Maven project in '{project_dir}'")
    print(f"Added dependency {dep_group_id}:{dep_artifact_id}:{dep_version} to pom.xml")

    # Step D: Run Maven to download dependencies into a 'libs' folder
    # We'll use `mvn dependency:copy-dependencies` with -DoutputDirectory=libs
    try:
        print("\n=== Running Maven to download all dependencies ===")
        subprocess.run(
            ["mvn", "clean", "dependency:copy-dependencies", "-DoutputDirectory=libs"],
            cwd=project_dir,
            check=True
        )
        print("Maven successfully downloaded all dependencies to 'libs/' folder.")
    except subprocess.CalledProcessError as e:
        print("Error running Maven:", e)
        sys.exit(e.returncode)


def parse_jar_filename(jar_filename):
    """
    Extract artifactID and version from a jar file name.
    Expects a format like: artifactID-version.jar
    For example, 'asm-5.1.jar' returns ('asm', '5.1')
    
    This regex assumes the version starts with a digit and may include dots and hyphens (like SNAPSHOT).
    """
    basename = os.path.basename(jar_filename)
    # Regex breakdown:
    #   ^                   : start of string
    #   (?P<artifact>.+)    : artifactID (one or more characters)
    #   -                   : literal dash separator
    #   (?P<version>\d[\d\.\-A-Za-z]+) : version starting with a digit and then digits, dots, hyphens, or letters
    #   \.jar$              : ends with .jar
    pattern = r'^(?P<artifact>.+)-(?P<version>\d[\d\.\-A-Za-z]+)\.jar$'
    match = re.match(pattern, basename)
    if not match:
        raise ValueError("Jar file name does not match the expected pattern: artifactID-version.jar")
    artifact = match.group("artifact")
    version = match.group("version")
    return artifact, version

def query_maven_group(artifact, version):
    """
    Query Maven Central's API for the given artifact (artifactID) and version.
    Returns the groupID if found, or None if not found.
    """
    # Maven Central Search API endpoint
    url = "https://search.maven.org/solrsearch/select"
    # Construct the query. The Maven API uses:
    #   a:"artifact" AND v:"version"
    params = {
        "q": f'a:"{artifact}" AND v:"{version}"',
        "rows": "20",
        "wt": "json"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"Error querying Maven Central: HTTP {response.status_code}")
    
    data = response.json()
    docs = data.get("response", {}).get("docs", [])
    if not docs:
        return None
    
    # The Maven API returns the groupId in the "g" field.
    group_id = docs[0].get("g")
    return group_id

def main():
    """
    Usage:
      getDepJars.py <JarName> <folderName>

    Example:
      ./getDepJars.py kryo-3.0.3.jar depofdepOld
    """
    if len(sys.argv) != 3:
        print("Usage: getDepJars.py <JarName> <folderName>")
        sys.exit(1)

    jar_file = sys.argv[1]
    folder_name = sys.argv[2]
    
    try:
        dep_artifact_id, dep_version = parse_jar_filename(jar_file)
    except ValueError as ve:
        print("Error:", ve)
        sys.exit(1)

    try:
        dep_group_id = query_maven_group(dep_artifact_id, dep_version)
    except Exception as e:
        print("Error querying Maven Central:", e)
        sys.exit(1)

    # Customize the project directory and base coordinates if you like
    project_dir = "my-maven-project"
    proj_group_id = "com.example"
    proj_artifact_id = "my-app"
    proj_version = "1.0-SNAPSHOT"

    create_maven_project_and_download_jars(
        dep_group_id,
        dep_artifact_id,
        dep_version,
        project_dir=project_dir,
        proj_group_id=proj_group_id,
        proj_artifact_id=proj_artifact_id,
        proj_version=proj_version
    )
    excluded_jar = f"{dep_artifact_id}-{dep_version}.jar"
    jars_to_return = []
    resource_folder = os.path.join(os.path.dirname(project_dir), folder_name)
    os.makedirs(resource_folder, exist_ok=True)
    libs_path = os.path.join(project_dir, "libs")
    if os.path.isdir(libs_path):
        for jar_file in os.listdir(libs_path):
            if jar_file.endswith(".jar"):
                if jar_file != excluded_jar:
                    jars_to_return.append(jar_file)
                shutil.copy2(os.path.join(libs_path, jar_file), resource_folder)
    shutil.rmtree(project_dir)
    print("\n".join(jars_to_return))
    excluded_jar_path = os.path.join(folder_name, excluded_jar)
    if os.path.isfile(excluded_jar_path):
        os.remove(excluded_jar_path)


if __name__ == "__main__":
    main()
