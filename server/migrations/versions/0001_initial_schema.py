"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-05-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("category", sa.String(length=40), nullable=False),
        sa.Column("equipment_needed", sa.Boolean(), nullable=False),
        sa.CheckConstraint("length(trim(name)) >= 2", name="ck_exercise_name_min_length"),
        sa.CheckConstraint(
            "category IN ('balance', 'cardio', 'core', 'flexibility', 'mobility', 'strength')",
            name="ck_exercise_category_allowed",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "workouts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.CheckConstraint("duration_minutes > 0", name="ck_workout_duration_positive"),
        sa.CheckConstraint("duration_minutes <= 600", name="ck_workout_duration_max"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "workout_exercises",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workout_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("reps", sa.Integer(), nullable=True),
        sa.Column("sets", sa.Integer(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.CheckConstraint("reps IS NULL OR reps > 0", name="ck_workout_exercise_reps_positive"),
        sa.CheckConstraint("sets IS NULL OR sets > 0", name="ck_workout_exercise_sets_positive"),
        sa.CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="ck_workout_exercise_duration_positive",
        ),
        sa.CheckConstraint(
            "(reps IS NOT NULL AND sets IS NOT NULL) OR duration_seconds IS NOT NULL",
            name="ck_workout_exercise_has_metric",
        ),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workout_id"], ["workouts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("workout_id", "exercise_id", name="uq_workout_exercise_pair"),
    )


def downgrade():
    op.drop_table("workout_exercises")
    op.drop_table("workouts")
    op.drop_table("exercises")
