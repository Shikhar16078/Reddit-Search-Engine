read -p "Enter a space-separated sub-reddit topics to crawl: " user_input

if [ -n "$user_input" ]; then
    python3 crawl_reddit.py "$user_input"
else
    python3 crawl_reddit.py
fi