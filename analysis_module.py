from analysis import list_habits, get_longest_streak, display_activity_on_habit


def analysis_module(user_id):
    """
    Interactive menu for the analysis module.

    :param user_id: the current user
    :return action: the next action to allow the user to continue or exit the module
    """

    list_analysis_commands()

    action = ''
    while action == '':
        command = input('\nEnter command: ')

        if command == 'list_my_habits':
            list_habits(user_id=user_id)

        elif command == 'list_my_habits_with_periodicity':
            periodicity = input('Periodicity: [daily/weekly] ')
            list_habits(user_id=user_id, periodicity=periodicity)

        elif command == 'get_the_longest_streak_of_a_habit':
            habit_id = input('Habit ID: ')
            get_longest_streak(user_id=user_id, habit_id=habit_id)

        elif command == 'get_the_habit_with_the_longest_streak':
            get_longest_streak(user_id=user_id)

        elif command == 'display_my_activity_on_a_habit':
            habit_id = input('Habit ID: ')
            display_activity_on_habit(user_id=user_id, habit_id=habit_id)

        elif command == 'list_analysis_commands':
            print()
            list_analysis_commands()

        else:
            print('Invalid command!')

        action = input("\nPress 'Enter' to continue or type 'exit': ")
        while action not in ('', 'exit'):
            action = input("\nPress 'Enter' to continue or type 'exit': ")

    return action


def list_analysis_commands():
    """
    Function to list available analysis module commands.
    """

    print('-\tlist_my_habits',
          '-\tlist_my_habits_with_periodicity',
          '-\tget_the_habit_with_the_longest_streak',
          '-\tget_the_longest_streak_of_a_habit',
          '-\tdisplay_my_activity_on_a_habit',
          '-\tlist_analysis_commands', sep='\n')
