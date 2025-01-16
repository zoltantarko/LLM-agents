from openai import OpenAI
import json
import os
from dotenv import load_dotenv
import time

def extract_comment_pain_points(submissions):
    data = []
    total_submissions = len(submissions)  # Total number of submissions to process
    for index, submission in enumerate(submissions, start=1):
        title = submission["title"]
        content = submission["content"]
        comments = submission["comments"]
        
        # Formulate the prompt for ChatGPT to summarize pain points in the comments
        prompt = (
            f"Here is a Reddit post titled '{title}' with the following content:\n"
            f"{content}\n\n"
            "The comments below express various views on the content. Extract 10 main challenges from the comments, and the content"
            "considering the context provided in the title and content of the post:\n"
            "\n" + "\n".join(comments) + "\n\n"
            "Return an itemized summary of the key pain points. The output should ONLY contain the itemized summary withe a comma-separated structure"
        )

        try:
            # Send the prompt to ChatGPT
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in understanding IT career challenges."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000
            )

            # Get and format the pain points from the response
            pain_points = response.choices[0].message.content.strip()
            data.append({
                "title": title,
                "content": content,
                "pain_points": pain_points
            })
        except Exception as e:
            print(f"Error processing submission '{title}': {e}")
            continue

        # Sleep to avoid hitting rate limits
        print(f"Processed submissions: {index}/{total_submissions}.")

    return data

# Load API keys
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open('cleaned_reddit_data_reviewed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract pain points from comments
data_with_pain_points = extract_comment_pain_points(data)

# Save the data to a JSON file
with open("reddit_data_with_pain_points.json", "w") as f:
    json.dump(data_with_pain_points, f, indent=4)

print("Pain point extraction complete!")
