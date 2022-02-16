from uuid import uuid4
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import Enum as SqlEnum

from imports import Base


class Category(Enum):
    """
    Enumeration class for 'Activity' categories
    """

    # user module activities
    user_registered = 0
    logged_in = 1
    displayed_user_info = 2
    changed_name = 3
    changed_email = 4
    changed_password = 5
    displayed_activity = 6
    deleted_activity = 7
    user_deleted = 8

    # habit module activities
    created_habit = 10
    displayed_habit = 11
    changed_the_name_of_habit = 12
    changed_the_description_of_habit = 13
    changed_the_periodicity_of_habit = 14
    completed_habit = 15
    deleted_habit = 16

    # analysis module activities
    displayed_habits = 20
    displayed_habits_with_periodicity = 21
    displayed_the_longest_streak_of_habit = 22
    displayed_the_habit_with_the_longest_streak = 23
    displayed_activity_on_habit = 24

    @staticmethod
    def from_string(s):
        """
        Helper function to get the activity category enum from string.

        :param s: string version of the category (case sensitive)
        :return: activity category as enum
        """

        try:
            return Category[s]
        except KeyError:
            raise ValueError()


class Activity(Base):
    """
    SQL Alchemy ORM model for 'Activity' objects
    """

    __tablename__ = "Activity"
    activity_id = Column(Integer, primary_key=True)
    category = Column(SqlEnum(Category))
    description = Column(String)
    timestamp = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete='cascade'), nullable=False)
    habit_id = Column(Integer, ForeignKey("Habit.habit_id", ondelete='cascade'))

    def __init__(self, category, user_id, habit_id=None, periodicity=None, timestamp=None):
        """
        Constructor for 'Activity' class.

        :param category: enum for activity category e.g. Category.user_registered
        :param user_id: id of the user the activity belongs to
        :param habit_id: id of the habit if the activity is related to a habit
        :param periodicity: periodicity of a habit (e.g. daily, weekly)
        :param timestamp: when the activity occurred
        """

        current_time = datetime.now()
        self.activity_id = uuid4().int >> 96
        self.category = category
        self.user_id = user_id
        self.habit_id = habit_id
        self.timestamp = current_time if timestamp is None else timestamp

        # create a meaningful description based on the activity
        if category == Category.user_registered:
            self.description = "A new user registered in the database with id {0} at {1}".format(self.user_id,
                                                                                                 self.timestamp)
        elif category == Category.user_deleted:
            self.description = "User {0} deleted their account at {1}".format(self.user_id,
                                                                              self.timestamp)
        else:
            if habit_id is None:
                if periodicity is None:
                    self.description = "User {0} {1} at {2}".format(self.user_id,
                                                                    self.category.name.replace('_', ' '),
                                                                    self.timestamp)
                else:
                    self.description = "User {0} {1} '{2}' at {3}".format(self.user_id,
                                                                          self.category.name.replace('_', ' '),
                                                                          periodicity,
                                                                          self.timestamp)
            else:
                self.description = "User {0} {1} {2} at {3}".format(self.user_id,
                                                                    self.category.name.replace('_', ' '),
                                                                    self.habit_id,
                                                                    self.timestamp)
