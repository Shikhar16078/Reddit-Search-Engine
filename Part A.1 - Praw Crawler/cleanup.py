import os

# File paths
log_file = "logs.txt"
processed_ids = "processed_ids.json"
directory = "."  # The current directory, modify this if the files are in a different directory
image_directory = "Assets/Images"  # Directory where images are stored

# Function to delete files
def delete_files(files):
    for file in files:
        if os.path.exists(file):
            try:
                os.remove(file)
            except Exception as e:
                print(f"Error deleting {file}: {e}")
        else:
            print(f"{file} does not exist.")
    print("Successfully Deleted all the files.")

# Function to delete files with a specific prefix
def delete_files_with_prefix(prefix, directory):
    files_deleted = []
    for filename in os.listdir(directory):
        if filename.startswith(prefix):
            file_path = os.path.join(directory, filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    files_deleted.append(filename)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
    print("Successfully Deleted Post Files.")
    return files_deleted

# Function to delete all images in the Assets/Images directory
def delete_all_images(image_directory):
    if os.path.exists(image_directory):
        for filename in os.listdir(image_directory):
            image_path = os.path.join(image_directory, filename)
            if os.path.isfile(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Error deleting image {image_path}: {e}")
    else:
        print(f"{image_directory} does not exist.")
    print(f"Successfully Deleted all the images.")


# Files to delete
files_to_delete = [log_file, processed_ids]

# Delete specific files
delete_files(files_to_delete)

# Delete all files with 'reddit_batch_' prefix
delete_files_with_prefix('reddit_batch_', directory)

# Delete all images in the Assets/Images folder
delete_all_images(image_directory)
