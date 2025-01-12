import praw
from openai import OpenAI
import json
import os
import requests
from dotenv import load_dotenv
from praw.exceptions import PRAWException
import time

# Load API keys
load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        {"role": "system", "content": "You are an expert in IT career transitions. Identify which of the following subreddits are most relevant for discussing IT career changes and challenges. Your output should ONLY contain the filtered subreddit list."},
        {"role": "user", "content": f"Subreddits: {', '.join(subreddits)}"}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=500
    )
    filtered_subreddits = response.choices[0].message.content.split(", ")
    return filtered_subreddits

# Scrape posts from filtered subreddits
def scrape_reddit(subreddits, keywords, limit=20):
    data = []
    for subreddit in subreddits:
        print("Attempting to scrape subreddit: ", subreddit)
        # Try-except block to skip problematic subreddits
        try:
            for keyword in keywords:
                print("Searching for keyword: ", keyword)
                for submission in reddit.subreddit(subreddit).search(keyword, limit=limit):
                    print("Processing submission: ", submission.title)
                    if keyword not in (submission.title or submission.selftext):
                        continue
                    comments = [comment.body for comment in submission.comments if hasattr(comment, "body")]
                    data.append({
                        "title": submission.title,
                        "content": submission.selftext,
                        "comments": comments
                    })
        except PRAWException as e:
            # Catch any PRAW specific errors (e.g., 403 errors)
            print(f"Skipping subreddit {subreddit} due to error: {e}")
        except requests.exceptions.RequestException as e:
            # Catch HTTP request errors (e.g., 403 errors)
            print(f"Skipping subreddit {subreddit} due to HTTP error: {e}")
        except Exception as e:
            # Catch any other unexpected errors
            print(f"Skipping subreddit {subreddit} due to unexpected error: {e}")

        # Sleep to avoid hitting Reddit's rate limit
        time.sleep(1)
    return data

# Run the workflow
search_term = "IT careers"
subreddits = get_relevant_subreddits(search_term)
print(f"Subreddits found: {subreddits}")

filtered_subreddits = filter_subreddits_with_chatgpt(subreddits)
#filtered_subreddits = ['ITCareers','cscareerquestions','ITCareerSecrets','SecurityCareerAdvice']
print(f"Filtered Subreddits by ChatGPT: {filtered_subreddits}")

data = scrape_reddit(filtered_subreddits, ["career change", "job transition"])
with open("filtered_reddit_data.json", "w") as f:
    json.dump(data, f, indent=4)

print("Scraping and filtering complete!")
