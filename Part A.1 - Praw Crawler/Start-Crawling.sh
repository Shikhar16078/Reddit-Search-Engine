read -p "Enter a space-separated sub-reddit topics to crawl: " user_input

if [ -z "$user_input" ]; then
    echo "No input was provided."
else
    echo "These are the inputs: $user_input"
fi

if [ -n "$user_input" ]; then
    python3 crawl_reddit.py "$user_input"
else
    python3 crawl_reddit.py
fi