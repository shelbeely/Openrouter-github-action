# src/tools/doc_gen_tools.py

import git
import os
import yaml
import json
from tree_sitter_languages import get_language, get_parser
from agents import function_tool, Agent
from src.tools.spec_harvesters import OpenAPISpecHarvester
from src.utils import is_thin_content

class RepoFetcher:
    def run(self, url, path):
        """
        Clones a repository from a URL to a local path.
        """
        git.Repo.clone_from(url, path)

class FilesystemReader:
    def run(self, path, extensions=None):
        """
        Reads all files in a directory with the given extensions.
        """
        for root, _, files in os.walk(path):
            for file in files:
                if extensions is None or file.endswith(tuple(extensions)):
                    yield os.path.join(root, file)

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

class DocusaurusFormatter(Formatter):
    def run(self, outline, output_dir):
        """
        Generates a docusaurus.config.js file and organizes the documentation.
        """
        docusaurus_config = {
            "title": "My Docs",
            "themeConfig": {
                "sidebar": {
                    "links": [],
                },
            },
        }

        for section in outline["sections"]:
            for page in section["pages"]:
                filename = f"{page['title'].replace(' ', '_').lower()}.md"
                docusaurus_config["themeConfig"]["sidebar"]["links"].append({
                    "to": filename,
                    "label": page["title"],
                })

        with open(os.path.join(output_dir, "docusaurus.config.js"), "w") as f:
            f.write(f"module.exports = {json.dumps(docusaurus_config, indent=2)};")

class SphinxFormatter(Formatter):
    def run(self, outline, output_dir):
        """
        Generates a conf.py file and organizes the documentation.
        """
        conf_py_content = f"""
project = 'My Docs'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_sidebars = {{
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
        'donate.html',
    ]
}}
master_doc = 'index'
"""
        with open(os.path.join(output_dir, "conf.py"), "w") as f:
            f.write(conf_py_content)

        index_rst_content = \"\"\"
My Docs
=======

.. toctree::
   :maxdepth: 2
   :caption: Contents:

\"\"\"
        for section in outline["sections"]:
            for page in section["pages"]:
                filename = f"{page['title'].replace(' ', '_').lower()}"
                index_rst_content += f"   {filename}\\n"

        with open(os.path.join(output_dir, "index.rst"), "w") as f:
            f.write(index_rst_content)

@function_tool
async def outline_tool(repo_path: str) -> str:
    """
    Scans the codebase and generates a documentation outline.
    """
    outline = {"sections": []}
    fs_reader = FilesystemReader()
    for filepath in fs_reader.run(repo_path):
        outline["sections"].append({"title": filepath, "pages": []})
    return json.dumps(outline)

@function_tool
async def api_ref_tool(repo_path: str) -> str:
    """
    Generates API reference pages from the codebase and OpenAPI specs.
    """
    outline = {"sections": []}
    parser = Parser()
    fs_reader = FilesystemReader()
    for filepath in fs_reader.run(repo_path):
        try:
            tree = parser.run(filepath)
            if tree:
                functions = _extract_functions(tree.root_node)
                classes = _extract_classes(tree.root_node)

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
    specs = spec_harvester.run(repo_path)
    for spec in specs:
        content = "## OpenAPI Reference\n"
        for path, methods in spec.get("paths", {}).items():
            for method, details in methods.items():
                content += f"### `{method.upper()} {path}`\n{details.get('summary', '')}\n\n"

        outline["sections"].append({"title": "OpenAPI Reference", "pages": [{"title": "OpenAPI Reference", "content": content}]})

    return json.dumps(outline)

def _extract_functions(node):
    functions = []
    if node.type == 'function_definition':
        name = node.child_by_field_name('name').text.decode()
        docstring_node = _find_docstring_node(node)
        docstring = docstring_node.text.decode() if docstring_node else ""
        functions.append({'name': name, 'docstring': docstring})
    for child in node.children:
        functions.extend(_extract_functions(child))
    return functions

def _find_docstring_node(node):
    body_node = node.child_by_field_name('body')
    if body_node and body_node.children:
        first_child = body_node.children[0]
        if first_child.type == 'expression_statement' and first_child.children and first_child.children[0].type == 'string':
            return first_child.children[0]
    return None

def _extract_classes(node):
    classes = []
    if node.type == 'class_definition':
        name = node.child_by_field_name('name').text.decode()
        docstring = ''
        if node.child_by_field_name('body').children and node.child_by_field_name('body').children[0].type == 'expression_statement' and node.child_by_field_name('body').children[0].children[0].type == 'string':
            docstring = node.child_by_field_name('body').children[0].children[0].text.decode()
        classes.append({'name': name, 'docstring': docstring})
    for child in node.children:
        classes.extend(_extract_classes(child))
    return classes

@function_tool
async def guide_tool(repo_path: str) -> str:
    """
    Generates how-to guides and tutorials from READMEs and other documentation.
    """
    outline = {"sections": []}
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.lower() == "readme.md":
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                outline["sections"].append({"title": "Guide", "pages": [{"title": "README", "content": content}]})
    return json.dumps(outline)

