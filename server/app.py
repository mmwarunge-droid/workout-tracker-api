import os

from flask import Flask, jsonify, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import Exercise, Workout, WorkoutExercise, db
from schemas import (
    ExerciseDetailSchema,
    ExerciseSchema,
    WorkoutDetailSchema,
    WorkoutExerciseCreateSchema,
    WorkoutExerciseSchema,
    WorkoutSchema,
)


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URI",
    "sqlite:///app.db",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_detail_schema = ExerciseDetailSchema()

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_detail_schema = WorkoutDetailSchema()

workout_exercise_create_schema = WorkoutExerciseCreateSchema()
workout_exercise_schema = WorkoutExerciseSchema()


@app.errorhandler(ValidationError)
def handle_marshmallow_error(error):
    return jsonify({"error": "Validation failed", "messages": error.messages}), 400


@app.errorhandler(ValueError)
def handle_value_error(error):
    return jsonify({"error": str(error)}), 400


@app.errorhandler(IntegrityError)
def handle_integrity_error(error):
    db.session.rollback()
    message = str(error.orig).lower() if getattr(error, "orig", None) else str(error).lower()

    if "unique" in message and "workout" in message and "exercise" in message:
        detail = "This exercise has already been added to this workout."
    elif "unique" in message and "exercises.name" in message:
        detail = "An exercise with this name already exists."
    elif "check constraint" in message:
        detail = "Database constraint failed. Check the submitted values."
    else:
        detail = "Database integrity error. Check the submitted values."

    return jsonify({"error": detail}), 400


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"error": "Resource not found."}), 404


def get_json_payload():
    data = request.get_json(silent=True)
    if data is None:
        raise ValidationError({"json": ["A valid JSON request body is required."]})
    return data


@app.get("/")
def index():
    return jsonify(
        {
            "message": "Workout Tracker API",
            "resources": ["/workouts", "/exercises", "/health"],
        }
    ), 200


@app.get("/health")
def health_check():
    return jsonify({"status": "ok"}), 200


@app.get("/workouts")
def get_workouts():
    workouts = Workout.query.order_by(Workout.date.desc(), Workout.id.desc()).all()
    return jsonify(workouts_schema.dump(workouts)), 200


@app.get("/workouts/<int:workout_id>")
def get_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id)
    return jsonify(workout_detail_schema.dump(workout)), 200


@app.post("/workouts")
def create_workout():
    data = workout_schema.load(get_json_payload())
    workout = Workout(**data)

    db.session.add(workout)
    db.session.commit()

    return jsonify(workout_schema.dump(workout)), 201


@app.delete("/workouts/<int:workout_id>")
def delete_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id)

    db.session.delete(workout)
    db.session.commit()

    return jsonify({"message": "Workout deleted successfully."}), 200


@app.get("/exercises")
def get_exercises():
    exercises = Exercise.query.order_by(Exercise.name.asc()).all()
    return jsonify(exercises_schema.dump(exercises)), 200


@app.get("/exercises/<int:exercise_id>")
def get_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id)
    return jsonify(exercise_detail_schema.dump(exercise)), 200


@app.post("/exercises")
def create_exercise():
    data = exercise_schema.load(get_json_payload())
    exercise = Exercise(**data)

    db.session.add(exercise)
    db.session.commit()

    return jsonify(exercise_schema.dump(exercise)), 201


@app.delete("/exercises/<int:exercise_id>")
def delete_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id)

    db.session.delete(exercise)
    db.session.commit()

    return jsonify({"message": "Exercise deleted successfully."}), 200


@app.post("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises")
def add_exercise_to_workout(workout_id, exercise_id):
    db.get_or_404(Workout, workout_id)
    db.get_or_404(Exercise, exercise_id)

    data = workout_exercise_create_schema.load(get_json_payload())
    workout_exercise = WorkoutExercise(
        workout_id=workout_id,
        exercise_id=exercise_id,
        **data,
    )
    workout_exercise.validate_metric_combination()

    db.session.add(workout_exercise)
    db.session.commit()

    return jsonify(workout_exercise_schema.dump(workout_exercise)), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
