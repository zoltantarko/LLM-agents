import json
import re


# Function to clean the comments
def clean_deprecated_comments(data):
    for post in data:
        post["comments"] = [comment for comment in post["comments"] if comment not in ["[deleted]", "[removed]"]]
    return data

def clean_special_unicode(data):
    # Regular expression pattern for emoticons and other special characters
    pattern = r'[^\x00-\x7F]+'

    # Function to clean text fields by removing special characters
    def clean_text(text):
        # Replace all non-ASCII characters (emoticons, etc.) with an empty string
        return re.sub(pattern, '', text)

    # Clean the content and comments for each post
    for post in data:
        if "title" in post:
            post["title"] = clean_text(post["title"])
        if "content" in post:
            post["content"] = clean_text(post["content"])
        if "comments" in post:
            post["comments"] = [clean_text(comment) for comment in post["comments"]]

    return data

with open('filtered_reddit_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Clean the data
cleaned_data = clean_deprecated_comments(clean_special_unicode(data))

# Output cleaned data to a new file
with open('cleaned_reddit_data.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
