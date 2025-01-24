import os

# File paths
log_file = "logs.txt"
reddit_file = "reddit_posts.txt"
processed_ids = "processed_ids.json"

# Function to delete files
def delete_files(files):
    for file in files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Successfully deleted: {file}")
            except Exception as e:
                print(f"Error deleting {file}: {e}")
        else:
            print(f"{file} does not exist.")

# Files to delete
files_to_delete = [log_file, reddit_file, processed_ids]

# Delete the files
delete_files(files_to_delete)
