# src/agents/doc_gen_agents.py

from agents import FunctionTool
from src.tools.doc_gen_tools import FilesystemReader, Parser
from src.tools.spec_harvesters import OpenAPISpecHarvester
from src.utils import is_thin_content
import os
import git
import yaml
import json

class OutlineTool(FunctionTool):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    async def __call__(self) -> str:
        """
        Scans the codebase and generates a documentation outline.
        """
        outline = {"sections": []}
        fs_reader = FilesystemReader()
        for filepath in fs_reader.run(self.repo_path):
            outline["sections"].append({"title": filepath, "pages": []})
        return json.dumps(outline)

class ApiRefTool(FunctionTool):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    async def __call__(self) -> str:
        """
        Generates API reference pages from the codebase and OpenAPI specs.
        """
        outline = {"sections": []}
        parser = Parser()
        fs_reader = FilesystemReader()
        for filepath in fs_reader.run(self.repo_path):
            try:
                tree = parser.run(filepath)
                if tree:
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
                        outline["sections"].append({"title": "API Reference", "pages": [{"title": "API Reference", "content": content}]})
            except Exception:
                pass

        spec_harvester = OpenAPISpecHarvester()
        specs = spec_harvester.run(self.repo_path)
        for spec in specs:
            content = "## OpenAPI Reference\n"
            for path, methods in spec.get("paths", {}).items():
                for method, details in methods.items():
                    content += f"### `{method.upper()} {path}`\n{details.get('summary', '')}\n\n"

            outline["sections"].append({"title": "OpenAPI Reference", "pages": [{"title": "OpenAPI Reference", "content": content}]})

        return json.dumps(outline)

    def _extract_functions(self, node):
        functions = []
        if node.type == 'function_definition':
            name = node.child_by_field_name('name').text.decode()
            docstring_node = self._find_docstring_node(node)
            docstring = docstring_node.text.decode() if docstring_node else ""
            functions.append({'name': name, 'docstring': docstring})
        for child in node.children:
            functions.extend(self._extract_functions(child))
        return functions

    def _find_docstring_node(self, node):
        body_node = node.child_by_field_name('body')
        if body_node and body_node.children:
            first_child = body_node.children[0]
            if first_child.type == 'expression_statement' and first_child.children and first_child.children[0].type == 'string':
                return first_child.children[0]
        return None

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

class GuideTool(FunctionTool):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    async def __call__(self) -> str:
        """
        Generates how-to guides and tutorials from READMEs and other documentation.
        """
        outline = {"sections": []}
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.lower() == "readme.md":
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r') as f:
                        content = f.read()
                    outline["sections"].append({"title": "Guide", "pages": [{"title": "README", "content": content}]})
        return json.dumps(outline)

class GettingStartedTool(FunctionTool):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    async def __call__(self, doc_audience: str = "beginner") -> str:
        """
        Generates a Getting Started guide by looking for common files.
        """
        getting_started_content = ""
        found_files = []
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.lower() in ["install.md", "contributing.md", "readme.md"]:
                    filepath = os.path.join(root, file)
                    found_files.append(filepath)
                    with open(filepath, 'r') as f:
                        getting_started_content += f.read() + "\n\n"

        if is_thin_content(getting_started_content):
            getting_started_content += f"\n\n**TODO:** This document is incomplete. Please add more information to the following files: {', '.join(found_files)}"

        return getting_started_content

class TaskGuidesTool(FunctionTool):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    async def __call__(self, doc_audience: str = "beginner") -> str:
        """
        Generates a set of task guides by analyzing the repository.
        """
        return "This is a placeholder for the Task Guides."

class ConceptsTool(FunctionTool):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    async def __call__(self, doc_audience: str = "beginner") -> str:
        """
        Generates a set of conceptual documents by analyzing the repository.
        """
        return "This is a placeholder for the Concepts documentation."

class FAQTool(FunctionTool):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    async def __call__(self, doc_audience: str = "beginner") -> str:
        """
        Generates a set of frequently asked questions by analyzing the repository.
        """
        return "This is a placeholder for the FAQ."

class TroubleshootingTool(FunctionTool):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    async def __call__(self, doc_audience: str = "beginner") -> str:
        """
        Generates a troubleshooting guide by analyzing the repository.
        """
        return "This is a placeholder for the Troubleshooting guide."

class GlossaryTool(FunctionTool):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    async def __call__(self, doc_audience: str = "beginner") -> str:
        """
        Generates a glossary of terms by analyzing the repository.
        """
        return "This is a placeholder for the Glossary."

class ChangelogTool(FunctionTool):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    async def __call__(self) -> str:
        """
        Generates a changelog from the git history, supporting semantic release notes.
        """
        repo = git.Repo(self.repo_path)
        tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)

        changelog = "# Changelog\n\n"

        for i, tag in enumerate(tags):
            changelog += f"## {tag.name} ({tag.commit.committed_datetime.date()})\n\n"

            if i > 0:
                commits = repo.iter_commits(f"{tags[i-1].name}..{tag.name}")
            else:
                commits = repo.iter_commits(tag.name)

            features = []
            fixes = []
            other = []

            for commit in commits:
                if commit.summary.startswith("feat:"):
                    features.append(f"- {commit.summary}")
                elif commit.summary.startswith("fix:"):
                    fixes.append(f"- {commit.summary}")
                else:
                    other.append(f"- {commit.summary}")

            if features:
                changelog += "### Features\n"
                changelog += "\n".join(features) + "\n\n"

            if fixes:
                changelog += "### Bug Fixes\n"
                changelog += "\n".join(fixes) + "\n\n"

            if other:
                changelog += "### Other Changes\n"
                changelog += "\n".join(other) + "\n\n"

        return changelog

class EditorTool(FunctionTool):
    def __init__(self, output_dir, doc_flavor):
        self.output_dir = output_dir
        self.doc_flavor = doc_flavor

    async def __call__(self, outline: str) -> None:
        """
        Stitches the documentation together into a cohesive set.
        """
        outline = json.loads(outline)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for section in outline["sections"]:
            for page in section["pages"]:
                filename = f"{page['title'].replace(' ', '_').lower()}.md"
                filepath = os.path.join(self.output_dir, filename)

                frontmatter = {"title": page["title"]}

                with open(filepath, 'w') as f:
                    f.write("---\n")
                    f.write(yaml.dump(frontmatter))
                    f.write("---\n")
                    f.write(page["content"])

        formatters = {
            "MkDocs": MkDocsFormatter(),
            "Docusaurus": DocusaurusFormatter(),
            "Sphinx": SphinxFormatter(),
        }

        if self.doc_flavor in formatters:
            formatter = formatters[self.doc_flavor]
            formatter.run(outline, self.output_dir)
