from getpass import getpass
import dbutil
from user import User


def user_module(user_id):
    """
    Interactive menu for the user module.

    :param user_id: the current user
    :return action: the next action to allow the user to continue or exit the module
    """

    list_user_commands()

    action = ''
    while action == '':
        command = input('\nEnter command: ')

        if command == 'display_my_account_info':
            dbutil.fetch_from_db(user_id, User)

        elif command == 'change_name':
            name = input('Name: ')
            values = (name, None, None)
            dbutil.update_in_db(user_id, User, values)
            print("\nUser name is successfully updated!")
            dbutil.fetch_from_db(user_id, User)

        elif command == 'change_email':
            email = input('Email: ')
            values = (None, email, None)
            dbutil.update_in_db(user_id, User, values)
            print("\nUser email is successfully updated!")
            dbutil.fetch_from_db(user_id, User)

        elif command == 'change_password':
            password = getpass()
            values = (None, None, password)
            dbutil.update_in_db(user_id, User, values)
            print("\nUser password is successfully updated!")

        elif command == 'display_my_activity':
            dbutil.display_activity(user_id=user_id)

        elif command == 'delete_my_activity':
            dbutil.delete_activity(user_id=user_id)

        elif command == 'delete_my_account':
            confirmation = input("\nAre you sure that you wish to delete your account? [yes/no] ")
            if confirmation == 'yes':
                # delete user from the database (all associated entities are removed as well)
                dbutil.delete_from_db(user_id, User)
                print("\nUser account is successfully deleted! Exiting the app now...\n")
                exit()

        elif command == 'list_user_commands':
            print()
            list_user_commands()

        else:
            print('Invalid command!')

        action = input("\nPress 'Enter' to continue or type 'exit': ")
        while action not in ('', 'exit'):
            action = input("\nPress 'Enter' to continue or type 'exit': ")

    return action


def list_user_commands():
    """
    Function to list available user module commands.
    """

    print('-\tdisplay_my_account_info',
          '-\tchange_name',
          '-\tchange_email',
          '-\tchange_password',
          '-\tdisplay_my_activity',
          '-\tdelete_my_activity',
          '-\tdelete_my_account',
          '-\tlist_user_commands', sep='\n')
