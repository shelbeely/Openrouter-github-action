# src/agents/contributor_guide_agent.py

class ContributorGuideAgent:
    def run(self, outline, repo_path):
        """
        Generates a contributor guide.
        """
        contributing_guide = """
# Contributing

We welcome contributions! Please follow these guidelines:

1.  Fork the repository.
2.  Create a new branch.
3.  Make your changes.
4.  Submit a pull request.
"""
        outline["sections"].append({"title": "Contributing Guide", "pages": [{"title": "CONTRIBUTING", "content": contributing_guide}]})
        return outline
