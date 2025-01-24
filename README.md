## Project Overview

This repository aims to develop a search engine utilizing Reddit posts.

## Current Status

We have successfully integrated the Reddit PRAW API. However, we’ve noticed some performance issues where the code seems to run slower than expected.

##### Potential Causes

- Inefficient API request handling
- Reauthentication on each API call
- Excessive skipped post requests

## Next Steps

1. Study the Reddit API in more detail to better understand its behavior.
2. Investigate and identify the root cause of the performance bottleneck.
3. Optimize the code to address any issues and improve speed.