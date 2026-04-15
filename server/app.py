from flask import Flask, request, jsonify
from flask_migrate import Migrate
 
from server.models import db, Exercise, Workout, WorkoutExercise
from server.schemas import (
    ma,
    exercise_schema, exercises_schema,
    workout_schema, workouts_schema,
    workout_exercise_schema
)
 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app, db)
 
# Connect SQLAlchemy and Marshmallow to this Flask app
db.init_app(app)
ma.init_app(app)
 
 
@app.route('/workouts', methods=['GET'])
def get_workouts():
    """Return a list of all workouts in the system."""
    workouts = Workout.query.all()
    # many=True schema handles the list serialization for us
    return workouts_schema.jsonify(workouts), 200
 
 
@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    """
    Return a single workout by ID.
    The response includes the workout's exercises with their sets/reps/duration
    (this is the stretch goal handled automatically by the nested schema).
    """
    workout = Workout.query.get(id)
 
    # Return a clear 404 if the workout doesn't exist instead of crashing
    if not workout:
        return jsonify({'error': f'No workout found with id {id}'}), 404
 
    return workout_schema.jsonify(workout), 200
 
 
@app.route('/workouts', methods=['POST'])
def create_workout():
    """
    Create a new workout.
    Expects JSON body with: date, duration_minutes, and optionally notes.
    Example: { "date": "2024-03-15", "duration_minutes": 45, "notes": "Leg day" }
    """
    data = request.get_json()
 
    try:
        # schema.load() validates the incoming data before we do anything with it.
        # If validation fails, it raises a ValidationError which we catch.
        workout_data = workout_schema.load(data)
        new_workout = Workout(**workout_data)
        db.session.add(new_workout)
        db.session.commit()
        return workout_schema.jsonify(new_workout), 201
 
    except Exception as e:
        # Roll back any changes if something went wrong mid-transaction
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
 
 
@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    """
    Delete a workout by ID.
    Thanks to cascade='all, delete-orphan' on the relationship,
    all associated WorkoutExercise rows are deleted automatically.
    """
    workout = Workout.query.get(id)
 
    if not workout:
        return jsonify({'error': f'No workout found with id {id}'}), 404
 
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message': f'Workout {id} deleted successfully.'}), 200
 
 
# EXERCISE ROUTES
 
@app.route('/exercises', methods=['GET'])
def get_exercises():
    """Return a list of all exercises."""
    exercises = Exercise.query.all()
    return exercises_schema.jsonify(exercises), 200
 
 
@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    """
    Return a single exercise by ID.
    The response includes all workouts this exercise has appeared in.
    """
    exercise = Exercise.query.get(id)
 
    if not exercise:
        return jsonify({'error': f'No exercise found with id {id}'}), 404
 
    return exercise_schema.jsonify(exercise), 200
 
 
@app.route('/exercises', methods=['POST'])
def create_exercise():
    """
    Create a new exercise.
    Expects JSON body with: name, category, and optionally equipment_needed.
    Example: { "name": "Squat", "category": "strength", "equipment_needed": false }
    """
    data = request.get_json()
 
    try:
        exercise_data = exercise_schema.load(data)
        new_exercise = Exercise(**exercise_data)
        db.session.add(new_exercise)
        db.session.commit()
        return exercise_schema.jsonify(new_exercise), 201
 
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
 
 
@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    """
    Delete an exercise by ID.
    Cascade handles cleaning up any WorkoutExercise rows that reference this exercise.
    """
    exercise = Exercise.query.get(id)
 
    if not exercise:
        return jsonify({'error': f'No exercise found with id {id}'}), 404
 
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({'message': f'Exercise {id} deleted successfully.'}), 200
 
 
# WORKOUT EXERCISE ROUTE
 
@app.route(
    '/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
    methods=['POST']
)
def add_exercise_to_workout(workout_id, exercise_id):
    """
    Add an exercise to a workout.
    The workout and exercise must both exist before we can link them.
 
    Expects JSON body with any of: reps, sets, duration_seconds.
    These are all optional depends on the exercise type.
    """
    # Make sure both the workout and exercise actually exist before proceeding
    workout = Workout.query.get(workout_id)
    exercise = Exercise.query.get(exercise_id)
 
    if not workout:
        return jsonify({'error': f'No workout found with id {workout_id}'}), 404
    if not exercise:
        return jsonify({'error': f'No exercise found with id {exercise_id}'}), 404
 
    # Grab the body (could be empty if no reps/sets/duration provided)
    data = request.get_json() or {}
 
    # Inject the IDs from the URL into the data dict so the schema can validate everything together
    data['workout_id'] = workout_id
    data['exercise_id'] = exercise_id
 
    try:
        we_data = workout_exercise_schema.load(data)
        new_we = WorkoutExercise(**we_data)
        db.session.add(new_we)
        db.session.commit()
        return workout_exercise_schema.jsonify(new_we), 201
 
    except Exception as e:
        # This will catch the UniqueConstraint violation if the exercise is already in the workout
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
 
 
# Only runs when you do `python app.py` directly, not when using `flask run`
if __name__ == '__main__':
    app.run(port=5555, debug=True)
 