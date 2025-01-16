import json

# Load the JSON data from a file
with open('reddit_data_with_pain_points.json') as file:
    data = json.load(file)

# Extract all pain points into a list
pain_points = []

for item in data:
    # Split the pain points by comma and strip any extra spaces
    pain_points.extend([point.strip() for point in item['pain_points'].split(',')])

with open('all_pain_points.txt',"w") as f:
    for item in pain_points:
        f.write(f"{item}\n")
