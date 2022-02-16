import dbutil
from activity import Activity, Category
from habit import Habit, Periodicity


def habit_module(user_id):
    """
    Interactive menu for the habit module.

    :param user_id: the current user
    :return action: the next action to allow the user to continue or exit the module
    """

    list_habit_commands()

    action = ''
    while action == '':
        command = input('\nEnter command: ')

        if command == 'create_habit':
            name = input('Name: ')
            periodicity = input('Periodicity: [daily/weekly] ')
            try:
                habit = Habit(user_id=user_id, name=name, periodicity=Periodicity.from_string(periodicity))
                habit_id = habit.habit_id
                dbutil.insert_into_db(habit)
                # delete object to avoid detached instance
                if habit is not None:
                    del habit

                print("\nHabit is successfully created!")
                dbutil.fetch_from_db(habit_id, Habit)

            except ValueError:
                print('Invalid periodicity!')

        elif command == 'display_habit':
            habit_id = input('Habit ID: ')
            try:
                dbutil.fetch_from_db(habit_id, Habit)
            except AttributeError:
                print('This Habit ID does not exist!')

        elif command == 'edit_habit':
            habit_id = input('Habit ID: ')
            try:
                dbutil.fetch_from_db(habit_id, Habit)

                print('\nINFO: You can edit Name, Description and/or Periodicity.\n')
                name = input('Name: ')
                desc = input('Description: ')
                periodicity = input('Periodicity: [daily/weekly] ')
                values = (name, desc, periodicity)
                dbutil.update_in_db(habit_id, Habit, values)

                print("\nHabit is successfully updated!")
                dbutil.fetch_from_db(habit_id, Habit)

            except AttributeError:
                print('This Habit ID does not exist!')

        elif command == 'complete_habit':
            habit_id = input('Habit ID: ')
            try:
                dbutil.complete_in_db(habit_id, Habit)

                print("\nHabit is successfully completed!")
                dbutil.fetch_from_db(habit_id, Habit)

            except AttributeError:
                print('This Habit ID does not exist!')

        elif command == 'delete_habit':
            habit_id = input('Habit ID: ')

            confirmation = input("\nAre you sure that you wish to delete this habit? [yes/no] ")
            if confirmation == 'yes':
                try:
                    # delete habit from the database
                    dbutil.delete_from_db(habit_id, Habit)

                    # TODO: check if it causes database integrity issues
                    # create related activity and insert into database table 'Activity'
                    activity = Activity(category=Category.deleted_habit, user_id=user_id, habit_id=habit_id)
                    dbutil.insert_into_db(activity)
                    # delete object to avoid detached instance
                    if activity is not None:
                        del activity

                    print("\nHabit is successfully deleted!")

                except AttributeError:
                    print('This Habit ID does not exist!')

        elif command == 'list_habit_commands':
            print()
            list_habit_commands()

        else:
            print('Invalid command!')

        action = input("\nPress 'Enter' to continue or type 'exit': ")
        while action not in ('', 'exit'):
            action = input("\nPress 'Enter' to continue or type 'exit': ")

    return action


def list_habit_commands():
    """
    Function to list available habit module commands.
    """

    print('-\tcreate_habit',
          '-\tdisplay_habit',
          '-\tedit_habit',
          '-\tcomplete_habit',
          '-\tdelete_habit',
          '-\tlist_habit_commands', sep='\n')
