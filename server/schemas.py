from flask_marshmallow import Marshmallow
from marshmallow import fields, validate, validates, ValidationError

ma = Marshmallow()
Schema = ma.Schema

class ExerciseLiteSchema(Schema):
    """Just enough exercise info to show inside a workout response."""
    id = fields.Int(dump_only=True)
    name = fields.Str()
    category = fields.Str()
    equipment_needed = fields.Bool()
 
 
class WorkoutLiteSchema(Schema):
    """Just enough workout info to show inside an exercise response."""
    id = fields.Int(dump_only=True)
    date = fields.Date()
    duration_minutes = fields.Int()
    notes = fields.Str()
 
 
class WorkoutExerciseNestedSchema(Schema):
    """
    Used inside WorkoutSchema to show each exercise + its performance details
    (sets, reps, duration) for that specific workout.
    This is what fulfills the stretch goal for GET /workouts/<id>.
    """
    id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)
 
    exercise = fields.Nested(ExerciseLiteSchema, dump_only=True)
 

class ExerciseSchema(Schema):
    # You can't send an id that the database generates it.
    id = fields.Int(dump_only=True)

    # required=True means this field must be in the request body when creating.
    # Length validation rejects names that are too short or too long.
    name = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100, error="Name must be between 2 and 100 characters.")
    )
 
    # OneOf restricts the value to our known categories.
    category = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['strength', 'cardio', 'flexibility', 'balance', 'plyometrics'],
            error="Category must be one of: strength, cardio, flexibility, balance, plyometrics"
        )
    )
 
    # if the client doesn't send this field, we default to False.
    equipment_needed = fields.Bool(load_default=False)
    workouts = fields.List(fields.Nested(WorkoutLiteSchema), dump_only=True)
 
    @validates('name')
    def validate_name(self, value):
        if not value.strip():
            raise ValidationError("Name can't be just whitespace.")
 
 
class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
 
    # Marshmallow handles date parsing automatically.
    date = fields.Date(required=True)
    duration_minutes = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="A workout must be at least 1 minute long.")
    )
 
    # Notes are completely optional and can be any length. 
    notes = fields.Str(allow_none=True)
 
    # This is the stretch goal — when you fetch a workout, you see each exercise
    # along with the sets/reps/duration for that session.
    workout_exercises = fields.List(
        fields.Nested(WorkoutExerciseNestedSchema),
        dump_only=True
    )
 
    @validates('duration_minutes')
    def validate_duration(self, value):
        # 10 hours is upper limit — anything beyond that is probably a typo.
        if value > 600:
            raise ValidationError("Duration can't exceed 600 minutes (10 hours). That's a lot.")
 
 
class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(required=True)
    exercise_id = fields.Int(required=True)
 
    # Range(min=1) rejects 0 or negative values.
    reps = fields.Int(allow_none=True, validate=validate.Range(min=1, error="Reps must be at least 1."))
    sets = fields.Int(allow_none=True, validate=validate.Range(min=1, error="Sets must be at least 1."))
    duration_seconds = fields.Int(
        allow_none=True,
        validate=validate.Range(min=1, error="Duration must be at least 1 second.")
    )
 
    # Read-only nested data so we can see full workout info in.
    workout = fields.Nested(WorkoutLiteSchema, dump_only=True)
    exercise = fields.Nested(ExerciseLiteSchema, dump_only=True)
 
    @validates('sets')
    def validate_sets(self, value):
        # 20 sets of anything is unrealistic 
        if value is not None and value > 20:
            raise ValidationError("Sets can't exceed 20 — that's not a workout, that's a punishment.")
 
exercise_schema=ExerciseSchema()
exercises_schema=ExerciseSchema(many=True) 
 
workout_schema=WorkoutSchema()
workouts_schema=WorkoutSchema(many=True)
 
workout_exercise_schema=WorkoutExerciseSchema()