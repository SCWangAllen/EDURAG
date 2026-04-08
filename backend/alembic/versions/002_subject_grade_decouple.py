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

    # 使用原生 SQL 的 IF EXISTS 語法，避免 PostgreSQL transaction abort 問題

    # 0. Drop check constraint on grade if it exists
    conn.execute(sa.text("""
        ALTER TABLE subjects DROP CONSTRAINT IF EXISTS check_subjects_grade
    """))

    # 0.1 Fix NULL grades to empty string to avoid unique constraint issues
    conn.execute(sa.text("""
        UPDATE subjects SET grade = '' WHERE grade IS NULL
    """))

    # 1. Drop unique constraints on subjects.name (if exists)
    conn.execute(sa.text("""
        ALTER TABLE subjects DROP CONSTRAINT IF EXISTS subjects_name_key
    """))
    conn.execute(sa.text("""
        ALTER TABLE subjects DROP CONSTRAINT IF EXISTS subjects_name_unique
    """))

    # Drop index if exists
    conn.execute(sa.text("""
        DROP INDEX IF EXISTS ix_subjects_name
    """))

    # 2. Alter subjects.grade column to varchar(20) and set default to empty string
    conn.execute(sa.text("""
        ALTER TABLE subjects
        ALTER COLUMN grade TYPE VARCHAR(20),
        ALTER COLUMN grade SET DEFAULT ''
    """))

    # 3. Create non-unique index on subjects.name
    conn.execute(sa.text("""
        CREATE INDEX IF NOT EXISTS ix_subjects_name ON subjects(name)
    """))

    # 4. Add unique constraint on (name, grade) combination
    conn.execute(sa.text("""
        ALTER TABLE subjects
        ADD CONSTRAINT uq_subject_name_grade UNIQUE (name, grade)
    """))

    # 5. Add grades column to templates table if not exists
    conn.execute(sa.text("""
        ALTER TABLE templates
        ADD COLUMN IF NOT EXISTS grades JSON DEFAULT '[]'
    """))


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
