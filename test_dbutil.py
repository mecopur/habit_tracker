import subprocess
from datetime import datetime, timedelta

import pytest
from sqlalchemy import delete, select

from activity import Activity
from dbutil import insert_into_db, Session, fetch_from_db, update_in_db, complete_in_db, delete_from_db, \
    delete_activity, display_activity, new_cycle
from habit import Habit, Periodicity
from user import User

"""

Test suite for dbutil functions

WARNING: Run the test suite instead of individual test cases as the cases depend on each other. Otherwise it might cause 
db integrity issues 

"""


def cleanup():
    session = Session(autoflush=True, expire_on_commit=True)
    old_habit_id = session.execute(select(Habit.habit_id).where(Habit.name == 'test_habit')).one_or_none()
    if old_habit_id is not None:
        old_habit = session.get(Habit, old_habit_id)
        session.delete(old_habit)
        session.commit()

    old_user_id = session.execute(select(User.user_id).where(User.email == 'test_email@domain.com')).one_or_none()
    if old_user_id is not None:
        old_user = session.get(User, old_user_id)
        session.delete(old_user)
        session.commit()

    session.close()


# cleanup if the test objects exist in the db
cleanup()

# obj expires after insert_into_db (i.e. session closes), keep attributes in a dict to compare
user = User(name='test_user', email='test_email@domain.com', password='test_password')
user_dict = {key: value for key, value in vars(user).items() if
             key != '_sa_instance_state'}  # obj expires after insert, keep attr in a dict
user_update_values = ('new_user', 'new_email@domain.com', 'new_password')
user_old_values = ('test_user', 'test_email@domain.com', 'test_password')

habit = Habit(user_id=user.user_id, name='test_habit', description='test_description',
              periodicity=Periodicity.from_string('daily'))
habit_dict = {key: value for key, value in vars(habit).items() if key != '_sa_instance_state'}
habit_update_values = ('new_habit', 'new_description', 'weekly')
habit_update_values = ('test_habit', 'test_description', 'daily')


@pytest.mark.parametrize('obj, obj_dict', [(user, user_dict), (habit, habit_dict)])
def test_insert_into_db(obj, obj_dict):
    try:
        # insert into db
        insert_into_db(obj)

        # check if the object is mapped in db correctly
        session = Session(autoflush=True, expire_on_commit=True)
        db_obj = session.get(type(obj), obj_dict.get(next(iter(obj_dict))))
        db_obj_dict = {key: value for key, value in vars(db_obj).items() if key != '_sa_instance_state'}

        assert obj_dict == db_obj_dict  # obj comparison doesn't work here as one of them is not session bound, attr dicts are compared instead.

        session.close()
    except:
        assert False


@pytest.mark.parametrize('obj, obj_dict', [(user, user_dict), (habit, habit_dict)])
def test_fetch_from_db(obj, obj_dict):
    try:
        # check if the object is fetched from db and its attrs are displayed correctly
        fetch_from_db(obj_dict.get(next(iter(obj_dict))), type(obj))
        assert True
    except:
        assert False


@pytest.mark.parametrize('obj, obj_dict, values, old_values',
                         [(user, user_dict, user_update_values, user_old_values),
                          (habit, habit_dict, habit_update_values, user_old_values)])
def test_update_in_db(obj, obj_dict, values, old_values):
    try:
        obj_id = next(iter(obj_dict))

        # object update to compare, no change in db object
        session = Session(autoflush=True, expire_on_commit=True)
        obj = session.get(type(obj), obj_dict.get(obj_id))
        obj.edit(*values)
        obj_dict = {key: value for key, value in vars(obj).items() if
                    key not in ('_sa_instance_state', 'next_cycle_start_time')}
        session.rollback()
        session.close()

        # update obj in db
        update_in_db(obj_dict.get(obj_id), type(obj), values)

        # get the updated obj from db
        session = Session(autoflush=True, expire_on_commit=True)
        db_obj = session.get(type(obj), obj_dict.get(obj_id))
        db_obj_dict = {key: value for key, value in vars(db_obj).items() if
                       key not in ('_sa_instance_state', 'next_cycle_start_time', 'activities')}

        assert obj_dict == db_obj_dict

        session.rollback()
        session.close()

        # restore obj to its old values in db
        update_in_db(obj_dict.get(obj_id), type(obj), old_values)

    except:
        assert False


