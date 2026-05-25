from marshmallow import Schema, ValidationError, fields, post_load, validates, validates_schema

from models import ALLOWED_CATEGORIES


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    equipment_needed = fields.Bool(required=True)

    @validates("name")
    def validate_name(self, value):
        normalized = " ".join(str(value).strip().split())
        if len(normalized) < 2 or len(normalized) > 80:
            raise ValidationError("Name must be between 2 and 80 characters.")

    @validates("category")
    def validate_category(self, value):
        if str(value).strip().lower() not in ALLOWED_CATEGORIES:
            allowed = ", ".join(sorted(ALLOWED_CATEGORIES))
            raise ValidationError(f"Category must be one of: {allowed}.")

    @post_load
    def normalize(self, data, **kwargs):
        data["name"] = " ".join(data["name"].strip().split())
        data["category"] = data["category"].strip().lower()
        return data


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True)
    notes = fields.Str(allow_none=True, load_default=None)

    @validates("duration_minutes")
    def validate_duration_minutes(self, value):
        if value < 1 or value > 600:
            raise ValidationError("Duration must be between 1 and 600 minutes.")

    @validates("notes")
    def validate_notes(self, value):
        if value is not None and len(str(value).strip()) > 500:
            raise ValidationError("Notes must not exceed 500 characters.")

    @post_load
    def normalize(self, data, **kwargs):
        if data.get("notes") is not None:
            data["notes"] = data["notes"].strip()
        return data


class WorkoutExerciseCreateSchema(Schema):
    sets = fields.Int(required=False, allow_none=True)
    reps = fields.Int(required=False, allow_none=True)
    duration_seconds = fields.Int(required=False, allow_none=True)

    @validates("sets")
    def validate_sets(self, value):
        if value is not None and value < 1:
            raise ValidationError("sets must be greater than 0.")

    @validates("reps")
    def validate_reps(self, value):
        if value is not None and value < 1:
            raise ValidationError("reps must be greater than 0.")

    @validates("duration_seconds")
    def validate_duration_seconds(self, value):
        if value is not None and value < 1:
            raise ValidationError("duration_seconds must be greater than 0.")

    @validates_schema
    def validate_metric_combination(self, data, **kwargs):
        has_sets = data.get("sets") is not None
        has_reps = data.get("reps") is not None
        has_duration = data.get("duration_seconds") is not None

        if has_sets != has_reps:
            raise ValidationError("sets and reps must be provided together.")
        if not ((has_sets and has_reps) or has_duration):
            raise ValidationError(
                "Provide either both sets and reps, duration_seconds, or all three metrics."
            )


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)
    exercise = fields.Nested(ExerciseSchema, dump_only=True)


class WorkoutExerciseWithWorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)
    workout = fields.Nested(WorkoutSchema, dump_only=True)


class WorkoutDetailSchema(WorkoutSchema):
    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True, dump_only=True)


class ExerciseDetailSchema(ExerciseSchema):
    workout_exercises = fields.Nested(
        WorkoutExerciseWithWorkoutSchema,
        many=True,
        dump_only=True,
    )
