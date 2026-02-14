from .base import AIProvider


class CICDGenerator:

    def __init__(self, provider: AIProvider):
        self.provider = provider

    async def generate_github_actions_yaml(self, stack_data: dict) -> str:
        prompt = self._build_prompt(stack_data)
        # For now, return stub YAML until provider is implemented
        # Later: response = await self.provider.generate(prompt)
        return self._generate_stub_yaml(stack_data)

    def _build_prompt(self, stack_data: dict) -> str:
        return f"Generate a production-ready GitHub Actions CI/CD pipeline for: {stack_data}"

    def _generate_stub_yaml(self, stack_data: dict) -> str:
        """Temporary stub until AI provider is implemented"""
        project_name = stack_data.get("project_name", "project")
        return f"""name: CI/CD Pipeline for {project_name}

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: echo "Tests would run here"
      - name: Build
        run: echo "Build would run here"
"""
