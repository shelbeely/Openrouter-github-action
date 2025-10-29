# tests/test_doc_gen.py
import os
import shutil
import tempfile
import unittest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

from src.doc_gen_manager import DocGenManager

class TestDocGenManager(unittest.TestCase):
    def setUp(self):
        self.repo_url = "https://github.com/openai/openai-python"
        self.target_doc_set = "API Reference,Getting Started"
        self.changelog_agent = "false"
        self.doc_flavor = "MkDocs"
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(os.getcwd(), f"docs_{self.doc_flavor.lower()}")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    @patch("src.doc_gen_manager.RepoFetcher")
    @patch("src.doc_gen_manager.tempfile.mkdtemp")
    @patch("src.doc_gen_manager.shutil.rmtree")
    @patch("src.doc_gen_manager.Agent.__call__", new_callable=AsyncMock)
    def test_run(self, mock_agent_call, mock_rmtree, mock_mkdtemp, MockRepoFetcher):
        # Mock the RepoFetcher to avoid cloning a real repository
        mock_repo_fetcher = MockRepoFetcher.return_value
        mock_repo_fetcher.run.return_value = None

        # Mock tempfile.mkdtemp to return our test directory
        mock_mkdtemp.return_value = self.test_dir

        # Mock the Agent.__call__ method to return a dummy response
        mock_agent_call.return_value = MagicMock(text="This is a dummy response from the AI agent.")

        # Create a dummy file in the test directory
        dummy_file_path = os.path.join(self.test_dir, "dummy.py")
        with open(dummy_file_path, "w") as f:
            f.write('def dummy_function():\n    """A dummy function."""\n    pass')

        # Create the DocGenManager
        manager = DocGenManager(
            self.repo_url,
            self.target_doc_set,
            self.changelog_agent,
            "", # doc_mode is no longer used
            "beginner",
            self.doc_flavor,
            "false",
            "test_token"
        )

        # Run the manager
        asyncio.run(manager.run())

        # Check if the output directory was created
        self.assertTrue(os.path.exists(self.output_dir))

        # Check if the output files were created
        api_ref_file = os.path.join(self.output_dir, "api_reference.md")
        getting_started_file = os.path.join(self.output_dir, "getting_started.md")
        self.assertTrue(os.path.exists(api_ref_file))
        self.assertTrue(os.path.exists(getting_started_file))

if __name__ == "__main__":
    unittest.main()
