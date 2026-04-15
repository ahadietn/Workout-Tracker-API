from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from datetime import date
 
db = SQLAlchemy()
 
class Exercise(db.Model):
    __tablename__ = 'exercises'
 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
 
    # Category helps trainers filter exercises by type 
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)
 
    # One exercise can appear in many workout_exercises (the join table).
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='exercise',
        cascade='all, delete-orphan'
    )
 
    # Shortcut relationship — jump straight from Exercise to Workouts without manually going through the join table every time.
    workouts = db.relationship(
        'Workout',
        secondary='workout_exercises',
        back_populates='exercises'
    )
    VALID_CATEGORIES = ['strength', 'cardio', 'flexibility', 'balance', 'plyometrics']
 
    @validates('name')
    def validate_name(self, key, value):
        if not value or len(value.strip()) < 2:
            raise ValueError("Exercise name must be at least 2 characters long.")
        return value.strip()
 
    @validates('category')
    def validate_category(self, key, value):
        if value not in self.VALID_CATEGORIES:
            raise ValueError(
                f"'{value}' isn't a valid category. "
                f"Choose from: {', '.join(self.VALID_CATEGORIES)}"
            )
        return value
 
    def __repr__(self):
        return f"<Exercise id={self.id} name='{self.name}' category='{self.category}'>"
 
 
class Workout(db.Model):
    __tablename__ = 'workouts'
 
    id = db.Column(db.Integer, primary_key=True)
 
    # The date of the workout session
    date = db.Column(db.Date, nullable=False)
 
    # How long the session lasted
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='workout',
        cascade='all, delete-orphan'
    )
 
    # Shortcut to jump from Workout straight to a list of Exercise objects.
    exercises = db.relationship(
        'Exercise',
        secondary='workout_exercises',
        back_populates='workouts'
    )
 
    @validates('duration_minutes')
    def validate_duration(self, key, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Duration must be a positive whole number (minutes).")
        return value
 
    @validates('date')
    def validate_date(self, key, value):
        if value is None:
            raise ValueError("A workout must have a date.")
        return value
 
    def __repr__(self):
        return f"<Workout id={self.id} date={self.date} duration={self.duration_minutes}min>"
 
class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'
 
    # This constraint prevents the same exercise from being added to the same workout more than once.
    __table_args__ = (
        db.UniqueConstraint('workout_id', 'exercise_id', name='unique_workout_exercise'),
    )
 
    id = db.Column(db.Integer, primary_key=True)
 
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
 
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)
 
    workout = db.relationship('Workout', back_populates='workout_exercises')
    exercise = db.relationship('Exercise', back_populates='workout_exercises')
 
    @validates('sets', 'reps', 'duration_seconds')
    def validate_positive(self, key, value):
        if value is not None and value <= 0:
            raise ValueError(f"'{key}' must be a positive number if provided.")
        return value
 
    def __repr__(self):
        return (
            f"<WorkoutExercise workout_id={self.workout_id} "
            f"exercise_id={self.exercise_id} sets={self.sets} reps={self.reps}>"
        )