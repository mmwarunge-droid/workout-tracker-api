from datetime import date, datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates


db = SQLAlchemy()


ALLOWED_CATEGORIES = {
    "balance",
    "cardio",
    "core",
    "flexibility",
    "mobility",
    "strength",
}


class Exercise(db.Model):
    """Reusable exercise that can appear in many workouts."""

    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    category = db.Column(db.String(40), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )
    workouts = db.relationship(
        "Workout",
        secondary="workout_exercises",
        back_populates="exercises",
        viewonly=True,
    )

    __table_args__ = (
        CheckConstraint("length(trim(name)) >= 2", name="ck_exercise_name_min_length"),
        CheckConstraint(
            "category IN ('balance', 'cardio', 'core', 'flexibility', 'mobility', 'strength')",
            name="ck_exercise_category_allowed",
        ),
    )

    @validates("name")
    def validate_name(self, key, value):
        if value is None:
            raise ValueError("Exercise name is required.")

        normalized = " ".join(str(value).strip().split())
        if len(normalized) < 2 or len(normalized) > 80:
            raise ValueError("Exercise name must be between 2 and 80 characters.")
        return normalized

    @validates("category")
    def validate_category(self, key, value):
        if value is None:
            raise ValueError("Exercise category is required.")

        normalized = str(value).strip().lower()
        if normalized not in ALLOWED_CATEGORIES:
            allowed = ", ".join(sorted(ALLOWED_CATEGORIES))
            raise ValueError(f"Exercise category must be one of: {allowed}.")
        return normalized

    @validates("equipment_needed")
    def validate_equipment_needed(self, key, value):
        if not isinstance(value, bool):
            raise ValueError("equipment_needed must be a boolean.")
        return value

    def __repr__(self):
        return f"<Exercise id={self.id} name={self.name!r}>"


class Workout(db.Model):
    """Workout session that can include many exercises."""

    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )
    exercises = db.relationship(
        "Exercise",
        secondary="workout_exercises",
        back_populates="workouts",
        viewonly=True,
    )

    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="ck_workout_duration_positive"),
        CheckConstraint("duration_minutes <= 600", name="ck_workout_duration_max"),
    )

    @validates("date")
    def validate_date(self, key, value):
        if value is None:
            raise ValueError("Workout date is required.")

        if isinstance(value, datetime):
            value = value.date()
        elif isinstance(value, str):
            try:
                value = date.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("Workout date must use YYYY-MM-DD format.") from exc
        elif not isinstance(value, date):
            raise ValueError("Workout date must be a date.")

        return value

    @validates("duration_minutes")
    def validate_duration_minutes(self, key, value):
        if value is None:
            raise ValueError("Workout duration is required.")

        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("Workout duration must be an integer.")
        if value < 1 or value > 600:
            raise ValueError("Workout duration must be between 1 and 600 minutes.")
        return value

    @validates("notes")
    def validate_notes(self, key, value):
        if value is None:
            return value

        normalized = str(value).strip()
        if len(normalized) > 500:
            raise ValueError("Workout notes must not exceed 500 characters.")
        return normalized

    def __repr__(self):
        return f"<Workout id={self.id} date={self.date}>"


class WorkoutExercise(db.Model):
    """Join model that stores exercise performance details for a workout."""

    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(
        db.Integer,
        db.ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
    )
    reps = db.Column(db.Integer, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    __table_args__ = (
        UniqueConstraint("workout_id", "exercise_id", name="uq_workout_exercise_pair"),
        CheckConstraint("reps IS NULL OR reps > 0", name="ck_workout_exercise_reps_positive"),
        CheckConstraint("sets IS NULL OR sets > 0", name="ck_workout_exercise_sets_positive"),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="ck_workout_exercise_duration_positive",
        ),
        CheckConstraint(
            "(reps IS NOT NULL AND sets IS NOT NULL) OR duration_seconds IS NOT NULL",
            name="ck_workout_exercise_has_metric",
        ),
    )

    @validates("reps", "sets", "duration_seconds")
    def validate_positive_metric(self, key, value):
        if value is None:
            return value
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{key} must be an integer.")
        if value < 1:
            raise ValueError(f"{key} must be greater than 0.")
        return value

    @validates("workout_id", "exercise_id")
    def validate_foreign_key_id(self, key, value):
        if value is None:
            raise ValueError(f"{key} is required.")
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{key} must be a positive integer.")
        return value

    def validate_metric_combination(self):
        has_reps_and_sets = self.reps is not None and self.sets is not None
        has_duration = self.duration_seconds is not None

        if not has_reps_and_sets and not has_duration:
            raise ValueError(
                "Provide either both sets and reps, duration_seconds, or all three metrics."
            )
        if (self.reps is None) != (self.sets is None):
            raise ValueError("sets and reps must be provided together.")

    def __repr__(self):
        return (
            f"<WorkoutExercise id={self.id} workout_id={self.workout_id} "
            f"exercise_id={self.exercise_id}>"
        )
