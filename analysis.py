import pandas
from tabulate import tabulate
from sqlalchemy import select, and_, func

import dbutil
from habit import Habit, Periodicity
from activity import Activity, Category


def list_habits(user_id, periodicity=None):
    """
    Analysis function to display the tracked habits of the current user. It can print out the results for the below
    commands:
        - list_my_habits
        - list_my_habits_with_periodicity

    :param user_id: current user
    :param periodicity: enumeration [daily/weekly]
    """

    session = dbutil.Session(autoflush=True)

    try:
        if periodicity is None:
            # list_my_habits
            results = session.execute(select(Habit.habit_id, Habit.name).where(Habit.user_id == user_id)).fetchall()
            headers = ['ID', 'Name']

            # create related activity
            activity = Activity(category=Category.displayed_habits, user_id=user_id)

        else:
            # list_my_habits_with_periodicity
            results = session.execute(select(Habit.habit_id, Habit.name, Habit.periodicity).where(and_(
                Habit.user_id == user_id, Habit.periodicity == Periodicity.from_string(periodicity)))).fetchall()
            headers = ['ID', 'Name', 'Periodicity']

            # create related activity
            activity = Activity(category=Category.displayed_habits_with_periodicity, user_id=user_id,
                                periodicity=periodicity)

        if len(results) != 0:
            # print the results in a tabular form
            df = pandas.DataFrame(results, columns=headers)
            print(tabulate(df, showindex=False, headers=df.columns, colalign=("left",)))
        else:
            print("\nYou don't have any habits!")

        # insert activity into database table 'Activity'
        dbutil.insert_into_db(activity)

    except ValueError:
        # catch invalid periodicity input
        print('\nERROR: Periodicity is invalid!')

    # except:
    #     # safely exit the app in case of other exceptions
    #     print('\nERROR: Something went wrong!')
    #     exit()

    finally:
        session.close()


def get_longest_streak(user_id, habit_id=None):
    """
    Analysis function to display the longest streak of the tracked habits of the current user. It can print out the
    results for the below commands:
        - get_the_habit_with_the_longest_streak
        - get_the_longest_streak_of_a_habit

    :param user_id: current user
    :param habit_id: id of a specific habit
    """

    session = dbutil.Session(autoflush=True)

    try:
        if habit_id is None:
            # get_the_habit_with_the_longest_streak
            results = session.execute(select(Habit.name, Habit.longest_streak).where(and_(
                Habit.user_id == user_id,
                Habit.longest_streak == select(func.max(Habit.longest_streak)).scalar_subquery()))).fetchall()
            headers = ['Name', 'Longest Streak']

            # create related activity
            activity = Activity(category=Category.displayed_the_habit_with_the_longest_streak, user_id=user_id)

        else:
            # get_the_longest_streak_of_a_habit
            results = session.execute(
                select(Habit.name, Habit.longest_streak).where(
                    and_(Habit.user_id == user_id, Habit.habit_id == habit_id))).fetchall()
            headers = ['Name', 'Longest Streak']

            # create related activity
            activity = Activity(category=Category.displayed_the_longest_streak_of_habit, user_id=user_id,
                                habit_id=habit_id)

        if len(results) != 0:
            # print the results in a tabular form
            df = pandas.DataFrame(results, columns=headers)
            print(tabulate(df, showindex=False, headers=df.columns, colalign=('left', 'left')))
        else:
            print('\nThis habit does not exist!')

        # insert activity into database table 'Activity'
        dbutil.insert_into_db(activity)

    # except:
    #     # safely exit the app in case of other exceptions
    #     print('\nERROR: Something went wrong!.')
    #     exit()

    finally:
        session.close()


def display_activity_on_habit(user_id, habit_id):
    """
    Analysis function to display the activities the current user performed on a habit.

    :param user_id: current user
    :param habit_id: id of a specific habit
    """

    session = dbutil.Session(autoflush=True)

    try:
        # display_my_activity_on_a_habit
        results = session.execute(
            select(Activity.description).where(
                and_(Activity.user_id == user_id, Activity.habit_id == habit_id)).order_by(
                Activity.timestamp)).fetchall()

        # create related activity
        activity = Activity(category=Category.displayed_activity_on_habit, user_id=user_id, habit_id=habit_id)

        if len(results) != 0:
            # print the results in a tabular form
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
