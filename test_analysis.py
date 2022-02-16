import subprocess

from analysis import list_habits, get_longest_streak, display_activity_on_habit
from dbutil import Session
from habit import Habit
from user import User


def test_list_habits():
    try:
        session = Session(autoflush=True, expire_on_commit=True)
        user = session.query(User).where(User.email == 'email').one_or_none()
        print('\n')
        list_habits(user_id=user.user_id)
        session.rollback()
        session.close()
        assert True
    except:
        assert False


def test_list_habits_with_periodicity():
    try:
        session = Session(autoflush=True, expire_on_commit=True)
        user = session.query(User).where(User.email == 'email').one_or_none()
        print('\n')
        list_habits(user_id=user.user_id, periodicity='daily')
        print()
        list_habits(user_id=user.user_id, periodicity='weekly')
        session.rollback()
        session.close()
        assert True
    except:
        assert False


def test_get_longest_streak():
    try:
        session = Session(autoflush=True, expire_on_commit=True)
        user = session.query(User).where(User.email == 'email').one_or_none()
        print('\n')
        get_longest_streak(user_id=user.user_id)
        session.rollback()
        session.close()
        assert True
    except:
        assert False


def test_get_longest_streak_of_habit():
    try:
        session = Session(autoflush=True, expire_on_commit=True)
        user = session.query(User).where(User.email == 'email').one_or_none()
        habit = session.query(Habit).where(Habit.name == 'do yoga').one_or_none()
        print('\n')
        get_longest_streak(user_id=user.user_id, habit_id=habit.habit_id)
        session.rollback()
        session.close()
        assert True
    except:
        assert False


def test_display_activity_on_habit():
    try:
        session = Session(autoflush=True, expire_on_commit=True)
        user = session.query(User).where(User.email == 'email').one_or_none()
        habit = session.query(Habit).where(Habit.name == 'do yoga').one_or_none()
        print('\n')
        display_activity_on_habit(user_id=user.user_id, habit_id=habit.habit_id)
        session.rollback()
        session.close()
        assert True
    except:
        assert False


def teardown_module():
    subprocess.call('python dbsetup.py', shell=True)