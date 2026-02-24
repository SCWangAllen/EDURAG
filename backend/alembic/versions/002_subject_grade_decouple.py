"""Subject grade decoupling and template grades field

Revision ID: 002_subject_grade_decouple
Revises: 001_add_image_questions
Create Date: 2026-02-24

Changes:
1. Remove unique constraint on subjects.name
2. Add unique constraint on (name, grade) combination
3. Extend subjects.grade column to varchar(20)
4. Add grades JSON column to templates table
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_subject_grade_decouple'
down_revision: Union[str, None] = '001_add_image_questions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # 0. Drop check constraint on grade if it exists (it restricts grade values)
    try:
        op.drop_constraint('check_subjects_grade', 'subjects', type_='check')
    except Exception:
        pass

    # 0.1 Fix NULL grades to empty string to avoid unique constraint issues with NULL
    # PostgreSQL treats NULL values as distinct in unique constraints
    conn.execute(sa.text("""
        UPDATE subjects SET grade = '' WHERE grade IS NULL
    """))

    # 1. Drop the unique constraint on subjects.name (if exists)
    # Try multiple common constraint naming patterns
    for constraint_name in ['subjects_name_key', 'subjects_name_unique', 'ix_subjects_name']:
        try:
            op.drop_constraint(constraint_name, 'subjects', type_='unique')
        except Exception:
            pass

    try:
        op.drop_index('ix_subjects_name', table_name='subjects')
    except Exception:
        pass

    # 2. Alter subjects.grade column to varchar(20) and set default to empty string
    op.alter_column(
        'subjects',
        'grade',
        existing_type=sa.String(10),
        type_=sa.String(20),
        existing_nullable=True,
        server_default=''
    )

    # 3. Create index on subjects.name (non-unique)
    try:
        op.create_index('ix_subjects_name', 'subjects', ['name'])
    except Exception:
        pass  # Index might already exist

    # 4. Add unique constraint on (name, grade) combination
    op.create_unique_constraint(
        'uq_subject_name_grade',
        'subjects',
        ['name', 'grade']
    )

    # 5. Add grades column to templates table
    op.add_column(
        'templates',
        sa.Column('grades', sa.JSON(), nullable=True, server_default='[]')
    )


def downgrade() -> None:
    # 1. Drop grades column from templates
    op.drop_column('templates', 'grades')

    # 2. Drop unique constraint on (name, grade)
    op.drop_constraint('uq_subject_name_grade', 'subjects', type_='unique')

    # 3. Drop non-unique index on name
    op.drop_index('ix_subjects_name', table_name='subjects')

    # 4. Revert subjects.grade column to varchar(10)
    op.alter_column(
        'subjects',
        'grade',
        existing_type=sa.String(20),
        type_=sa.String(10),
        existing_nullable=True
    )

    # 5. Recreate unique constraint on subjects.name
    op.create_unique_constraint('subjects_name_key', 'subjects', ['name'])

    # 6. Recreate unique index on name
    op.create_index('ix_subjects_name', 'subjects', ['name'], unique=True)
