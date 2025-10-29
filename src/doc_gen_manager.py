# src/doc_gen_manager.py

import tempfile
import shutil
from src.agents.doc_gen_agents import OutlineAgent, ApiRefAgent, GuideAgent, GlossaryAgent, ChangelogAgent, EditorAgent
from src.tools.doc_gen_tools import RepoFetcher

class DocGenManager:
    def __init__(self, repo_url, target_doc_set, changelog_agent):
        self.repo_url = repo_url
        self.target_doc_set = target_doc_set.split(',')
        self.changelog_agent_enabled = changelog_agent.lower() == 'true'

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

            # Run the parallel worker agents
            worker_agents = {
                "api_ref": ApiRefAgent(),
                "tutorials": GuideAgent(),
                "getting_started": GuideAgent(),
                "glossary": GlossaryAgent(),
            }

            for doc_type in self.target_doc_set:
                if doc_type in worker_agents:
                    if isinstance(worker_agents[doc_type], GuideAgent):
                         outline = worker_agents[doc_type].run(repo_path, outline)
                    else:
                        outline = worker_agents[doc_type].run(outline)

            if self.changelog_agent_enabled:
                changelog_agent = ChangelogAgent()
                outline = changelog_agent.run(repo_path, outline)

            # Run the editor agent
            editor_agent = EditorAgent()
            editor_agent.run(outline)

        finally:
            shutil.rmtree(repo_path)
