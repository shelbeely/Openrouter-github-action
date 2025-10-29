# src/tools/spec_harvesters.py
import os
import yaml
import json

class SpecHarvester:
    def run(self, repo_path):
        raise NotImplementedError

class OpenAPISpecHarvester(SpecHarvester):
    def run(self, repo_path):
        """
        Finds and parses OpenAPI specs in the repository.
        """
        specs = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file in ["openapi.json", "openapi.yaml", "swagger.json", "swagger.yaml"]:
                    filepath = os.path.join(root, file)
                    with open(filepath, 'r') as f:
                        if file.endswith(".json"):
                            spec = json.load(f)
                        else:
                            spec = yaml.safe_load(f)
                        specs.append(spec)
        return specs
