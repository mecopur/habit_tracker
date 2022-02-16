import os
import logging
from datetime import datetime, timedelta

from imports import Base, engine, update_scheduler
from dbutil import Session
from habit import Habit, Periodicity
from user import User

# remove the old database to prevent db integrity errors
db_path = os.path.join(os.getcwd(), 'Habit_Tracker.db')
os.remove(db_path)

# suppress logging of missed jobs. disabling the specific logger didn't work, might be because of threading.
logging.disable(logging.WARNING)

# create the SQLite engine 'Habit_Tracker.db' and the tables 'Activity', 'Habit', 'User' from defined SQLAlchemy ORM
# models
Base.metadata.create_all(engine)
update_scheduler.start()  # called here to trigger creation of persistent job db table 'apscheduler_jobs'


# function to generate the example objects in the db (called here subsequently)
def generate_example_data():
    session = Session(autoflush=True, expire_on_commit=True)

    try:

        # create example users
        users_to_insert = [User(name='user', email='email', password='pass'),
                           User(name='user_name', email='email@domain.com', password='password')]
        session.bulk_save_objects(users_to_insert)
        session.commit()

        four_weeks_ago = datetime.now() - timedelta(weeks=4)

        # create example habits
        habits_to_insert = [
            Habit(user_id=users_to_insert[0].user_id, name='do yoga', description='pregnancy yoga',
                  periodicity=Periodicity.from_string('weekly'), time_of_creation=four_weeks_ago),
            Habit(user_id=users_to_insert[0].user_id, name='drink water', description='3 liters per day',
                  periodicity=Periodicity.from_string('daily'), time_of_creation=four_weeks_ago),
            Habit(user_id=users_to_insert[0].user_id, name='date night', description='event or restaurant for date night',
                  periodicity=Periodicity.from_string('weekly'), time_of_creation=four_weeks_ago),
            Habit(user_id=users_to_insert[0].user_id, name='play tennis', description='play tennis on Sundays',
                  periodicity=Periodicity.from_string('weekly'), time_of_creation=four_weeks_ago),
            Habit(user_id=users_to_insert[0].user_id, name='daily walk', description='walk at least 30 minutes',
                  periodicity=Periodicity.from_string('daily'), time_of_creation=four_weeks_ago)]
        session.bulk_save_objects(habits_to_insert)
        session.commit()
        session.flush()

        # create example habit completion activities for the habits above
        yoga = session.query(Habit).where(Habit.name == 'do yoga').one_or_none()
        yoga.complete(time_of_completion=(
                four_weeks_ago + timedelta(seconds=5))), yoga.update()  # current_streak = 1, longest_streak = 1
        yoga.complete(time_of_completion=(
                four_weeks_ago + timedelta(weeks=1))), yoga.update()  # current_streak = 2, longest_streak = 2
        yoga.complete(time_of_completion=(
                four_weeks_ago + timedelta(weeks=2))), yoga.update()  # current_streak = 3, longest_streak = 3
        yoga.complete(time_of_completion=(
                four_weeks_ago + timedelta(weeks=3))), yoga.update()  # current_streak = 4, longest_streak = 4
        yoga.complete(time_of_completion=datetime.now())  # current_streak = 5, longest_streak = 5
        yoga.next_cycle_start_time = datetime.combine(yoga.next_cycle_start_time.date(), datetime.min.time())
        update_scheduler.get_job(job_id=yoga.update_job_id).modify(next_run_time=yoga.next_cycle_start_time)
        session.commit()
        session.flush()

        water = session.query(Habit).where(Habit.name == 'drink water').one_or_none()
        water.complete(time_of_completion=(
                four_weeks_ago + timedelta(seconds=10))), water.update()  # current_streak = 1, longest_streak = 1
        water.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=1))), water.update()  # current_streak = 2, longest_streak = 2
        water.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=2))), water.update()  # current_streak = 3, longest_streak = 3
        water.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=3))), water.update()  # current_streak = 4, longest_streak = 4
        water.update()  # current_streak = 0, longest_streak = 4
        water.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=14))), water.update()  # current_streak = 1, longest_streak = 4
        water.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=15))), water.update()  # current_streak = 2, longest_streak = 4
        water.update()  # current_streak = 0, longest_streak = 4
        water.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=16))), water.update()  # current_streak = 1, longest_streak = 4
        water.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=17))), water.update()  # current_streak = 2, longest_streak = 4
        water.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=18))), water.update()  # current_streak = 3, longest_streak = 4
        water.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=19))), water.update()  # current_streak = 4, longest_streak = 4
        water.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=20))), water.update()  # current_streak = 5, longest_streak = 5
        water.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=21))), water.update()  # current_streak = 6, longest_streak = 6
        water.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=22))), water.update()  # current_streak = 7, longest_streak = 7
        water.update()  # current_streak = 0, longest_streak = 7
        water.complete(time_of_completion=datetime.now())  # current_streak = 1, longest_streak = 7
        water.next_cycle_start_time = datetime.combine(water.next_cycle_start_time.date(), datetime.min.time())
        update_scheduler.get_job(job_id=water.update_job_id).modify(next_run_time=water.next_cycle_start_time)
        session.commit()
        session.flush()

        date_night = session.query(Habit).where(Habit.name == 'date night').one_or_none()
        date_night.complete(time_of_completion=(
                four_weeks_ago + timedelta(seconds=15))), date_night.update()  # current_streak = 1, longest_streak = 1
        date_night.complete(time_of_completion=(
                four_weeks_ago + timedelta(weeks=1))), date_night.update()  # current_streak = 2, longest_streak = 2
        date_night.complete(time_of_completion=(
                four_weeks_ago + timedelta(weeks=2))), date_night.update()  # current_streak = 3, longest_streak = 3
        date_night.complete(time_of_completion=(
                four_weeks_ago + timedelta(weeks=3))), date_night.update()  # current_streak = 4, longest_streak = 4
        date_night.complete(time_of_completion=datetime.now())  # current_streak = 5, longest_streak = 5
        date_night.next_cycle_start_time = datetime.combine(date_night.next_cycle_start_time.date(), datetime.min.time())
        update_scheduler.get_job(job_id=date_night.update_job_id).modify(next_run_time=date_night.next_cycle_start_time)
        session.commit()
        session.flush()

        tennis = session.query(Habit).where(Habit.name == 'play tennis').one_or_none()
        tennis.complete(time_of_completion=(
                four_weeks_ago + timedelta(seconds=20))), tennis.update()  # current_streak = 1, longest_streak = 1
        tennis.complete(time_of_completion=(
                four_weeks_ago + timedelta(weeks=1))), tennis.update()  # current_streak = 2, longest_streak = 2
        tennis.update()  # current_streak = 0, longest_streak = 2
        tennis.complete(time_of_completion=(
                four_weeks_ago + timedelta(weeks=3))), tennis.update()  # current_streak = 1, longest_streak = 2
        tennis.update()  # current_streak = 0, longest_streak = 2
        tennis.next_cycle_start_time = datetime.combine(tennis.next_cycle_start_time.date(), datetime.min.time())
        update_scheduler.get_job(job_id=tennis.update_job_id).modify(next_run_time=tennis.next_cycle_start_time)
        session.commit()
        session.flush()

        walk = session.query(Habit).where(Habit.name == 'daily walk').one_or_none()
        walk.complete(time_of_completion=(
                four_weeks_ago + timedelta(seconds=25))), walk.update()  # current_streak = 1, longest_streak = 1
        walk.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=1))), walk.update()  # current_streak = 2, longest_streak = 2
        walk.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=2))), walk.update()  # current_streak = 3, longest_streak = 3
        walk.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=3))), walk.update()  # current_streak = 4, longest_streak = 4
        walk.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=4))), walk.update()  # current_streak = 5, longest_streak = 5
        walk.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=5))), walk.update()  # current_streak = 6, longest_streak = 6
        walk.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=6))), walk.update()  # current_streak = 7, longest_streak = 7
        walk.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=7))), walk.update()  # current_streak = 8, longest_streak = 8
        walk.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=8))), walk.update()  # current_streak = 9, longest_streak = 9
        walk.update()  # current_streak = 0, longest_streak = 9
        walk.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=15))), walk.update()  # current_streak = 1, longest_streak = 9
        walk.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=16))), walk.update()  # current_streak = 2, longest_streak = 9
        walk.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=17))), walk.update()  # current_streak = 3, longest_streak = 9
        walk.update()  # current_streak = 0, longest_streak = 9
        walk.complete(time_of_completion=(
                four_weeks_ago + timedelta(days=27))), walk.update()  # current_streak = 1, longest_streak = 9
        walk.complete(time_of_completion=datetime.now())  # current_streak = 2, longest_streak = 9
        walk.next_cycle_start_time = datetime.combine(walk.next_cycle_start_time.date(), datetime.min.time())
        update_scheduler.get_job(job_id=walk.update_job_id).modify(next_run_time=walk.next_cycle_start_time)
        session.commit()

        session.close()

        print('\nSetup successfully completed!\n')

    except:
        print('\nERROR: Something went wrong!.\n')


generate_example_data()