@function_tool
async def getting_started_tool(repo_path: str, doc_audience: str = "beginner") -> str:
    """
    Generates a Getting Started guide by looking for common files.
    """
    getting_started_content = ""
    found_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.lower() in ["install.md", "contributing.md", "readme.md"]:
                filepath = os.path.join(root, file)
                found_files.append(filepath)
                with open(filepath, 'r') as f:
                    getting_started_content += f.read() + "\n\n"

    if is_thin_content(getting_started_content):
        getting_started_content += f"\n\n**TODO:** This document is incomplete. Please add more information to the following files: {', '.join(found_files)}"

    return getting_started_content

@function_tool
async def task_guides_tool(repo_path: str, doc_audience: str = "beginner") -> str:
    """
    Generates a set of task guides by analyzing the repository.
    """
    agent = Agent(
        name="Task Guides Agent",
        tools=[],
        instructions="You are a technical writer generating a set of task guides for a software project.",
    )
    response = await agent(f"Generate a set of task guides for a software project. The target audience is {doc_audience}. The repository is located at {repo_path}.")
    return response.text

@function_tool
async def concepts_tool(repo_path: str, doc_audience: str = "beginner") -> str:
    """
    Generates a set of conceptual documents by analyzing the repository.
    """
    agent = Agent(
        name="Concepts Agent",
        tools=[],
        instructions="You are a technical writer generating a set of conceptual documents for a software project.",
    )
    response = await agent(f"Generate a set of conceptual documents for a software project. The target audience is {doc_audience}. The repository is located at {repo_path}.")
    return response.text

@function_tool
async def faq_tool(repo_path: str, doc_audience: str = "beginner") -> str:
    """
    Generates a set of frequently asked questions by analyzing the repository.
    """
    agent = Agent(
        name="FAQ Agent",
        tools=[],
        instructions="You are a technical writer generating a set of frequently asked questions for a software project.",
    )
    response = await agent(f"Generate a set of frequently asked questions for a software project. The target audience is {doc_audience}. The repository is located at {repo_path}.")
    return response.text

@function_tool
async def troubleshooting_tool(repo_path: str, doc_audience: str = "beginner") -> str:
    """
    Generates a troubleshooting guide by analyzing the repository.
    """
    agent = Agent(
        name="Troubleshooting Agent",
        tools=[],
        instructions="You are a technical writer generating a troubleshooting guide for a software project.",
    )
    response = await agent(f"Generate a troubleshooting guide for a software project. The target audience is {doc_audience}. The repository is located at {repo_path}.")
    return response.text

@function_tool
async def glossary_tool(repo_path: str, doc_audience: str = "beginner") -> str:
    """
    Generates a glossary of terms by analyzing the repository.
    """
    agent = Agent(
        name="Glossary Agent",
        tools=[],
        instructions="You are a technical writer generating a glossary of terms for a software project.",
    )
    response = await agent(f"Generate a glossary of terms for a software project. The target audience is {doc_audience}. The repository is located at {repo_path}.")
    return response.text

@function_tool
async def changelog_tool(repo_path: str) -> str:
    """
    Generates a changelog from the git history, supporting semantic release notes.
    """
    repo = git.Repo(repo_path)
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

@function_tool
async def editor_tool(output_dir: str, doc_flavor: str, outline: str) -> None:
    """
    Stitches the documentation together into a cohesive set.
    """
    outline = json.loads(outline)
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

    formatters = {
        "MkDocs": MkDocsFormatter(),
        "Docusaurus": DocusaurusFormatter(),
        "Sphinx": SphinxFormatter(),
    }

    if doc_flavor in formatters:
        formatter = formatters[doc_flavor]
        formatter.run(outline, output_dir)

from pycg import pycg

@function_tool
async def diagrammer_tool(repo_path: str) -> str:
    """
    Generates a class diagram from the source code.
    """
    try:
        cg_generator = pycg.CallGraphGenerator([repo_path], repo_path, -1, "json")
        cg_generator.analyze()
        cg = cg_generator.output()

        mermaid_diagram = "classDiagram\n"
        for module, data in cg.items():
            for cls, methods in data.get("classes", {}).items():
                mermaid_diagram += f"class {cls}\n"
                for method in methods:
                    mermaid_diagram += f"{cls} : +{method}()\n"

        return f"```mermaid\n{mermaid_diagram}\n```"
    except Exception as e:
        return f"Error generating diagram: {e}"

@function_tool
async def contributor_guide_tool(repo_path: str) -> str:
    """
    Generates a contributor guide.
    """
    # In a real implementation, we would analyze the repo and generate
    # a contributor guide. For now, we'll just return a placeholder.
    return \"\"\"
# Contributing

We welcome contributions! Please follow these guidelines:

1.  Fork the repository.
2.  Create a new branch.
3.  Make your changes.
4.  Submit a pull request.
\"\"\"
