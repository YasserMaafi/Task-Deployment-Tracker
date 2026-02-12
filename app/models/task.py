from sqlalchemy import Column, Integer, String, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime
from app.models.user import Base
from app.models.project import Project

class TaskStatus(PyEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class AssignmentStatus(PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    assignment_status = Column(Enum(AssignmentStatus), nullable=True)
    working_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    project = relationship("Project", backref="tasks")
    creator = relationship("User", foreign_keys=[creator_id], backref="tasks_created")
    assignee = relationship("User", foreign_keys=[assignee_id], backref="tasks_assigned")
    working_user = relationship("User", foreign_keys=[working_user_id], backref="tasks_working_on")

    def __repr__(self):
        return f"<Task(title={self.title}, status={self.status})>"
