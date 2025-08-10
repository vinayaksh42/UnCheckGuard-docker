import os
import subprocess
import sys
import requests
import shutil

def clone_repository(repo_url, clone_dir, commit_sha):
    """
    Clones the repository from repo_url into clone_dir.
    Removes the directory first if it already exists.
    """
    if os.path.exists(clone_dir):
        print(f"\033[33mRemoving existing directory: {clone_dir}\033[0m")
        shutil.rmtree(clone_dir)
    try:
        print(f"\033[32mCloning repository from {repo_url} into {clone_dir}...\033[0m")
        subprocess.run(["git", "clone", repo_url, clone_dir],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True
                    )
    except subprocess.CalledProcessError:
        print("\033[31mAn error occurred while cloning the repository.\033[0m")
        sys.exit(1)

    if commit_sha:
        try:
            print(f"\033[32mChecking out commit: {commit_sha}\033[0m")
            subprocess.run(["git", "checkout", commit_sha], cwd=clone_dir,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True
                    )
        except subprocess.CalledProcessError:
            print("\033[31mAn error occurred while cloning the repository.\033[0m")
            sys.exit(1)

def get_commit_sha(owner_repo):
    response = requests.get(f"https://api.github.com/repos/{owner_repo}/commits")
    if response.status_code == 200:
        data = response.json()
        commit_sha = data[0]['sha']
        return commit_sha
    else:
        print(f"Failed to fetch commit sha for repository: {owner_repo}")
        return None