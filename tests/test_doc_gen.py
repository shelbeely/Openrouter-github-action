# tests/test_doc_gen.py
import os
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from src.doc_gen_manager import DocGenManager

class TestDocGenManager(unittest.TestCase):
    def setUp(self):
        self.repo_url = "https://github.com/openai/openai-python"
        self.target_doc_set = "api_ref"
        self.changelog_agent = "false"
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(os.getcwd(), "docs")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)

    @patch("src.doc_gen_manager.RepoFetcher")
    @patch("src.doc_gen_manager.tempfile.mkdtemp")
    @patch("src.doc_gen_manager.shutil.rmtree")
    def test_run(self, mock_rmtree, mock_mkdtemp, MockRepoFetcher):
        # Mock the RepoFetcher to avoid cloning a real repository
        mock_repo_fetcher = MockRepoFetcher.return_value
        mock_repo_fetcher.run.return_value = None

        # Mock tempfile.mkdtemp to return our test directory
        mock_mkdtemp.return_value = self.test_dir

        # Create a dummy file in the test directory
        dummy_file_path = os.path.join(self.test_dir, "dummy.py")
        with open(dummy_file_path, "w") as f:
            f.write("def dummy_function(): pass")

        # Create the DocGenManager
        manager = DocGenManager(self.repo_url, self.target_doc_set, self.changelog_agent)

        # Run the manager
        manager.run()

        # Check if the output directory was created
        self.assertTrue(os.path.exists(self.output_dir))

        # Check if the output file was created
        output_file = os.path.join(self.output_dir, "api_reference.md")
        self.assertTrue(os.path.exists(output_file))

if __name__ == "__main__":
    unittest.main()
