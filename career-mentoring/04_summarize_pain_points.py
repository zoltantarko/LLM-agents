# The scope is of this script is to process the career-mentoring\reddit_data_with_pain_points.json file in order to cluster the posts based on the title AND description.
# It should name the cluster and should create a description to that cluster. The cluster should contain all the paint points which was listed in each post which belongs
# to the given cluster. After this has been done, it should check through the pain points of the given cluster and create a list of 10 pain points for the cluster instead
# the previously listed ones. It should use openai api at points where it is really necessary.
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from openai import OpenAI
from dotenv import load_dotenv
import os
import csv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load data
with open('reddit_data_with_pain_points.json') as file:
    data = json.load(file)

# Prepare data for clustering
titles_and_contents = [f"{post['title']} {post['content']}" for post in data]

# Vectorize the text
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(titles_and_contents)

# Perform KMeans clustering
num_clusters = 10  # Adjust as necessary
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
kmeans.fit(tfidf_matrix)

# Assign clusters to posts
clusters = kmeans.labels_
for i, post in enumerate(data):
    post['cluster'] = int(clusters[i])

# Group posts by cluster
cluster_groups = {}
for post in data:
    cluster_id = post['cluster']
    if cluster_id not in cluster_groups:
        cluster_groups[cluster_id] = []
    cluster_groups[cluster_id].append(post)

def generate_cluster_summary(cluster_posts):
    combined_text = " ".join([post['content'] for post in cluster_posts])
    messages = [
        {"role": "system", "content": "You are an expert IT career advisor, specialised on empathizing and summarizing clustered user stories."},
        {"role": "user", "content": f"Create a summary and name for the following text:\n{combined_text}"}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=200
    )
    return response.choices[0].message.content.split(", ")

def generate_top_pain_points(cluster_posts):
    combined_pain_points = " ".join([post['pain_points'] for post in cluster_posts])
    messages = [
        {"role": "system", "content": "You are an expert IT career advisor, specialised on empathizing and identify pain points of user stories."},
        {"role": "user", "content": f"Create a list of the top 10 pain points from the following text:\n{combined_pain_points}"}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=200
    )
    return response.choices[0].message.content.split(", ")

# Process each cluster and write to CSV
with open('clustered_reddit_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['cluster_id', 'summary', 'top_pain_points']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for cluster_id, posts in cluster_groups.items():
        cluster_summary = generate_cluster_summary(posts)
        top_pain_points = generate_top_pain_points(posts)
        writer.writerow({'cluster_id': cluster_id, 'summary': cluster_summary, 'top_pain_points': top_pain_points})

print("CSV file has been successfully created!")
