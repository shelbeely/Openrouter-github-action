# src/tools/doc_gen_tools.py

import git

class RepoFetcher:
    def run(self, url, path):
        """
        Clones a repository from a URL to a local path.
        """
        git.Repo.clone_from(url, path)

import os

class FilesystemReader:
    def run(self, path, extensions=None):
        """
        Reads all files in a directory with the given extensions.
        """
        for root, _, files in os.walk(path):
            for file in files:
                if extensions is None or file.endswith(tuple(extensions)):
                    yield os.path.join(root, file)

import os
from tree_sitter_languages import get_language, get_parser

class Parser:
    def run(self, filepath):
        """
        Parses a file using Tree-sitter to extract its AST.
        """
        with open(filepath, 'r') as f:
            code = f.read()

        lang = self._get_language_from_filepath(filepath)
        if lang:
            parser = get_parser(lang)
            tree = parser.parse(bytes(code, "utf8"))
            return tree
        return None

    def _get_language_from_filepath(self, filepath):
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".c": "c",
            ".cpp": "cpp",
        }
        _, extension = os.path.splitext(filepath)
        return extension_map.get(extension)

import yaml

class Formatter:
    def run(self, outline, output_dir):
        raise NotImplementedError

class MkDocsFormatter(Formatter):
    def run(self, outline, output_dir):
        """
        Generates an mkdocs.yml file and organizes the documentation.
        """
        mkdocs_config = {
            "site_name": "My Docs",
            "nav": [],
        }

        for section in outline["sections"]:
            for page in section["pages"]:
                filename = f"{page['title'].replace(' ', '_').lower()}.md"
                mkdocs_config["nav"].append({page["title"]: filename})

        with open(os.path.join(output_dir, "mkdocs.yml"), "w") as f:
            yaml.dump(mkdocs_config, f)
