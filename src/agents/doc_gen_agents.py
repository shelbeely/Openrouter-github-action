# src/agents/doc_gen_agents.py

from src.tools.doc_gen_tools import FilesystemReader, Parser

class OutlineAgent:
    def run(self, repo_path):
        """
        Scans the codebase and generates a documentation outline.
        """
        outline = {"sections": []}

        # Scan the codebase to identify key modules and components
        fs_reader = FilesystemReader()

        for filepath in fs_reader.run(repo_path):
            # In a real implementation, we would extract more meaningful
            # information from the AST. For now, we'll just add the file path.
            outline["sections"].append({"title": filepath, "pages": []})

        return outline

from src.tools.doc_gen_tools import Parser

class ApiRefAgent:
    def run(self, outline):
        """
        Generates API reference pages from the codebase.
        """
        parser = Parser()
        for section in outline["sections"]:
            filepath = section["title"]
            try:
                tree = parser.run(filepath)
                # Extract functions and classes from the AST
                functions = self._extract_functions(tree.root_node)
                classes = self._extract_classes(tree.root_node)

                content = ""
                if functions:
                    content += "## Functions\n"
                    for func in functions:
                        content += f"### `{func['name']}`\n{func['docstring']}\n\n"

                if classes:
                    content += "## Classes\n"
                    for cls in classes:
                        content += f"### `{cls['name']}`\n{cls['docstring']}\n\n"

                if content:
                    section["pages"].append({"title": "API Reference", "content": content})
            except Exception:
                pass
        return outline

    def _extract_functions(self, node):
        functions = []
        if node.type == 'function_definition':
            name = node.child_by_field_name('name').text.decode()
            docstring = ''
            if node.child_by_field_name('body').children and node.child_by_field_name('body').children[0].type == 'expression_statement' and node.child_by_field_name('body').children[0].children[0].type == 'string':
                docstring = node.child_by_field_name('body').children[0].children[0].text.decode()
            functions.append({'name': name, 'docstring': docstring})
        for child in node.children:
            functions.extend(self._extract_functions(child))
        return functions

    def _extract_classes(self, node):
        classes = []
        if node.type == 'class_definition':
            name = node.child_by_field_name('name').text.decode()
            docstring = ''
            if node.child_by_field_name('body').children and node.child_by_field_name('body').children[0].type == 'expression_statement' and node.child_by_field_name('body').children[0].children[0].type == 'string':
                docstring = node.child_by_field_name('body').children[0].children[0].text.decode()
            classes.append({'name': name, 'docstring': docstring})
        for child in node.children:
            classes.extend(self._extract_classes(child))
        return classes

import os

class GuideAgent:
    def run(self, repo_path, outline):
        """
        Generates how-to guides and tutorials from READMEs and other documentation.
        """
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.lower() == "readme.md":
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r') as f:
                        content = f.read()
                    outline["sections"].append({"title": "Guide", "pages": [{"title": "README", "content": content}]})
        return outline

class GlossaryAgent:
    def run(self, outline):
        """
        Creates a glossary of repeated terms.
        """
        # In a real implementation, we would scan the codebase for repeated terms.
        # For now, we'll just add a placeholder.
        outline["sections"].append({"title": "Glossary", "pages": [{"title": "Glossary", "content": "This is a placeholder glossary."}]})
        return outline

import git

class ChangelogAgent:
    def run(self, repo_path, outline):
        """
        Generates a changelog from the git history.
        """
        repo = git.Repo(repo_path)
        changelog = ""
        for commit in repo.iter_commits():
            changelog += f"- {commit.summary}\n"

        outline["sections"].append({"title": "Changelog", "pages": [{"title": "Changelog", "content": changelog}]})
        return outline

import os
import yaml

class EditorAgent:
    def run(self, outline, output_dir="docs"):
        """
        Stitches the documentation together into a cohesive set.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for section in outline["sections"]:
            for page in section["pages"]:
                filename = f"{page['title'].replace(' ', '_').lower()}.md"
                filepath = os.path.join(output_dir, filename)

                frontmatter = {"title": page["title"]}

                with open(filepath, 'w') as f:
                    f.write("---\n")
                    f.write(yaml.dump(frontmatter))
                    f.write("---\n")
                    f.write(page["content"])
