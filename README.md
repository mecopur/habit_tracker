SOFTWARE REQUIREMENTS
---------------------

- conda 4.11.0 (earlier versions might also work)


INSTALLATION
------------

- Change your directory to the project directory in terminal:
    ```
    cd <path_to_project>/habit_tracker
    ```

- Create the conda environment from yaml and activate:
    ```
    conda env create -f environment_habit_tracker.yml
    conda activate habit_tracker_env
    ```

- Set up the SQLite database (HabitTracker.db) in the project directory with example data:
    ```
    python dbsetup.py
    ```

- Run the tests:
    ```
    pytest -v
    ```

- Run the application and follow the instructions on the terminal:
    ```
    python main.py
    ```

- Login with Email = 'email' and Password = 'pass' to discover the app and play with the example data:

    ```
    Type 'login' if you already have an account, 'register' to create an account or 'exit' to exit the application.
    login
    Email: email
    Password: pass
    Login was successful. Welcome!
    
    Access granted. User ID: 1234567890 
    Have fun!
    ```

- Check out Habit_Tracker.pptx for more information and instructions.
