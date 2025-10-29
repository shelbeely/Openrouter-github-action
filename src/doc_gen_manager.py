# src/doc_gen_manager.py

import tempfile
import shutil
import asyncio
import json
from agents import Agent
from src.agents.doc_gen_agents import OutlineTool, ApiRefTool, GuideTool, GlossaryTool, ChangelogTool, EditorTool, GettingStartedTool, TaskGuidesTool, ConceptsTool, FAQTool, TroubleshootingTool
from src.agents.diagrammer_agent import DiagrammerTool
from src.agents.contributor_guide_agent import ContributorGuideTool
from src.tools.doc_gen_tools import RepoFetcher
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

            # Create an agent to orchestrate the documentation generation
            orchestrator_agent = Agent(
                name="Orchestrator Agent",
                tools=[
                    OutlineTool(repo_path),
                    ApiRefTool(repo_path),
                    GuideTool(repo_path),
                    GettingStartedTool(repo_path),
                    GlossaryTool(repo_path),
                    TaskGuidesTool(repo_path),
                    ConceptsTool(repo_path),
                    FAQTool(repo_path),
                    TroubleshootingTool(repo_path),
                    DiagrammerTool(repo_path),
                    ContributorGuideTool(repo_path),
                    ChangelogTool(repo_path),
                    EditorTool(f"docs_{self.doc_flavor.lower()}", self.doc_flavor),
                ],
                instructions=f"You are a technical writer responsible for generating a comprehensive documentation set for a software project. The target audience is {self.doc_audience}. The desired documentation set includes: {', '.join(self.target_doc_set)}.",
            )

            # Run the orchestrator agent
            response = await orchestrator_agent(f"Generate the documentation set.")

            # The EditorTool will write the files, so we don't need to do anything else here.

        finally:
            shutil.rmtree(repo_path)
