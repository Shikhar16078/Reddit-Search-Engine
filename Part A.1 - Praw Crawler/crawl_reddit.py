import praw
import json
import logging
import os
import time
import requests
import sys

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

# List of subreddits to scrape (Sequential Order)
if(len(sys.argv) > 1):
    subreddits_list = sys.argv[1].split()
    print("I will crawl from your given list of topics.")
else:
    subreddits_list = [
        'technology', 'Android', 'iOS', 'gadgets', 'programming', 
        'learnprogramming', 'webdev', 'Python', 'cybersecurity', 'techsupport', 
        'DevOps', 'DataScience', 'MachineLearning', 'ArtificialIntelligence', 'Linux'
    ]
    print("No topic provided, scrawling defaults.")

# 'Computers', 'TechNews', 'BigData', 'Blockchain', 'cryptocurrency'
# 'Apple', 'Windows10', 'VirtualReality', '3Dprinting', 'IoT', 
#     'SelfDrivingCars', 'QuantumComputing', 'cloudcomputing', 'networking', 'gamedev'

# Path for storing Reddit posts
reddit_file_prefix = "reddit_batch"
processed_ids_file = "processed_ids.json"

# Load previously processed IDs (if the file exists)
if os.path.exists(processed_ids_file):
    with open(processed_ids_file, "r") as f:
        processed_ids = set(json.load(f))
else:
    processed_ids = set()

print(f"We have currently {len(processed_ids)} posts.")
print(f"Crawling posts from subreddits in order...")

# Directory for saving images
image_directory = "Assets/Images"
os.makedirs(image_directory, exist_ok=True)

# File size threshold (in bytes, 10 MB)
FILE_SIZE_THRESHOLD = 9.5 * 1024 * 1024  # 10 MB Approx.

# Function to check the size of the file
def get_file_size(file_path):
    return os.path.getsize(file_path) if os.path.exists(file_path) else 0

# Create a new file with an incremented index
def get_new_file_path(file_prefix, index):
    return f"{file_prefix}_{index}.txt"

# Function to download images
def download_image(image_url, post_id):
    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            image_extension = os.path.splitext(image_url)[-1]  # Get file extension
            if image_extension.lower() not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                image_extension = ".jpg"  # Default to .jpg if extension is unknown
            
            image_path = os.path.join(image_directory, f"{post_id}{image_extension}")
            with open(image_path, "wb") as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)
            logging.info(f"Downloaded Image: {image_url} -> {image_path}")
            return image_path
    except Exception as e:
        logging.warning(f"Failed to download image {image_url}: {e}")
    return None

# Crawl data in bulk
time_start_crawl = time.time()
max_posts_to_save = 15000  # Specify how many posts you want to collect

# File counter for naming
file_index = 1
reddit_file = get_new_file_path(reddit_file_prefix, file_index)

counter = 0
posts_checked = 0

# Collect posts from subreddits **in a structured order**
for subreddit_name in subreddits_list:
    subreddit = reddit.subreddit(subreddit_name)

    try:
        for post in subreddit.top(limit=990):
            try:
                if post.id not in processed_ids and (post.is_self or post.url.endswith(('.jpg', '.png', '.gif', '.jpeg', '.webp'))):
                    counter += 1
                    image_path = None  # Default to None

                    # Download image if it's in post body or a direct image link
                    if post.url.endswith(('.jpg', '.png', '.gif', '.jpeg', '.webp')):
                        logging.info("Found a post with Image!")
                        image_path = download_image(post.url, post.id)

                    post_data = {
                        "subreddit": post.subreddit.display_name,
                        "id": post.id,
                        "title": post.title,
                        "author": post.author.name if post.author else 'Unknown',
                        "body": post.selftext,
                        "comments": [],
                        "flair_text": post.link_flair_text,
                        "permalink": post.permalink,
                        "url": post.url,
                        "image_path": image_path,  # Store image path if available
                        "created_utc": post.created_utc,
                        "score": post.score,
                        "upvote_ratio": post.upvote_ratio,
                        "num_comments": post.num_comments,
                        "is_self": post.is_self,
                        "over_18": post.over_18,
                        "spoiler": post.spoiler,
                        "locked": post.locked,
                        "stickied": post.stickied,
                    }

                    # Fetching comments for the post
                    try:
                        post.comments.replace_more(limit=0)
                        for comment in post.comments.list():
                            comment_data = {
                                "id": comment.id,
                                "author": comment.author.name if comment.author else 'Unknown',
                                "body": comment.body,
                                "subreddit": comment.subreddit.display_name,
                                "parent_id": comment.parent_id,
                                "permalink": comment.permalink,
                                "author_flair_text": comment.author_flair_text,
                                "created_utc": comment.created_utc,
                                "score": comment.score,
                                "is_submitter": comment.is_submitter,
                                "stickied": comment.stickied,
                                "edited": comment.edited,
                                "distinguished": comment.distinguished,
                            }
                            post_data["comments"].append(comment_data)
                    except Exception as e:
                        logging.warning(f"Error fetching comments for post {post.id}: {e}")

                    # Add the post ID to the processed set
                    processed_ids.add(post.id)

                    # Write the post to the file
                    with open(reddit_file, "a") as file:
                        file.write(json.dumps(post_data) + ",\n")
                        logging.info(f"WRITTEN: {post_data['title']}")

                    print(f"Written {counter}th post in {reddit_file} file.")

                    # **Check file size AFTER writing**
                    if get_file_size(reddit_file) >= FILE_SIZE_THRESHOLD:
                        file_index += 1  # Increment file index
                        reddit_file = get_new_file_path(reddit_file_prefix, file_index)  # Get new file path
                        logging.info(f"File exceeded {FILE_SIZE_THRESHOLD / (1024*1024)} MB. Created new file: {reddit_file}")
                
                posts_checked+=1
            except Exception as e:
                logging.warning(f"Skipping post due to error: {e}")
                continue  # Ignore error and move to the next post

    except Exception as e:
        logging.error(f"Error fetching posts from subreddit {subreddit_name}: {e}")
        print(f"Skipping subreddit {subreddit_name} due to error: {e}")

time_end_crawl = time.time()
time_execution_crawl = time_end_crawl - time_start_crawl
minutes = int(time_execution_crawl // 60)
seconds = int(time_execution_crawl % 60)
print(f"Crawling Completed in {minutes} minutes and {seconds} seconds.")
print(f"Checked: {posts_checked}.")

# Save the processed IDs to a file
with open(processed_ids_file, "w") as f:
    json.dump(list(processed_ids), f)
print(f"Updated processed IDs in '{processed_ids_file}'.")

logging.info(f"Total Posts: {len(processed_ids)}")
logging.info("---------- Application Completed ----------")

print(f"Total Posts: {len(processed_ids)}")
print("Successfully ran the application.")