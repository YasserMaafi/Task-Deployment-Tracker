from .base import AIProvider


class CICDGenerator:

    def __init__(self, provider: AIProvider):
        self.provider = provider

    async def generate_github_actions_yaml(self, stack_data: dict) -> str:
        prompt = self._build_prompt(stack_data)
        response = await self.provider.generate(prompt)
        return response

    def _build_prompt(self, stack_data: dict) -> str:
        project_name = stack_data.get("project_name", "project")
        description = stack_data.get("description", "")
        
        return f"""You are a DevOps automation engine.

Generate a production-ready GitHub Actions CI/CD pipeline.

Requirements:
- Output ONLY valid YAML.
- No markdown.
- No explanations.
- No backticks.
- Must be deployable.

Project details:
- Name: {project_name}
- Description: {description}

Generate the complete .github/workflows/ci-cd.yml file content."""
