#!/usr/bin/env python3
from datetime import date

from app import app
from models import Exercise, Workout, WorkoutExercise, db


with app.app_context():
    print("Clearing existing data...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    print("Creating exercises...")
    push_up = Exercise(name="Push Up", category="strength", equipment_needed=False)
    squat = Exercise(name="Goblet Squat", category="strength", equipment_needed=True)
    plank = Exercise(name="Plank", category="core", equipment_needed=False)
    jump_rope = Exercise(name="Jump Rope", category="cardio", equipment_needed=True)
    hip_mobility = Exercise(name="Hip Mobility Flow", category="mobility", equipment_needed=False)

    db.session.add_all([push_up, squat, plank, jump_rope, hip_mobility])
    db.session.flush()

    print("Creating workouts...")
    upper_body = Workout(
        date=date(2026, 5, 20),
        duration_minutes=45,
        notes="Upper-body strength and core session.",
    )
    conditioning = Workout(
        date=date(2026, 5, 22),
        duration_minutes=35,
        notes="Cardio conditioning with short rest periods.",
    )
    mobility = Workout(
        date=date(2026, 5, 24),
        duration_minutes=25,
        notes="Recovery-focused mobility work.",
    )

    db.session.add_all([upper_body, conditioning, mobility])
    db.session.flush()

    print("Attaching exercises to workouts...")
    workout_exercises = [
        WorkoutExercise(workout_id=upper_body.id, exercise_id=push_up.id, sets=3, reps=12),
        WorkoutExercise(workout_id=upper_body.id, exercise_id=plank.id, duration_seconds=180),
        WorkoutExercise(workout_id=conditioning.id, exercise_id=jump_rope.id, duration_seconds=300),
        WorkoutExercise(workout_id=conditioning.id, exercise_id=squat.id, sets=4, reps=10),
        WorkoutExercise(workout_id=mobility.id, exercise_id=hip_mobility.id, duration_seconds=900),
    ]

    for workout_exercise in workout_exercises:
        workout_exercise.validate_metric_combination()

    db.session.add_all(workout_exercises)
    db.session.commit()

    print("Database seeded successfully.")
