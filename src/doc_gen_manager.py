# src/doc_gen_manager.py

import tempfile
import shutil
from agents import Agent
from src.tools.doc_gen_tools import RepoFetcher, OutlineTool, ApiRefTool, GuideTool, GlossaryTool, ChangelogTool, EditorTool, GettingStartedTool, TaskGuidesTool, ConceptsTool, FAQTool, TroubleshootingTool, DiagrammerTool, ContributorGuideTool
from src.tools.dev_tools import create_new_tool, create_pull_request
from src.tools.repo_signals import RepoSignalsTool

class DocGenManager:
    def __init__(self, repo_url, target_doc_set, changelog_agent, doc_audience, doc_flavor, enable_repo_signals, github_token):
        self.repo_url = repo_url
        self.target_doc_set = target_doc_set.split(',')
        self.changelog_agent_enabled = changelog_agent.lower() == 'true'
        self.doc_audience = doc_audience
        self.doc_flavor = doc_flavor
        self.enable_repo_signals = enable_repo_signals.lower() == 'true'
        self.github_token = github_token

    async def run(self):
        """
        Orchestrates the documentation generation workflow.
        """
        repo_path = tempfile.mkdtemp()
        try:
            # Fetch the repository
            repo_fetcher = RepoFetcher()
            repo_fetcher.run(self.repo_url, repo_path)

            # Initialize the tools
            tools = [
                OutlineTool(repo_path),
                ApiRefTool(repo_path),
                GuideTool(repo_path),
                GlossaryTool(repo_path),
                ChangelogTool(repo_path),
                EditorTool(f"docs_{self.doc_flavor.lower()}", self.doc_flavor),
                GettingStartedTool(repo_path),
                TaskGuidesTool(repo_path),
                ConceptsTool(repo_path),
                FAQTool(repo_path),
                TroubleshootingTool(repo_path),
                DiagrammerTool(repo_path),
                ContributorGuideTool(repo_path),
                create_new_tool,
                create_pull_request,
            ]
            if self.enable_repo_signals:
                repo_name = self.repo_url.replace("https://github.com/", "")
                tools.append(RepoSignalsTool(self.github_token, repo_name))

            # Create the orchestrator agent
            orchestrator_agent = Agent(
                name="Orchestrator Agent",
                tools=tools,
                instructions=f"You are an AI agent responsible for generating documentation for the repository at {self.repo_url}. "
                             f"Your target audience is {self.doc_audience}, and the desired documentation flavor is {self.doc_flavor}. "
                             f"Please generate the following documentation set: {', '.join(self.target_doc_set)}."
            )

            # Run the agent
            await orchestrator_agent(f"Generate the documentation for the repository at {self.repo_url}.")

        finally:
            shutil.rmtree(repo_path)
