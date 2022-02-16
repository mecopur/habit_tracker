import pandas
from datetime import datetime, timedelta
from tabulate import tabulate
from enum import Enum
from uuid import uuid4
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy import Enum as SqlEnum

import dbutil
from activity import Activity, Category
from imports import Base, update_scheduler


class Periodicity(Enum):
    """
    Enumeration class for 'Habit' periodicity
    """

    daily = 1
    weekly = 7

    @staticmethod
    def from_string(s):
        """
        Helper function to get the periodicity enum from string.

        :param s: string version of the periodicity (case sensitive)
        :return: periodicity as enum
        """

        try:
            return Periodicity[s]
        except KeyError:
            raise ValueError()


class Habit(Base):
    """
    SQL Alchemy ORM model for 'Habit' objects
    """

    __tablename__ = "Habit"
    habit_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    periodicity = Column(SqlEnum(Periodicity))
    time_of_creation = Column(DateTime)
    is_completed = Column(Boolean)
    time_of_completion = Column(DateTime)
    next_cycle_start_time = Column(DateTime)
    current_streak = Column(Integer)
    longest_streak = Column(Integer)
    update_job_id = Column(String)
    user_id = Column(Integer, ForeignKey("User.user_id", ondelete='cascade'))
    activities = relationship("Activity", cascade="all, delete")

    def __init__(self, user_id, periodicity, name, description=None, time_of_creation=None, next_cycle_start_time=None):
        """
        Constructor for 'Habit' class.

        :param user_id: id of the user the habit belongs to
        :param periodicity: periodicity of a habit (e.g. daily, weekly)
        :param name: name of the habit
        :param description: description of the habit
        :param time_of_creation: when the habit is created
        :param next_cycle_start_time: next run time of the scheduled job
        """

        current_time = datetime.now()
        self.habit_id = uuid4().int >> 96
        self.user_id = user_id
        self.name = name
        self.description = '' if description is None else description
        self.periodicity = periodicity
        self.time_of_creation = current_time if time_of_creation is None else time_of_creation
        self.is_completed = False
        self.time_of_completion = datetime.min
        self.current_streak = 0
        self.longest_streak = 0

        # start time of the next cycle e.g. tomorrow 00:00:00 for daily periodicity
        calculated_start_time = datetime.combine(self.time_of_creation.date(), datetime.min.time()) + timedelta(days=self.periodicity.value)
        self.next_cycle_start_time = calculated_start_time if next_cycle_start_time is None else next_cycle_start_time

        # create and configure a job to schedule periodic updates to track the habit
        self.update_job_id = uuid4().hex
        trigger = IntervalTrigger(days=self.periodicity.value)
        update_scheduler.add_job(id=self.update_job_id, func=dbutil.new_cycle, args=(self.habit_id,), trigger=trigger, replace_existing=True)
        update_scheduler.get_job(job_id=self.update_job_id).modify(next_run_time=self.next_cycle_start_time)

        # create related activity and insert into database table 'Activity'
        activity = Activity(category=Category.created_habit, user_id=self.user_id, habit_id=self.habit_id, timestamp=self.time_of_creation)
        dbutil.insert_into_db(activity)

    def display(self):
        """
        Habit class method to display a habit.
        """

        print('\nHabit Info: ')
        # collect and display relevant attributes for the habit
        variables = {key: value for key, value in vars(self).items() if key not in ('_sa_instance_state', 'user_id', 'update_job_id')}
        df = pandas.DataFrame.from_records([variables])
        print(tabulate(df.T, tablefmt='simple'))

        # create related activity and insert into database table 'Activity'
        activity = Activity(category=Category.displayed_habit, user_id=self.user_id, habit_id=self.habit_id)
        dbutil.insert_into_db(activity)

    def edit(self, name=None, desc=None, periodicity=None):
        """
        Habit class method to edit a habit. It updates the habit record only if new and valid values are provided,
        otherwise the attributes remain unchanged.

        :param name: name of the habit
        :param desc: description of the habit
        :param periodicity: periodicity of teh habit (e.g. daily, weekly)
        """

        if name not in (self.name, '', None):
            self.name = name
            # create related activity and insert into database table 'Activity'
            activity = Activity(category=Category.changed_the_name_of_habit, user_id=self.user_id, habit_id=self.habit_id)
            dbutil.insert_into_db(activity)

        if desc not in (self.description, '', None):
            self.description = desc
            # create related activity and insert into database table 'Activity'
            activity = Activity(category=Category.changed_the_description_of_habit, user_id=self.user_id,
                                habit_id=self.habit_id)
            dbutil.insert_into_db(activity)
        try:
            periodicity = Periodicity.from_string(periodicity)
            if periodicity not in (self.periodicity, '', None):
                self.periodicity = periodicity
                # reschedule the job since the periodicity has a new value
                self.reschedule_update()
                # create related activity and insert into database table 'Activity'
                activity = Activity(category=Category.changed_the_periodicity_of_habit, user_id=self.user_id,
                                    habit_id=self.habit_id)
                dbutil.insert_into_db(activity)
        except ValueError:
            print('\nWARNING: Invalid periodicity. No change will be applied to periodicity!')

    def complete(self, time_of_completion=None):
        """
        Habit class method to complete a habit.

        :param time_of_completion: when the habit is completed
        """

        # update the relevant attributes when the habit is completed
        self.time_of_completion = datetime.now() if time_of_completion is None else time_of_completion
        if not self.is_completed and self.time_of_completion.timestamp() < self.next_cycle_start_time.timestamp():
            self.is_completed = True
            self.current_streak += 1
            self.longest_streak = self.current_streak if self.current_streak > self.longest_streak else self.longest_streak

        # create related activity and insert into database table 'Activity'
        activity = Activity(category=Category.completed_habit, user_id=self.user_id, habit_id=self.habit_id, timestamp=self.time_of_completion)
        dbutil.insert_into_db(activity)

    def update(self):
        """
        Habit class method to update the tracking attributes of a habit.
        """

        # update the relevant attributes in the next cycle and reschedule the job
        self.current_streak = self.current_streak if self.is_completed else 0
        self.longest_streak = self.current_streak if self.current_streak > self.longest_streak else self.longest_streak
        self.is_completed = False
        self.reschedule_update()

    def reschedule_update(self, trigger=None):
        """
        Habit class method to update the scheduled job of a habit

        :param trigger: custom trigger for the background job scheduler
        """

        # reschedule the job for the next cycle
        trigger = IntervalTrigger(days=self.periodicity.value) if trigger is None else trigger
        update_scheduler.get_job(job_id=self.update_job_id).reschedule(trigger)
        self.next_cycle_start_time = datetime.combine(update_scheduler.get_job(job_id=self.update_job_id).next_run_time.date(), datetime.min.time())
        update_scheduler.get_job(job_id=self.update_job_id).modify(next_run_time=self.next_cycle_start_time)
