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

from tree_sitter_languages import get_language, get_parser

class Parser:
    def run(self, filepath):
        """
        Parses a file using Tree-sitter to extract its AST.
        """
        with open(filepath, 'r') as f:
            code = f.read()

        language = get_language(filepath)
        parser = get_parser(language.name)
        tree = parser.parse(bytes(code, "utf8"))
        return tree

class Formatter:
    def run(self, docs):
        # Logic to format the documentation
        pass
