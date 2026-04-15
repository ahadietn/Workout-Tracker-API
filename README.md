# Workout Tracker API

A REST API for managing workout sessions and exercises, built with Flask, SQLAlchemy, and Marshmallow.

## Tech Stack

- **Flask** 
- **Flask-SQLAlchemy** 
- **Flask-Migrate** 
- **Flask-Marshmallow** 

## Project Structure

```
workout-tracker-api/
├── server/
│   ├── app.py        # Flask app and routes
│   ├── models.py     # SQLAlchemy models
│   ├── schemas.py    # Marshmallow schemas
│   └── seed.py       # Database seed data
├── Pipfile
└── README.md
```

## Setup

```bash
pipenv install
pipenv shell
```

## Database Setup

```bash
flask --app server.app db upgrade
python -m server.seed
```

## Running the Server

```bash
flask --app server.app run --port 5555 --debug
```

## API Endpoints

### Exercises

 GET `/exercises` Get all exercises 
 GET /exercises/<id>` Get a single exercise
 POST `/exercises` Create a new exercise 
 DELETE `/exercises/<id>`Delete an exercise 

**POST `/exercises` body:**
```json
{
  "name": "Squat",
  "category": "strength",
  "equipment_needed": false
}
```

Valid categories: `strength`, `cardio`, `flexibility`, `balance`, `plyometrics`

### Workouts

 GET `/workouts` Get all workouts 
 GET  `/workouts/<id>` Get a single workout with exercises 
 POST `/workouts` Create a new workout 
 DELETE `/workouts/<id>` Delete a workout 

**POST `/workouts` body:**
```json
{
  "date": "2024-03-15",
  "duration_minutes": 45,
  "notes": "Leg day"
}
```

### Workout Exercises

 POST  `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises`

**POST body (all optional):**
```json
{
  "sets": 3,
  "reps": 10,
  "duration_seconds": 60
}
```

