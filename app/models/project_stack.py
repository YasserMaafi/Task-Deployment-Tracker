from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.user import Base


class ProjectStack(Base):
    __tablename__ = "project_stacks"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False)

    language = Column(String, nullable=False)
    framework = Column(String, nullable=True)
    database = Column(String, nullable=True)
    test_framework = Column(String, nullable=True)

    containerized = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="stack")
