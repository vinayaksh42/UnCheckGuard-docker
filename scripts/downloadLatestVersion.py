import requests
import argparse
import os
import shutil
import sys
import re

def get_latest_version(group_id, artifact_id):
    """Fetches the latest version of a Maven library from Maven Central."""
    url = f"https://search.maven.org/solrsearch/select?q=g:{group_id}+AND+a:{artifact_id}&core=gav&rows=1&wt=json"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data["response"]["docs"]:
            latest_version = data["response"]["docs"][0]["v"]
            return latest_version
        else:
            print("Library not found on Maven Central.")
            return None
    else:
        print("Failed to connect to Maven Central.")
        return None

def download_jar(group_id, artifact_id, version):
    """Downloads the JAR file of the specified Maven library version."""
    jar_url = f"https://repo1.maven.org/maven2/{group_id.replace('.', '/')}/{artifact_id}/{version}/{artifact_id}-{version}.jar"
    
    response = requests.get(jar_url, stream=True)
    if response.status_code == 200:
        jar_filename = f"{artifact_id}-{version}.jar"
        with open(jar_filename, "wb") as jar_file:
            for chunk in response.iter_content(chunk_size=8192):
                jar_file.write(chunk)
        print(f"{jar_filename}")
    else:
        print("Error downloading JAR file.")

    jar_name = f"{artifact_id}-{version}.jar"

    resources_dir = os.path.join(os.path.dirname(__file__), "../resources")
    os.makedirs(resources_dir, exist_ok=True)
    shutil.copy2(jar_name, resources_dir)

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
    if len(sys.argv) != 2:
        print("Usage: downloadLatestVersion.py <JarName>")
        sys.exit(1)

    jar_file = sys.argv[1]

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

    version = get_latest_version(dep_group_id, dep_artifact_id)

    download_jar(dep_group_id, dep_artifact_id, dep_version)

if __name__ == "__main__":
    main()
