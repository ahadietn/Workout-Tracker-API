from server.app import app
from server.models import db, Exercise, Workout, WorkoutExercise
from datetime import date
 
with app.app_context():
 
    # Clear existing data
    print("Clearing old data...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()
 
    # Create Exercises- These are reusable, a trainer can add any of these to any workout.
    print("Creating exercises...")
 
    squat = Exercise(name="Squat", category="strength", equipment_needed=False)
    bench_press = Exercise(name="Bench Press", category="strength", equipment_needed=True)
    treadmill_run = Exercise(name="Treadmill Run", category="cardio", equipment_needed=True)
    plank = Exercise(name="Plank", category="flexibility", equipment_needed=False)
    box_jump = Exercise(name="Box Jump", category="plyometrics", equipment_needed=True)
 
    db.session.add_all([squat, bench_press, treadmill_run, plank, box_jump])
    db.session.commit()  
    # Create Workouts
    # Three example sessions
    print("Creating workouts...")
 
    leg_day = Workout(
        date=date(2024, 1, 10),
        duration_minutes=60,
        notes="Heavy leg session — client handled it well."
    )
    upper_body = Workout(
        date=date(2024, 1, 12),
        duration_minutes=45,
        notes="Upper body push focus. Increase bench weight next session."
    )
    cardio_session = Workout(
        date=date(2024, 1, 14),
        duration_minutes=30,
        notes="Steady-state cardio. Heart rate stayed around 140bpm."
    )
 
    db.session.add_all([leg_day, upper_body, cardio_session])
    db.session.commit()  # Commit so workouts get IDs
 
    # Link Exercises to Workouts
    # This is where we use the join table to say "this exercise was done in this workout,
    print("Linking exercises to workouts")
 
    we1 = WorkoutExercise(
        workout_id=leg_day.id,
        exercise_id=squat.id,
        sets=4,
        reps=10
    )
    we2 = WorkoutExercise(
        workout_id=leg_day.id,
        exercise_id=plank.id,
        duration_seconds=60  # 1-minute plank hold
    )
    we3 = WorkoutExercise(
        workout_id=leg_day.id,
        exercise_id=box_jump.id,
        sets=3,
        reps=5
    )
 
    we4 = WorkoutExercise(
        workout_id=upper_body.id,
        exercise_id=bench_press.id,
        sets=3,
        reps=8
    )
 
    # Cardio: treadmill run (timed, no reps)
    we5 = WorkoutExercise(
        workout_id=cardio_session.id,
        exercise_id=treadmill_run.id,
        duration_seconds=1800  # 30-minute run
    )
 
    db.session.add_all([we1, we2, we3, we4, we5])
    db.session.commit()

    print("\nAll done! Database seeded successfully.")
    print(f"  {Exercise.query.count()} exercises")
    print(f"  {Workout.query.count()} workouts")
    print(f"  {WorkoutExercise.query.count()} workout-exercise links")
 