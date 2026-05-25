import os
import sys
import unittest
from datetime import date

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SERVER_DIR = os.path.join(ROOT_DIR, "server")
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

from app import app
from models import Exercise, Workout, WorkoutExercise, db


class WorkoutTrackerApiTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

        self.app_context = app.app_context()
        self.app_context.push()

        db.drop_all()
        db.create_all()

        self.exercise = Exercise(
            name="Push Up",
            category="strength",
            equipment_needed=False,
        )
        self.workout = Workout(
            date=date(2026, 5, 20),
            duration_minutes=45,
            notes="Test workout",
        )
        db.session.add_all([self.exercise, self.workout])
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_exercises_returns_seeded_exercise(self):
        response = self.client.get("/exercises")

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["name"], "Push Up")

    def test_create_workout(self):
        response = self.client.post(
            "/workouts",
            json={
                "date": "2026-05-21",
                "duration_minutes": 30,
                "notes": "Conditioning session",
            },
        )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(payload["duration_minutes"], 30)

    def test_invalid_exercise_category_is_rejected(self):
        response = self.client.post(
            "/exercises",
            json={
                "name": "Invalid Category Exercise",
                "category": "speed",
                "equipment_needed": False,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Validation failed", response.get_json()["error"])

    def test_add_exercise_to_workout(self):
        response = self.client.post(
            f"/workouts/{self.workout.id}/exercises/{self.exercise.id}/workout_exercises",
            json={"sets": 3, "reps": 12},
        )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(payload["sets"], 3)
        self.assertEqual(payload["reps"], 12)

    def test_duplicate_workout_exercise_is_rejected(self):
        first = WorkoutExercise(
            workout_id=self.workout.id,
            exercise_id=self.exercise.id,
            sets=3,
            reps=12,
        )
        db.session.add(first)
        db.session.commit()

        response = self.client.post(
            f"/workouts/{self.workout.id}/exercises/{self.exercise.id}/workout_exercises",
            json={"sets": 2, "reps": 10},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("already", response.get_json()["error"].lower())

    def test_delete_workout_cascades_join_records(self):
        workout_exercise = WorkoutExercise(
            workout_id=self.workout.id,
            exercise_id=self.exercise.id,
            sets=3,
            reps=12,
        )
        db.session.add(workout_exercise)
        db.session.commit()

        response = self.client.delete(f"/workouts/{self.workout.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(WorkoutExercise.query.count(), 0)


if __name__ == "__main__":
    unittest.main()
