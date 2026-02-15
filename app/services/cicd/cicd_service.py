from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.ai.cicd_generator import CICDGenerator
from app.models.ai_generation import AIGeneration
from app.models.project_stack import ProjectStack


class CICDService:

    def __init__(self, generator: CICDGenerator):
        self.generator = generator

    async def generate_pipeline(self, project, user, db_session: AsyncSession):
        # 1️⃣ Permission check
        if project.owner_id != user.id and user.role != "admin":
            raise PermissionError("Only project owner or admin can generate CI/CD pipelines.")

        # 2️⃣ Get project stack data
        # For now, we'll pass basic project info
        # Later this will fetch from ProjectStack model
        stack_data = {
            "project_name": project.name,
            "description": project.description
        }

        # 3️⃣ Create AI generation record (PENDING)
        ai_record = AIGeneration(
            project_id=project.id,
            user_id=user.id,
            generation_type="cicd",
            input_payload=stack_data,
            output_content=None,
            status="pending",
            model_used=None,
            error_message=None
        )
        db_session.add(ai_record)
        await db_session.commit()
        await db_session.refresh(ai_record)

        try:
            # 4️⃣ Call CICDGenerator
            # Currently returns stub YAML
            yaml_result = await self.generator.generate_github_actions_yaml(stack_data)

            # 5️⃣ Update record with output
            ai_record.output_content = yaml_result
            ai_record.status = "completed"
            ai_record.completed_at = datetime.utcnow()
            ai_record.model_used = "gemini-pro"

        except Exception as e:
            # 6️⃣ Handle failure
            ai_record.status = "failed"
            ai_record.error_message = str(e)
            ai_record.completed_at = datetime.utcnow()

        db_session.add(ai_record)
        await db_session.commit()
        await db_session.refresh(ai_record)

        return ai_record
