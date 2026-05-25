# Project Plan - Workout Tracker API

## Objective

Build a production-quality Flask backend API for a personal-trainer workout tracking application. The API tracks workouts, reusable exercises, and workout-specific exercise performance metrics.

## Core Functional Requirements

1. Manage workouts.
   - List all workouts.
   - View one workout with its attached exercises.
   - Create a workout.
   - Delete a workout and its join records.

2. Manage exercises.
   - List all exercises.
   - View one exercise with its attached workouts.
   - Create an exercise.
   - Delete an exercise and its join records.

3. Attach exercises to workouts.
   - Add an exercise to a workout through the `WorkoutExercise` join model.
   - Store `sets`, `reps`, and/or `duration_seconds` on the join record.

## Data Model

### Exercise

Reusable exercise catalog record.

Fields:

- `id`
- `name`
- `category`
- `equipment_needed`

Relationships:

- Has many `WorkoutExercise` records.
- Has many `Workout` records through `WorkoutExercise`.

### Workout

A workout session.

Fields:

- `id`
- `date`
- `duration_minutes`
- `notes`

Relationships:

- Has many `WorkoutExercise` records.
- Has many `Exercise` records through `WorkoutExercise`.

### WorkoutExercise

Join model with workout-specific exercise metrics.

Fields:

- `id`
- `workout_id`
- `exercise_id`
- `reps`
- `sets`
- `duration_seconds`

Relationships:

- Belongs to a `Workout`.
- Belongs to an `Exercise`.

## Validation Strategy

### Database/Table Constraints

- Exercise names are unique.
- Exercise names must be at least two non-space characters.
- Exercise categories are restricted to approved category values.
- Workout durations must be positive and capped at 600 minutes.
- Join records must contain at least sets/reps or duration.
- A workout cannot contain the same exercise twice.

### SQLAlchemy Model Validations

- Normalize exercise names.
- Validate category membership.
- Validate boolean equipment flags.
- Validate workout date and duration.
- Validate positive join-table performance metrics.

### Marshmallow Schema Validations

- Validate request payload shape and required fields.
- Validate date, integer, string, and boolean field types.
- Validate allowed categories.
- Validate join payload metric combinations.

## API Design

The API follows resource-oriented REST conventions:

- `/workouts` for workout collection operations.
- `/workouts/<id>` for individual workout operations.
- `/exercises` for exercise collection operations.
- `/exercises/<id>` for individual exercise operations.
- `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` for creating the join record.

## Testing Strategy

Unit tests verify:

- Listing exercises.
- Creating workouts.
- Rejecting invalid exercise categories.
- Adding an exercise to a workout.
- Rejecting duplicate workout-exercise pairs.
- Cascading deletion of join records when a workout is deleted.

## Delivery Artifacts

- Flask application source code.
- SQLAlchemy models and relationships.
- Marshmallow schemas.
- Alembic migration files.
- Seed data.
- README with installation, run, endpoint, and testing instructions.
- Unit tests.
- Git repository with initial implementation commit.
