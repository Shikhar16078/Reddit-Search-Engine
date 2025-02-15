@echo off
set /p user_input=Enter Space Separated 'Topics' to Crawl: 

if not "%user_input%"=="" (
    python crawl_reddit.py %user_input%
) else (
    python crawl_reddit.py
)