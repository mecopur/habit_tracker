from getpass import getpass
from sqlalchemy import exc

import dbutil
from activity import Activity, Category
from user import User


def access():
    """
    Authorization utility function to grant access to the user

    :return
        (0, user_id): if access is granted
        (1, None): if access is not granted
    """

    action = input()

    if action == 'login':
        user_id = login()
        return 0, user_id

    elif action == 'register':
        user_id = register()
        return 0, user_id

    elif action == 'exit':
        exit()

    else:
        print("Please type 'login' or 'register' to access the Habit Tracker App. Type 'exit' to quit.")
        return 1, None


def login():
    """
    Authorization utility function to allow the user to log in

    :return user_id: id of the current user if login is successful
    """

    login_attempt = 3
    while login_attempt != 0:
        login_attempt -= 1
        email = input('Email: ')
        # TODO: password scrambling
        password = getpass()

        # check the database for the credentials
        user_id = authenticate(email, password)
        if user_id is not None:
            # create related activity and insert into database table 'Activity'
            activity = Activity(category=Category.logged_in, user_id=user_id[0])
            dbutil.insert_into_db(activity)
            print('Login was successful. Welcome!\n')
            return user_id[0]
        elif login_attempt != 0:
            print('ERROR: Login was unsuccessful. Either email or password is wrong.', login_attempt, 'attempts '
                                                                                                      'left!\n')
        else:
            print('Access denied. Goodbye!')
            exit()


def register():
    """
    Authorization utility function to allow the user to create an account

    :return user_id: id of the current user if registration is successful
    """

    email = input('Email: ')
    password = getpass()
    user = User(email, password)
    try:
        # insert user into the database
        dbutil.insert_into_db(user)

        # check if the database is updated with the user credentials
        user_id = authenticate(email, password)
        if user_id is not None:
            # create related activity and insert into database table 'Activity'
            activity = Activity(category=Category.user_registered, user_id=user_id[0])
            dbutil.insert_into_db(activity)
            print('Registration was successful. Welcome!\n')
            return user_id[0]
    except exc.IntegrityError:
        exit()


def authenticate(email, password):
    """
    Authorization utility function to check if the provided user credentials match the records in the database

    :return user_id: id of the current user
    """

    session = dbutil.Session()

    try:
        # check the user credentials in the database
        user_id = session.query(User.user_id).filter(User.email == email, User.password == password).one_or_none()
    except exc.MultipleResultsFound:
        # catch if the email is not unique
        print('ERROR: There are multiple entries for this user.')
        exit()
    finally:
        session.close()

    return user_id
