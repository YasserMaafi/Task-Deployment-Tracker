"""add assignment workflow and activity logging

Revision ID: 5b317012f6a7
Revises: 3afb3ae90564
Create Date: 2026-02-12 15:37:16.485308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b317012f6a7'
down_revision: Union[str, Sequence[str], None] = '3afb3ae90564'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum type first
    assignmentstatus = sa.Enum('PENDING', 'ACCEPTED', 'REJECTED', name='assignmentstatus')
    assignmentstatus.create(op.get_bind(), checkfirst=True)
    
    # Add columns
    op.add_column('tasks', sa.Column('assignment_status', assignmentstatus, nullable=True))
    op.add_column('tasks', sa.Column('working_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'tasks', 'users', ['working_user_id'], ['id'])
    
    # Create task_activities table
    op.create_table('task_activities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=50), nullable=False),
    sa.Column('details', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('task_activities')
    op.drop_constraint(None, 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'working_user_id')
    op.drop_column('tasks', 'assignment_status')
    sa.Enum(name='assignmentstatus').drop(op.get_bind(), checkfirst=True)
