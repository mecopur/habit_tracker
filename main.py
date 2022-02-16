"""
    Interactive menu
"""

import authutil
from analysis_module import analysis_module
from habit_module import habit_module
from user_module import user_module

print("\nWelcome to the Habit Tracker App!")
print("\nType 'login' if you already have an account, 'register' to create an account or 'exit' to exit the "
      "application.")

# authorize user
ret = authutil.access()
while ret[0] == 1:
    ret[0] = authutil.access()

user_id = ret[1]
print('Access granted. User ID:', user_id, '\nHave fun!')

# display available modules after successful access. each module can be thought of as a different screen.
module = 'Invalid module.'
action = ''
while module == 'Invalid module.':
    module = input("\nChoose module [user/habit/analysis] or type 'exit' to quit the Habit Tracker: ")
    if module == 'user':
        print("\nHere is a list of commands you can use to manage your user profile:\n")
        action = user_module(user_id=user_id)
    elif module == 'habit':
        print("\nHere is a list of commands you can use to manage your habits:\n")
        action = habit_module(user_id=user_id)
    elif module == 'analysis':
        print("\nHere is a list of commands you can use to analyse your habits:\n")
        action = analysis_module(user_id=user_id)
    elif module == 'exit':
        print('\nGood bye!')
        exit()
    else:
        print('ERROR: Invalid module')
        module = 'Invalid module.'

    if action == 'exit':
        module = 'Invalid module.'
