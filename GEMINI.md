# Gemini Development Workflow

For all future development on this project, the following procedure must be followed after implementing any new feature or change:

1.  **Run Database Migrations:** After making any changes to the Django models, you must generate and run the database migrations to apply the changes to the database schema.

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

2.  **Test the Implementation:** After the migrations are successfully applied, you must thoroughly test the new feature or change to ensure it works as expected and has not introduced any regressions. This can involve:
    *   Running existing automated tests.
    *   Creating new automated tests for the new feature.
    *   Manually running the relevant management commands with different arguments to test all scenarios.

This two-step process ensures that the database is always up-to-date with the code and that all features are verified before moving on to the next task.
