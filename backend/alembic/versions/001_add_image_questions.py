"""add image_questions table

Revision ID: 001_add_image_questions
Revises:
Create Date: 2026-02-21
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_add_image_questions'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'image_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_image', sa.String(255), nullable=False, index=True),
        sa.Column('answer_image', sa.String(255), nullable=True),
        sa.Column('question_description', sa.Text(), nullable=True),
        sa.Column('subject', sa.String(50), nullable=False, index=True),
        sa.Column('chapter', sa.String(100), nullable=True),
        sa.Column('grade', sa.String(10), nullable=True, index=True),
        sa.Column('page', sa.String(20), nullable=True),
        sa.Column('question_image_ext', sa.String(10), server_default='jpg'),
        sa.Column('answer_image_ext', sa.String(10), server_default='jpg'),
        sa.Column('images_verified', sa.Boolean(), server_default='false'),
        sa.Column('import_batch_id', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_image_questions_id', 'image_questions', ['id'])


def downgrade() -> None:
    op.drop_index('ix_image_questions_id', table_name='image_questions')
    op.drop_table('image_questions')
