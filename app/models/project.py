from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.models.user import Base
from app.models.project_students import project_students
from app.models.project_supervisors import project_supervisors

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Keep for backward compatibility
    is_public = Column(Boolean, default=True)

    owner = relationship("User", backref="projects")
    stack = relationship("ProjectStack", back_populates="project", uselist=False)
    feedback = relationship("ProjectFeedback", back_populates="project")
    
    # Many-to-many relationships
    students = relationship("User", secondary=project_students, backref="student_projects")
    supervisors = relationship("User", secondary=project_supervisors, backref="supervised_projects")

    def __repr__(self):
        return f"<Project(name={self.name}, owner_id={self.owner_id})>"
