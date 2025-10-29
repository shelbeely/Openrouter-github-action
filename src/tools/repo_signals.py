# src/tools/repo_signals.py
from github import Github

class RepoSignalsTool:
    def __init__(self, github_token, repo_name):
        self.github = Github(github_token)
        self.repo = self.github.get_repo(repo_name)

    def get_issues(self):
        return self.repo.get_issues(state="all")

    def get_pull_requests(self):
        return self.repo.get_pulls(state="all")

    def get_discussions(self):
        # The PyGithub library does not yet support the Discussions API.
        # This is a placeholder for future implementation.
        return []
