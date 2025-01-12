import praw
import openai
import json
import os
import requests
from dotenv import load_dotenv

# Load API keys
load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Fetch subreddits from the Reddit API
def get_relevant_subreddits(keyword):
    url = f"https://www.reddit.com/subreddits/search.json?q={keyword}"
    headers = {"User-Agent": "career-transition-scraper"}
    response = requests.get(url, headers=headers)
    subreddits = [item['data']['display_name'] for item in response.json()['data']['children']]
    return subreddits

# Use ChatGPT to filter the subreddits
def filter_subreddits_with_chatgpt(subreddits):
    messages = [
        {"role": "system", "content": "You are an expert in IT career transitions. Identify which of the following subreddits are most relevant for discussing IT career changes and challenges."},
        {"role": "user", "content": f"Subreddits: {', '.join(subreddits)}"}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=500
    )
    filtered_subreddits = response['choices'][0]['message']['content'].split(", ")
    return filtered_subreddits

# Scrape posts from filtered subreddits
def scrape_reddit(subreddits, keywords, limit=20):
    data = []
    for subreddit in subreddits:
        for keyword in keywords:
            for submission in reddit.subreddit(subreddit).search(keyword, limit=limit):
                comments = [comment.body for comment in submission.comments if hasattr(comment, "body")]
                data.append({
                    "title": submission.title,
                    "content": submission.selftext,
                    "comments": comments
                })
    return data

# Run the workflow
search_term = "IT careers"
subreddits = get_relevant_subreddits(search_term)
print(f"Subreddits found: {subreddits}")

filtered_subreddits = filter_subreddits_with_chatgpt(subreddits)
print(f"Filtered Subreddits by ChatGPT: {filtered_subreddits}")

data = scrape_reddit(filtered_subreddits, ["career change", "burnout", "job transition"])
with open("filtered_reddit_data.json", "w") as f:
    json.dump(data, f, indent=4)

print("Scraping and filtering complete!")
