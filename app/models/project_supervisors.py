from sqlalchemy import Column, Integer, ForeignKey, DateTime, Table
from sqlalchemy.sql import func
from app.models.user import Base

# Association table for many-to-many relationship between projects and supervisors
project_supervisors = Table(
    'project_supervisors',
    Base.metadata,
    Column('id', Integer, primary_key=True, index=True),
    Column('project_id', Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
    Column('supervisor_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('assigned_at', DateTime(timezone=True), server_default=func.now())
)
