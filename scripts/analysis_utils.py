import os
import subprocess
import json
import csv
import datetime
import shutil
from file_utils import create_directory

def download_depofdep(jar_file, depofdep_dir):
    if os.path.exists(depofdep_dir):
        shutil.rmtree(depofdep_dir)
    create_directory(depofdep_dir)
    subprocess.run(['python3', 'getDepJars.py', jar_file, depofdep_dir])

def saveResults(libraryOld, libraryNew, client_name, owner_repo, commit_sha, final_result, final_result_name, match_dir):
    print(f"Saving the results in {final_result}/results.csv")

    # check if the file exists
    if not os.path.exists(final_result + "/results.csv"):
        with open(final_result + "/results.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ClientName","OwnerRepo","CommitSha","LibraryOld", "LibraryNew", "Match Results", "Time", "GitHubRepo", "NumberOfMatchedMethods", "Number of Times the Library is Used in the Client"])
    
    # open the Match results in ../Match folder for the client
    with open(match_dir + "/" + final_result_name) as match_file:
        match_data = json.load(match_file)

    # open the client_result file to get the number of times the library is used in the client
    with open("../client/client_results/" + client_name + ".json") as client_file:
        client_data = json.load(client_file)
    
    # Open the matched methods file to get the number of matched methods
    with open("../client/matched_methods/" + libraryOld + "#" + "MatchedMethods" + ".json") as matched_methods_file:
        matched_methods = json.load(matched_methods_file)
    
    number_of_times_library_used = 0
    for class_data in client_data:
        for methods in class_data.values():
            for method in methods:
                for external_call in method['external_method_calls']:
                    if external_call in matched_methods:
                        number_of_times_library_used += 1
    
    with open(final_result + "/results.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([client_name, owner_repo, commit_sha, libraryOld, libraryNew, "github.com/vinayaksh42/UncheckedException/tree/main/Match/" + final_result_name, datetime.datetime.now(), "github.com/" + owner_repo, len(match_data), number_of_times_library_used])
    
    # Create combined results CSV
    results_csv_path = final_result + "/results.csv"
    combined_results_csv_path = final_result + "/combined_results.csv"

    # Read the results.csv file into a dictionary
    results_dict = {}
    with open(results_csv_path, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            results_dict[row['Match Results']] = row

    # Create combined results CSV
    results_csv_path = final_result + "/results.csv"
    combined_results_csv_path = final_result + "/combined_results.csv"

    # Read the results.csv file into a dictionary
    results_dict = {}
    with open(results_csv_path, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            results_dict[row['Match Results']] = row

    # Create the output CSV file
    with open(combined_results_csv_path, mode='w', newline='') as csvfile:
        fieldnames = ['ClientName', 'OwnerRepo', 'GitHubOwnerRepo', 'LibraryOld', 'LibraryNew', 'CommitSha', 'ClientMethod', 'ExternalCall']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Iterate over each JSON file in the Match folder
        for filename in os.listdir(match_dir):
            if filename.endswith('.json'):
                json_path = os.path.join(match_dir, filename)
                with open(json_path, 'r') as jsonfile:
                    match_data = json.load(jsonfile)
                    match_results_url = f"github.com/vinayaksh42/UncheckedException/tree/main/Match/{filename}"
                    
                    if match_results_url in results_dict:
                        result_row = results_dict[match_results_url]
                        for entry in match_data:
                            writer.writerow({
                                'ClientName': result_row['ClientName'],
                                'OwnerRepo': result_row['OwnerRepo'],
                                'GitHubOwnerRepo': result_row['GitHubRepo'],
                                'LibraryOld': result_row['LibraryOld'],
                                'LibraryNew': result_row['LibraryNew'],
                                'CommitSha': result_row['CommitSha'],
                                'ClientMethod': entry['client_method'],
                                'ExternalCall': entry['external_call']
                            })