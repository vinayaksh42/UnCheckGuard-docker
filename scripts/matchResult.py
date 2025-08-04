import csv
import json
import os

# Define file paths
results_csv_path = '/Users/vinayaksh42/Desktop/Research/BBC Research/unexpectedException/results/results.csv'
match_folder_path = '/Users/vinayaksh42/Desktop/Research/BBC Research/unexpectedException/Match'
output_csv_path = '/Users/vinayaksh42/Desktop/Research/BBC Research/unexpectedException/results/combined_results.csv'

# Read the results.csv file into a dictionary
results_dict = {}
with open(results_csv_path, mode='r', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        results_dict[row['Match Results']] = row

# Create the output CSV file
with open(output_csv_path, mode='w', newline='') as csvfile:
    fieldnames = ['ClientName', 'OwnerRepo', 'GitHubOwnerRepo', 'LibraryOld', 'LibraryNew', 'CommitSha', 'ClientMethod', 'ExternalCall']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Iterate over each JSON file in the Match folder
    for filename in os.listdir(match_folder_path):
        if filename.endswith('.json'):
            json_path = os.path.join(match_folder_path, filename)
            with open(json_path, 'r') as jsonfile:
                match_data = json.load(jsonfile)
                match_results_url = f"https://github.com/vinayaksh42/UncheckedException/tree/main/Match/{filename}"
                
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