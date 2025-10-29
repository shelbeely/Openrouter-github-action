# src/doc_gen_manager.py

import tempfile
import shutil
from src.agents.doc_gen_agents import OutlineAgent, ApiRefAgent, GuideAgent, GlossaryAgent, ChangelogAgent, EditorAgent, GettingStartedAgent, TaskGuidesAgent, ConceptsAgent, FAQAgent, TroubleshootingAgent
from src.tools.doc_gen_tools import RepoFetcher
from src.tools.repo_signals import RepoSignalsTool

class DocGenManager:
    def __init__(self, repo_url, target_doc_set, changelog_agent, doc_mode, doc_audience, doc_flavor, enable_repo_signals, github_token):
        self.repo_url = repo_url
        self.target_doc_set = target_doc_set.split(',')
        self.changelog_agent_enabled = changelog_agent.lower() == 'true'
        self.doc_mode = doc_mode
        self.doc_audience = doc_audience
        self.doc_flavor = doc_flavor
        self.enable_repo_signals = enable_repo_signals.lower() == 'true'
        self.github_token = github_token

    def run(self):
        """
        Orchestrates the documentation generation workflow.
        """
        repo_path = tempfile.mkdtemp()
        try:
            # Fetch the repository
            repo_fetcher = RepoFetcher()
            repo_fetcher.run(self.repo_url, repo_path)

            # Run the outline agent
            outline_agent = OutlineAgent()
            outline = outline_agent.run(repo_path)

            # If repo signals are enabled, fetch issues and PRs
            if self.enable_repo_signals:
                repo_name = self.repo_url.replace("https://github.com/", "")
                repo_signals_tool = RepoSignalsTool(self.github_token, repo_name)
                issues = repo_signals_tool.get_issues()
                pull_requests = repo_signals_tool.get_pull_requests()

                repo_signals_section = {"title": "Repo Signals", "pages": []}
                for issue in issues:
                    repo_signals_section["pages"].append({"title": f"Issue #{issue.number}: {issue.title}", "content": issue.body})
                for pr in pull_requests:
                    repo_signals_section["pages"].append({"title": f"PR #{pr.number}: {pr.title}", "content": pr.body})
                outline["sections"].append(repo_signals_section)

            # Run the parallel worker agents
            worker_agents = {
                "API Reference": ApiRefAgent(),
                "Tutorials": GuideAgent(),
                "Getting Started": GettingStartedAgent(),
                "Glossary": GlossaryAgent(),
                "Task Guides": TaskGuidesAgent(),
                "Concepts": ConceptsAgent(),
                "FAQ": FAQAgent(),
                "Troubleshooting": TroubleshootingAgent(),
            }

            for doc_type in self.target_doc_set:
                if doc_type in worker_agents:
                    agent = worker_agents[doc_type]
                    if isinstance(agent, (GuideAgent, ApiRefAgent)):
                        outline = agent.run(outline, repo_path)
                    elif isinstance(agent, GettingStartedAgent):
                        outline = agent.run(outline, repo_path, self.doc_audience)
                    else:
                        outline = agent.run(outline, self.doc_audience)

            if self.changelog_agent_enabled:
                changelog_agent = ChangelogAgent()
                outline = changelog_agent.run(repo_path, outline)

            # Run the editor agent
            editor_agent = EditorAgent()
            editor_agent.run(outline, output_dir=f"docs_{self.doc_flavor.lower()}", doc_flavor=self.doc_flavor)

        finally:
            shutil.rmtree(repo_path)
