# Workout Tracker API

A Flask, SQLAlchemy, and Marshmallow backend API for a workout tracking application used by personal trainers. The API manages reusable exercises, workouts, and the join records that attach exercise performance details such as sets, reps, and duration to each workout.

## Project Scope

This backend implements the lab requirements for:

- Creating, viewing, and deleting workouts.
- Creating, viewing, and deleting exercises.
- Adding an exercise to a workout through a join table.
- One-to-many and many-to-many relationships through `WorkoutExercise`.
- Table-level constraints, SQLAlchemy model validations, and Marshmallow schema validations.
- Seed data for all models.
- REST-style JSON endpoints.
- Cascade deletion of related join-table records when workouts or exercises are deleted.

## Tech Stack

- Python 3.8.13+
- Flask 2.2.2
- Flask-SQLAlchemy 3.0.3
- Flask-Migrate 3.1.0
- Marshmallow 3.20.1
- SQLite by default
- Pipenv

## Repository Structure

```text
workout-tracker-api/
├── Pipfile
├── README.md
├── .gitignore
├── server/
│   ├── app.py
│   ├── models.py
│   ├── schemas.py
│   ├── seed.py
│   └── migrations/
│       ├── env.py
│       ├── README
│       ├── script.py.mako
│       └── versions/
│           └── 0001_initial_schema.py
└── tests/
    └── test_api.py
```

## Installation

From the project root:

```bash
pipenv install
pipenv shell
```

## Database Setup

The application defaults to SQLite at `server/instance/app.db` when run through Flask.

From the project root:

```bash
cd server
export FLASK_APP=app.py
flask db upgrade head
python seed.py
```

For Windows PowerShell:

```powershell
cd server
$env:FLASK_APP = "app.py"
flask db upgrade head
python seed.py
```

## Run the API

From the `server/` directory:

```bash
flask run --port 5555
```

The API will be available at:

```text
http://127.0.0.1:5555
```

## Optional Database Environment Variable

You can override the default SQLite database with:

```bash
export DATABASE_URI="sqlite:///app.db"
```

## Endpoints

### Health Check

#### `GET /`

Returns API metadata and available core resources.

#### `GET /health`

Returns a simple status response.

### Workouts

#### `GET /workouts`

Returns all workouts in descending date order.

Example response:

```json
[
  {
    "id": 1,
    "date": "2026-05-20",
    "duration_minutes": 45,
    "notes": "Upper-body strength session"
  }
]
```

#### `GET /workouts/<id>`

Returns one workout with its associated exercises, including join-table performance details.

#### `POST /workouts`

Creates a workout.

Required body:

```json
{
  "date": "2026-05-20",
  "duration_minutes": 45,
  "notes": "Upper-body strength session"
}
```

Validation rules include:

- `date` must be a valid `YYYY-MM-DD` date.
- `duration_minutes` must be between 1 and 600.
- `notes`, when supplied, must not exceed 500 characters.

#### `DELETE /workouts/<id>`

Deletes a workout and all associated `WorkoutExercise` join records.

### Exercises

#### `GET /exercises`

Returns all exercises alphabetically by name.

#### `GET /exercises/<id>`

Returns one exercise with associated workouts and join-table performance details.

#### `POST /exercises`

Creates an exercise.

Required body:

```json
{
  "name": "Push Up",
  "category": "strength",
  "equipment_needed": false
}
```

Allowed categories:

- `balance`
- `cardio`
- `core`
- `flexibility`
- `mobility`
- `strength`

Validation rules include:

- `name` must be unique and between 2 and 80 characters.
- `category` must be one of the allowed values.
- `equipment_needed` must be a boolean.

#### `DELETE /exercises/<id>`

Deletes an exercise and all associated `WorkoutExercise` join records.

### Workout Exercises

#### `POST /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises`

Adds an exercise to a workout with performance details.

Example body for sets and reps:

```json
{
  "sets": 3,
  "reps": 12
}
```

Example body for timed exercise:

```json
{
  "duration_seconds": 300
}
```

Validation rules include:

- The workout and exercise must exist.
- The same exercise cannot be added twice to the same workout.
- At least one performance metric must be supplied: `sets` plus `reps`, or `duration_seconds`.
- `sets`, `reps`, and `duration_seconds`, when supplied, must be positive integers.

## Validations Implemented

### Table Constraints

Examples include:

- Unique exercise names.
- Allowed exercise categories through a check constraint.
- Positive workout duration through a check constraint.
- Unique `(workout_id, exercise_id)` pairs in the join table.
- Positive join-table performance metrics through check constraints.

### Model Validations

Examples include:

- Exercise name normalization and length validation.
- Exercise category validation.
- Workout duration validation.
- Workout date validation.
- Join-table metric validation.

### Schema Validations

Examples include:

- Request payload validation through Marshmallow schemas.
- Required field checks.
- Type checks.
- Allowed category validation.
- Join payload validation requiring sets/reps and/or duration.

## Seed the Database

From the `server/` directory:

```bash
python seed.py
```

The seed script clears existing rows and creates sample exercises, workouts, and workout-exercise records.

## Run Tests

From the project root:

```bash
python -m unittest discover -s tests
```

The tests use an in-memory SQLite database and verify core endpoint behavior, schema/model validation, join-table creation, and cascade deletion.

## Example Manual Testing with curl

Create an exercise:

```bash
curl -X POST http://127.0.0.1:5555/exercises \
  -H "Content-Type: application/json" \
  -d '{"name":"Burpee","category":"cardio","equipment_needed":false}'
```

Create a workout:

```bash
curl -X POST http://127.0.0.1:5555/workouts \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-05-20","duration_minutes":30,"notes":"Conditioning session"}'
```

Add an exercise to a workout:

```bash
curl -X POST http://127.0.0.1:5555/workouts/1/exercises/1/workout_exercises \
  -H "Content-Type: application/json" \
  -d '{"sets":3,"reps":15}'
```
