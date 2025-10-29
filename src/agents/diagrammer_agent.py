# src/agents/diagrammer_agent.py

from agents import FunctionTool
from pycg import pycg
import json

class DiagrammerTool(FunctionTool):
    def __init__(self, repo_path):
        self.repo_path = repo_path

    async def __call__(self) -> str:
        """
        Generates a class diagram from the source code.
        """
        try:
            cg_generator = pycg.CallGraphGenerator([self.repo_path], self.repo_path, -1, "json")
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
