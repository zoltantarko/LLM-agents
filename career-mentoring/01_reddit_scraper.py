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

def filter_reddit_data_with_chatgpt(data):
    filtered_data = []
    decision_check = []
    for entry in data:
        messages = [
            {"role": "system", "content": "You are an expert in career transitions between IT subfields. Identify if the post provided to you are about career changes between IT subfields based on its title and content. Respond with ONLY 'yes' or 'no'."},
            {"role": "user", "content": f"Title: {entry['title']}\nContent: {entry['content']}"}
        ]
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=100
            )
            decision = response.choices[0].message.content.strip().lower()
            if "yes" in decision:
                filtered_data.append(entry)
            verdict = f"Relevant: {decision}, Submission: {entry['title']}"
            decision_check.append(verdict)
        except Exception as e:
            print(f"Error filtering entry with ChatGPT: {e}")
            continue
    with open("verdict_check_data.txt", "w") as f:
        for item in decision_check:
            f.write(f"{item}\n")
    return filtered_data

# Fetch subreddits from the Reddit API
def get_relevant_subreddits(keyword):
    url = f"https://www.reddit.com/subreddits/search.json"
    headers = {"User-Agent": "career-transition-scraper"}
    subreddits = []
    after = None

    while True:
        params = {"q": keyword, "after": after}
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        # Collect the current page of subreddits
        subreddits.extend([item['data']['display_name'] for item in data['data']['children']])
        
        # Check if there's another page
        after = data['data'].get('after')
        if not after:
            break  # No more results, exit the loop

    return subreddits

# Use ChatGPT to filter the subreddits
def filter_subreddits_with_chatgpt(subreddits):
    messages = [
        {"role": "system", "content": "You are an expert in career transitions between IT subfields. Identify which of the following subreddits are the relevant for discussing career changes between IT subfields and challenges. Your output should ONLY contain the filtered subreddit list without any additional string."},
        {"role": "user", "content": f"Subreddits: {', '.join(subreddits)}"}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=500
    )
    filtered_subreddits = response.choices[0].message.content.split(", ")
    return filtered_subreddits

def filter_submissions_with_chatgpt(subreddits):
    messages = [
        {"role": "system", "content": "You are an expert in career transitions between IT subfields. Identify which of the following subreddits are the relevant for discussing career changes between IT subfields and challenges. Your output should ONLY contain the filtered subreddit list without any additional string."},
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
    print("Collected submissions: ",len(data))
    return data

# Run the workflow
#search_term = "\"IT career\""
#subreddits = get_relevant_subreddits(search_term)
#print(f"Subreddits found: {subreddits}")

#filtered_subreddits = filter_subreddits_with_chatgpt(subreddits)
filtered_subreddits = ['ITCareerQuestions', 'ITCareerAnalytics', 'sysadmin', 'CompTIA', 'ITCareers', 'itcareerswitch', 'InformationTechnology', 'careerguidance', 'itcareeradvice', 'ITCareer_Discussion', 'findapath', 'it', 'ITCareerSecrets', 'ITcareerNinja', 'cscareerquestions', 'ITCareerGuide', 'ExperiencedDevs', 'helpdeskcareer', 'ExperienceDevsRead', 'careeradvice', 'ITdept', 'ITManagers', 'ccna']
print(f"Filtered Subreddits by ChatGPT: {filtered_subreddits}")

data = scrape_reddit(filtered_subreddits, ["career change", "job transition"])

with open("scraped_reddit_data.json", "w") as f:
    json.dump(data, f, indent=4)

filtered_data = filter_reddit_data_with_chatgpt(data)

print("Submissions after the filtering: ",{len(filtered_data)})

with open("filtered_reddit_data.json", "w") as f:
    json.dump(filtered_data, f, indent=4)

print("Scraping and filtering complete!")
