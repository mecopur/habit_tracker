from sqlalchemy import exc, select, delete
from sqlalchemy.orm import sessionmaker
from user import *
from habit import *
from activity import *
from imports import engine

# create the db tables 'Activity', 'Habit', 'User' from defined SQLAlchemy ORM models (w/o running dbsetup.py)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def insert_into_db(obj):
    """
    Database utility function to insert an object into the database.

    :param obj: object
    """

    session = Session(autoflush=True, expire_on_commit=True)

    try:
        # insert the object into the database
        session.add(obj)
        session.commit()

    except exc.IntegrityError:
        # catch to prevent duplicate errors for unique fields in the database
        print('ERROR: This entity already exist in the database.')
        raise

    # except:
    #     # safely exit the app in case of other exceptions
    #     print('ERROR: Something went wrong with database insertion.')
    #     exit()

    finally:
        session.close()


def fetch_from_db(obj_id, obj_type):
    """
    Database utility function to retrieve an object from the database.

    :param obj_id: object id
    :param obj_type: object type (class name)
    """

    session = Session(autoflush=True, expire_on_commit=True)


    try:
        # retrieve the object from the database
        obj = session.get(obj_type, obj_id)
        obj.display()

    except AttributeError:
        # catch if the object does not exist in the database
        raise

    # except:
    #     # safely exit the app in case of other exceptions
    #     print('ERROR: Something went wrong!.')
    #     exit()

    finally:
        session.close()


def update_in_db(obj_id, obj_type, values):
    """
    Database utility function to update an object in the database.

    :param obj_id: object id
    :param obj_type: object type (class name)
    :param values: new attribute values
    """

    session = Session(autoflush=True, expire_on_commit=True)

    try:
        # update the object in the database
        obj = session.get(obj_type, obj_id)
        obj.edit(*values)
        session.commit()

    # except:
    #     # safely exit the app in case of other exceptions
    #     print('ERROR: Something went wrong with entity update.')
    #     exit()

    finally:
        session.close()


def complete_in_db(obj_id, obj_type):
    """
    Database utility function to update the parameters of an object in the database due to 'complete' action.
    'complete()' method of the Habit class changes some # attributes of the object such as time_of_completion,
    etc. that are not accessible with edit. Therefore it # requires another dbutil function to update the object
    in the database.

    :param obj_id: object id
    :param obj_type: object type (class name)
    """

    session = Session(autoflush=True, expire_on_commit=True)

    try:
        # update the parameters of the object in the database due to complete action
        obj = session.get(obj_type, obj_id)
        obj.complete()
        session.commit()

    # except:
    #     # safely exit the app in case of other exceptions
    #     print('ERROR: Something went wrong with habit completion.')
    #     exit()

    finally:
        session.close()


def delete_from_db(obj_id, obj_type):
    """
    Database utility function to delete an object in the database.

    :param obj_id: object id
    :param obj_type: object type (class name)
    """

    session = Session(autoflush=True, expire_on_commit=True)

    try:
        # delete the object from the database
        obj = session.get(obj_type, obj_id)
        session.delete(obj)
        session.commit()

    # except:
    #     # safely exit the app in case of other exceptions
    #     print('ERROR: Something went wrong with entity deletion.')
    #     exit()

    finally:
        session.close()


def new_cycle(habit_id):
    """
    Database utility function to update the scheduled task of a habit.

    :param habit_id: habit id
    """
    session = Session(autoflush=True, expire_on_commit=True)

    try:
        # retrieve the object from the database and trigger update
        obj = session.get(Habit, habit_id)
        if obj is not None:
            obj.update()
            session.commit()

    except AttributeError:
        # catch if the object does not exist in the database
        raise

    # except:
    #     # safely exit the app in case of other exceptions
    #     print('ERROR: Something went wrong!.')
    #     exit()

    finally:
        session.close()


def display_activity(user_id):
    """
    Database utility function to fetch and display user activity.

    :param user_id: user id
    """

    session = Session(autoflush=True, expire_on_commit=True)

    try:
        # fetch user activity description ordered by timestamp
        results = session.execute(
            select(Activity.description).where(Activity.user_id == user_id).order_by(Activity.timestamp)).fetchall()

        # create related activity
        activity = Activity(category=Category.displayed_activity, user_id=user_id)

        if len(results) != 0:
            # print the results in a tabular form
            print()
            print(tabulate(results, tablefmt='simple'))
        else:
            print('\nThis user has no recorded activity!')

        # insert activity into database table 'Activity'
        dbutil.insert_into_db(activity)

    # except:
    #     # safely exit the app in case of other exceptions
    #     print('\nERROR: Something went wrong!.')
    #     exit()

    finally:
        session.close()


def delete_activity(user_id):
    """
    Database utility function to delete user activity from the database.

    :param user_id: user id
    """

    session = Session(autoflush=True, expire_on_commit=True)

    try:
        # delete user activity
        session.execute(delete(Activity).where(Activity.user_id == user_id))
        session.commit()

        print('\nThis user has no recorded activity!')

        # create related activity and insert into database table 'Activity' (to record that there was activity but it
        # is deleted)
        activity = Activity(category=Category.deleted_activity, user_id=user_id)
        dbutil.insert_into_db(activity)

    # except:
    #     # safely exit the app in case of other exceptions
    #     print('\nERROR: Something went wrong!.')
    #     exit()

    finally:
        session.close()
