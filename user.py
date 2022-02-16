import pandas
from tabulate import tabulate
from uuid import uuid4
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

import dbutil
from activity import Activity, Category
from imports import Base


class User(Base):
    """
    SQL Alchemy ORM model for 'User' objects
    """

    __tablename__ = "User"
    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    habits = relationship("Habit", cascade="all, delete")
    activities = relationship("Activity", cascade="all, delete")

    def __init__(self, email, password, user_id=None, name=None):
        """
        Constructor for 'User' class.

        :param email: user email
        :param password: user password
        :param user_id: user id
        :param name: name of the user
        """

        self.user_id = uuid4().int >> 96 if user_id is None else user_id
        self.name = name
        self.email = email
        self.password = password

        # TODO: create checks for valid email and password

    def __eq__(self, obj):
        """
        Equality operator for user attribute comparison.

        :param obj: user object
        """

        self_dict = {key: value for key, value in vars(self).items() if key != '_sa_instance_state'}
        obj_dict = {key: value for key, value in vars(obj).items() if key != '_sa_instance_state'}
        return self_dict == obj_dict

    def display(self):
        """
        User class method to display user attributes, except the password.
        """

        print('\nUser Info: ')
        variables = {key: value for key, value in vars(self).items() if key not in ('password', '_sa_instance_state')}
        df = pandas.DataFrame.from_records([variables])
        print(tabulate(df.T, tablefmt='simple'))

        # insert into database table 'activity' as 'displayed_user_info' activity
        activity = Activity(category=Category.displayed_user_info, user_id=self.user_id)
        dbutil.insert_into_db(activity)

    def edit(self, name=None, email=None, password=None):
        """
        User class method to edit a user. It updates the user record only if new and valid values are provided,
        otherwise the attributes remain unchanged.

        :param name: name of the user
        :param email: user email
        :param password: user password
        """

        if name not in (self.name, '', None):
            self.name = name
            # create related activity and insert into database table 'Activity'
            activity = Activity(category=Category.changed_name, user_id=self.user_id)
            dbutil.insert_into_db(activity)

        if email not in (self.email, '', None):
            self.email = email
            # create related activity and insert into database table 'Activity'
            activity = Activity(category=Category.changed_email, user_id=self.user_id)
            dbutil.insert_into_db(activity)

        if password not in (self.password, '', None):
            self.password = password
            # create related activity and insert into database table 'Activity'
            activity = Activity(category=Category.changed_password, user_id=self.user_id)
            dbutil.insert_into_db(activity)
