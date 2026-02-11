from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime
from app.models.user import Base
from app.models.project import Project

class DeploymentStatus(PyEnum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    deployed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    environment = Column(String(50), nullable=False)  # e.g., staging, production
    version = Column(String(50), nullable=False)      # e.g., v1.2.3
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING)
    deployed_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", backref="deployments")
    deployed_by = relationship("User", backref="deployments_done")

    def __repr__(self):
        return f"<Deployment(project_id={self.project_id}, env={self.environment}, status={self.status})>"
