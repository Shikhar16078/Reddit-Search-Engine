import praw
import json
import logging
import os
import time
import random

#region Logging Configuration
logging.basicConfig(
    filename='logs.txt',
    level=logging.NOTSET,
    format='Type: %(levelname)s %(asctime)s \n%(message)s\n',
    datefmt='on %d-%m-%Y at %H:%M:%S'
)
logging.info("---------- Application Started ----------")
#endregion

#region API Connection
# Load Reddit credentials from JSON
with open("credentials.json", "r") as cred_file:
    creds = json.load(cred_file)

logging.info(f"""---------- Credentials Loaded Successfully ----------
username = {creds['username']}
useragent = {creds['user_agent']}
""")
print("Established Connection with the API")
#endregion

# Create Reddit instance
reddit = praw.Reddit(
    client_id=creds['client_id'],
    client_secret=creds['client_secret'],
    user_agent=creds['user_agent']
)

# List of subreddits to scrape
subreddits_list = ['AskReddit', 'Movies', 'Technology', 'WorldNews', 'funny', 'pics', 'Music']

# Path for storing reddit posts
reddit_file_prefix = "reddit_batch"
processed_ids_file = "processed_ids.json"

# Load previously processed IDs (if the file exists)
if os.path.exists(processed_ids_file):
    with open(processed_ids_file, "r") as f:
        processed_ids = set(json.load(f))
else:
    processed_ids = set()

print(f"We have currently {len(processed_ids)} posts.")
print(f"Crawling for random posts from reddit.")

# File size threshold (in bytes, 10 MB)
FILE_SIZE_THRESHOLD = 2 * 1024 * 1024  # 10 MB

# Function to check the size of the file
def get_file_size(file_path):
    if os.path.exists(file_path):
        return os.path.getsize(file_path)
    return 0

# Create a new file with an incremented index
def get_new_file_path(file_prefix, index):
    return f"{file_prefix}_{index}.txt"

# Crawl data in bulk
time_start_crawl = time.time()
max_posts_to_save = 1000 # Specify how many posts you want to collect

# File counter for naming
file_index = 1
reddit_file = get_new_file_path(reddit_file_prefix, file_index)

counter = 0
# Collect posts from subreddits in bulk
for i in range(max_posts_to_save):
    subreddit_name = random.choice(subreddits_list)  # Choose a random subreddit
    subreddit = reddit.subreddit(subreddit_name)

    try:
        for post in subreddit.new(limit=200):  # Fetch 100 posts from the 'new' section
            if post.id not in processed_ids and post.is_self:  # Filter text posts only
                counter += 1 
                post_data = {
                    "id": post.id,
                    "title": post.title,
                    "author": post.author.name if post.author else 'Unknown',
                    "url": post.url,
                    "body": post.selftext,
                    "comments": [],
                    "score": post.score,
                    "upvotes": post.ups,
                    "downvotes": post.downs,
                    "num_comments": post.num_comments,
                }

                # Fetching comments for the post
                post.comments.replace_more(limit=0)
                for comment in post.comments.list():
                    comment_data = {
                        "author": comment.author.name if comment.author else 'Unknown',
                        "body": comment.body,
                        "score": comment.score,
                    }
                    post_data["comments"].append(comment_data)
                
                # Add the post id to the processed set
                processed_ids.add(post.id)
                
                # Check if the file size exceeds the threshold
                if get_file_size(reddit_file) >= FILE_SIZE_THRESHOLD:
                    file_index += 1  # Increment file index
                    reddit_file = get_new_file_path(reddit_file_prefix, file_index)  # Get new file path
                    logging.info("File exceeded 10 MBs. Therefore, created new file.")
                
                # Write the post to the file
                with open(reddit_file, "a") as file:
                    file.write(json.dumps(post_data) + "\n")
                    logging.info(f"WRITTEN: {post_data["title"]}")

                print(f"Written {counter}th post in {reddit_file} file.")
                if len(processed_ids) >= max_posts_to_save:
                    break

    except Exception as e:
        logging.error(f"Error fetching post from {subreddit_name}: {e}")
        print(f"Error fetching post from {subreddit_name}: {e}")

    if len(processed_ids) >= max_posts_to_save:
        break

time_end_crawl = time.time()
time_execution_crawl = time_end_crawl - time_start_crawl
minutes = int(time_execution_crawl // 60)
seconds = int(time_execution_crawl % 60)
print(f"Crawling Completed in {minutes} minutes and {seconds} seconds.")

# Save the processed IDs to a file
with open(processed_ids_file, "w") as f:
    json.dump(list(processed_ids), f)
print(f"Updated processed IDs in '{processed_ids_file}'.")

logging.info(f"Total Posts: {len(processed_ids)}")
logging.info("---------- Application Completed ----------")

print(f"Total Posts: {len(processed_ids)}")
print("Successfully ran the application.")