# only available for habit obj
@pytest.mark.parametrize('obj, obj_dict', [(habit, habit_dict)])
def test_complete_in_db(obj, obj_dict):
    try:
        obj_id = next(iter(obj_dict))

        # before complete_in_db
        session = Session(autoflush=True, expire_on_commit=True)
        db_obj = session.get(type(obj), obj_dict.get(obj_id))

        assert db_obj.is_completed == False

        session.rollback()
        session.close()

        # complete the habit and update the obj in db
        complete_in_db(obj_dict.get(obj_id), type(obj))

        # after complete_in_db
        session = Session(autoflush=True, expire_on_commit=True)
        db_obj = session.get(type(obj), obj_dict.get(obj_id))

        assert db_obj.is_completed == True  # other attribute changes were tested in the class method Habit.complete()

        session.rollback()
        session.close()
    except:
        assert False


# only available for habit obj
@pytest.mark.parametrize('obj, obj_dict', [(habit, habit_dict)])
def test_new_cycle(obj, obj_dict):
    try:
        obj_id = next(iter(obj_dict))

        # before next_cycle
        session = Session(autoflush=True, expire_on_commit=True)
        db_obj = session.get(type(obj), obj_dict.get(obj_id))

        assert db_obj.next_cycle_start_time == datetime.combine(datetime.now().date(),
                                                                datetime.min.time()) + timedelta(days=1)

        session.rollback()
        session.close()

        # next_cycle updates the next cycle start time by periodicity * days from the time point it is triggered
        # (updates other attrs as well w.r.t. the previous state)
        new_cycle(obj_dict.get(obj_id))

        # after next_cycle
        session = Session(autoflush=True, expire_on_commit=True)
        db_obj = session.get(type(obj), obj_dict.get(obj_id))

        assert db_obj.next_cycle_start_time - (datetime.now() + timedelta(days=1)) <= timedelta(
            seconds=1)  # other changes were tested in the class method Habit.update()

        session.rollback()
        session.close()
    except:
        assert False


# only available for user obj
@pytest.mark.parametrize('obj_dict', [user_dict])
def test_display_activity(obj_dict):
    try:
        obj_id = next(iter(obj_dict))

        # display user activity
        display_activity(obj_dict.get(obj_id))
        assert True
    except:
        assert False


# only available for user obj
@pytest.mark.parametrize('obj_dict', [user_dict])
def test_delete_activity(obj_dict):
    try:
        obj_id = next(iter(obj_dict))

        # before delete_activity
        session = Session(autoflush=True, expire_on_commit=True)
        results = session.execute(
            select(Activity.description).where(Activity.user_id == obj_dict.get(obj_id)).order_by(
                Activity.timestamp)).fetchall()

        assert len(results) > 1  # even after deleting all activity there is one activity added for deletion

        session.rollback()
        session.close()

        # delete user activity (removes all previous activity but adds an activity to db for deletion)
        delete_activity(obj_dict.get(obj_id))

        # after delete_activity
        session = Session(autoflush=True, expire_on_commit=True)
        results = session.execute(
            select(Activity.description).where(Activity.user_id == obj_dict.get(obj_id)).order_by(
                Activity.timestamp)).fetchall()

        assert len(results) == 1

        desc = results[0][0]
        desc_substring = 'User {0} deleted activity'.format(obj_dict.get(obj_id))

        assert desc.__contains__(desc_substring)

        session.rollback()
        session.close()
    except:
        assert False


@pytest.mark.parametrize('obj, obj_dict', [(habit, habit_dict), (user, user_dict)])
def test_delete_from_db(obj, obj_dict):
    try:
        obj_id = next(iter(obj_dict))

        # before delete_from_db
        session = Session(autoflush=False, expire_on_commit=True)
        db_obj = session.get(type(obj), obj_dict.get(obj_id))

        assert db_obj is not None

        session.rollback()
        session.close()

        # delete the habit from db
        delete_from_db(obj_dict.get(obj_id), type(obj))

        # after delete_from_db
        session = Session(autoflush=True, expire_on_commit=True)
        db_obj = session.get(type(obj), obj_dict.get(obj_id))

        assert db_obj is None

        session.rollback()
        session.close()
    except:
        assert False


def teardown_module():
    subprocess.call('python dbsetup.py', shell=True)
