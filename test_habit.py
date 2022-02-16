import subprocess
import time
from datetime import datetime, timedelta

from habit import Habit, Periodicity


def test_display():
    try:
        habit = Habit(user_id=1, name='test_habit', periodicity=Periodicity.from_string('daily'))
        print()
        habit.display()
        assert True
    except:
        assert False


def test_edit():
    try:
        habit = Habit(user_id=1, name='test_habit', periodicity=Periodicity.from_string('daily'))
        habit.edit(name='new_habit', desc='new_description', periodicity='weekly')
        assert habit.name == 'new_habit'
        assert habit.description == 'new_description'
        assert habit.periodicity == Periodicity.weekly
    except:
        assert False


def test_complete():
    try:
        # scenario 1: before calling the method, habit was not completed
        # --------------------------------------------------------------
        habit = Habit(user_id=1, name='test_habit', periodicity=Periodicity.from_string('daily'))
        assert habit.is_completed == False
        old_current_streak = habit.current_streak

        habit.complete()

        assert habit.is_completed == True
        assert habit.time_of_completion - datetime.now() <= timedelta(seconds=1)  # expected: updated completion time
        assert habit.current_streak - old_current_streak == 1  # expected: updated current streak
        assert habit.current_streak <= habit.longest_streak  # expected: condition met
        # --------------------------------------------------------------

        time.sleep(5)

        # scenario 2: before calling the method, habit was completed
        # --------------------------------------------------------------
        assert habit.is_completed == True
        old_current_streak = habit.current_streak
        old_longest_streak = habit.longest_streak

        habit.complete()

        assert habit.is_completed == True
        assert habit.time_of_completion - datetime.now() <= timedelta(seconds=1)  # expected: updated completion time
        assert habit.current_streak == old_current_streak  # expected: no change
        assert habit.longest_streak == old_longest_streak  # expected: no change
        assert habit.current_streak <= habit.longest_streak  # expected: condition met
        # --------------------------------------------------------------

    except:
        assert False


def test_update():
    try:
        # scenario 1: before calling the method, habit was not completed
        # --------------------------------------------------------------
        a_week_ago = datetime.now() - timedelta(weeks=1)
        habit = Habit(user_id=1, name='test_habit', periodicity=Periodicity.from_string('daily'),
                      time_of_creation=a_week_ago)
        assert habit.is_completed == False

        habit.update()

        assert habit.is_completed == False  # expected: no change
        assert habit.current_streak == 0  # expected: streak is lost
        # --------------------------------------------------------------

        time.sleep(5)

        # scenario 2: before calling the method, habit was completed
        # --------------------------------------------------------------
        habit.complete()
        old_current_streak = habit.current_streak
        assert habit.is_completed == True

        habit.update()

        assert habit.is_completed == False  # expected: flag reset for the next cycle
        assert habit.current_streak == old_current_streak  # expected: no change
        # --------------------------------------------------------------
    except:
        assert False


def test_reschedule_update():
    try:
        a_week_ago = datetime.now() - timedelta(weeks=1)
        habit = Habit(user_id=1, name='test_habit', periodicity=Periodicity.from_string('daily'),
                      time_of_creation=a_week_ago)
        old_next_cycle_start_time = habit.next_cycle_start_time

        habit.reschedule_update()

        assert habit.next_cycle_start_time.timestamp() > old_next_cycle_start_time.timestamp()  # expected: updated next cycle start time
    except:
        assert False


def teardown_module():
    subprocess.call('python dbsetup.py', shell=True)
