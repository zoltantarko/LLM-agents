import re
from openai import OpenAI
from collections import defaultdict
from dotenv import load_dotenv
import os

# Set up OpenAI API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load and clean the pain points
with open('pain_points.txt', 'r') as file:
    pain_points = [re.sub(r'^[-\d.\s]+', '', line).strip() for line in file if line.strip()]

# Function to get semantic similarity between two texts using GPT-4
def get_similarity_score(text1, text2):
    prompt = f"Please evaluate the semantic similarity between the following two statements and score them from 0 (not similar) to 10 (extremely similar):\n\n1. {text1}\n2. {text2}\n\nSimilarity Score:"

    response = openai.Completion.create(
        engine="gpt-4",  # or "gpt-3.5-turbo" if you are using GPT-3.5
        prompt=prompt,
        max_tokens=50,
        temperature=0,
    )

    score = response.choices[0].text.strip()
    try:
        return float(score)
    except ValueError:
        return 0.0  # Default to 0.0 if the response is not parseable

# Function to group pain points
def group_pain_points(pain_points, threshold=7.0):
    grouped = defaultdict(list)
    used = [False] * len(pain_points)

    for i, point1 in enumerate(pain_points):
        if used[i]:
            continue
        group = [point1]
        for j, point2 in enumerate(pain_points[i+1:], start=i+1):
            if used[j]:
                continue
            similarity = get_similarity_score(point1, point2)
            if similarity >= threshold:
                group.append(point2)
                used[j] = True
        grouped[len(group)] = group  # Store by the size of the group

    return grouped

# Group the pain points
grouped_pain_points = group_pain_points(pain_points, threshold=7.0)

# Save the results to a file
with open('grouped_pain_points_gpt.txt', 'w') as file:
    for group_size, group in grouped_pain_points.items():
        file.write(f"Group (Size: {group_size}):\n")
        for item in group:
            file.write(f"  - {item}\n")
        file.write("\n")

# Print out representative pain points from each group
print("\nUnique Pain Points (One per group):\n")
for group in grouped_pain_points.values():
    print(group[0])
