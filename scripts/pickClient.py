
input_file = "ten_star_client.txt"
output_file = "clientDataset.txt"

with open(input_file, "r") as f:
    elements = f.read().split()

selected_elements = [elements[i] for i in range(18, len(elements), 19)]

with open(output_file, "w") as f:
    for item in selected_elements:
        f.write(item + "\n")

print(f"Saved {len(selected_elements)} elements to {output_file}")
