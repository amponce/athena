import os
from github import Github

github_token = os.getenv('GITHUB_TOKEN')
if github_token:
    g = Github(github_token)
else:
    g = None
    print("Warning: GITHUB_TOKEN is not set. GitHub functionalities will be disabled.")

def get_repo_notifications(repo_name):
    if g is None:
        print("GitHub client not initialized. Skipping repository notifications retrieval.")
        return {
            "issues": [],
            "pull_requests": []
        }
    try:
        repo = g.get_repo(repo_name)
        issues = repo.get_issues(state='open')
        pull_requests = repo.get_pulls(state='open')
        notifications = {
            "issues": [issue.title for issue in issues],
            "pull_requests": [pr.title for pr in pull_requests]
        }
        return notifications
    except Exception as e:
        print(f"Error in get_repo_notifications: {e}")
        return {
            "issues": [],
            "pull_requests": []
        }