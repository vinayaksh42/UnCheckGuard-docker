import os
import json

dataset_folder = "dataset"
output_file = "hundred_star_client.txt"

qualified_repos = []

for client_name in os.listdir(dataset_folder):
    client_path = os.path.join(dataset_folder, client_name)
    if os.path.isdir(client_path):
        for repo_name in os.listdir(client_path):
            repo_path = os.path.join(client_path, repo_name)
            json_path = os.path.join(repo_path, "project-info.json")
            if os.path.isfile(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    full_name = data.get("full_name")
                    stargazers_count = data.get("stargazers_count", 0)

                    if full_name and isinstance(stargazers_count, int) and stargazers_count >= 100:
                        qualified_repos.append(full_name)

                except json.JSONDecodeError:
                    print(f"Error decoding JSON in {json_path}")

with open(output_file, "w", encoding="utf-8") as out:
    for repo in qualified_repos:
        out.write(repo + "\n")

print(f"Done! Saved {len(qualified_repos)} repos to {output_file}.")
