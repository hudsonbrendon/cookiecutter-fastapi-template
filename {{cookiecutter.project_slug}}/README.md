# 🎉 Backend {{cookiecutter.project_name}} 🎉

## Configure and run 🚀

To configure:

If you don't already have a .env file with your settings. Use the basic version for local testing use:

```bash
cp dot-env-template .env
```

Then build and launch the test/debug stack for the development environment with:

```bash
docker compose -f docker-compose.dev.yml up --build
```

Or in production environment with:

```bash
docker compose up --build
```

- Visit http://localhost:4000/docs to view the interactive API (Swagger) docs. To get the initial superuser username and password to authenticate for the first time, see your **.env** file.
- Modify your code, which is linked to the _api_ container, and watch uvicorn automatically restart your application when the changes are made.

# Virtual environment

Using [pyenv](https://github.com/pyenv/pyenv), install Python 3.11 and create a virtual environment with the command below:

```bash
python3 -m venv venv
```

With the environment created, activate it with:

```bash
source venv/bin/activate
```

# Pre-commit

With the virtual environment activated, run the command below:

```bash
pre-commit install
```

[pre-commit](https://pre-commit.com/) is a hook manager for git that applies numerous validations during commit. Python, yml and json file formatting validations are present in this project.

If you need to skip the validation step due to some rule in the document, use the following command:

```bash
git commit --no-verify -m "chore: skiip pre-commit devido a $seu-motivo-aqui "
```

## Tests

To run tests in a development environment directly in Docker, run:

```bash
docker-compose -f docker-compose.dev.yml exec api pytest

```

If you want to run the tests directly in the vscode interface, in your .env, set the variable **POSTGRES_SERVER** with the value _localhost_

This way, with the virtual environment activated, it is also possible to run the tests directly in the terminal with the command:

```bash
pytest
```

And run the application directly in vscode using the run and debug option.

If you want to run a specific test, run:

```bash
docker-compose -f docker-compose.dev.yml run api pytest -k "<test-name>"
```

or

```bash
pytest -k "test-name>"
```

If you are running the application in your virtual environment.

If the database has not been created, back up your current database.

With Docker running, drop all existing volumes:

```bash
docker-compose -f docker-compose.dev.yml down --volumes
```

## Migrations

**Attention!** - When creating a new table in models, it is important to add the import of your new model to the "models/**init**.py" file, following the naming convention of the other imports.
This way, Alembic will recognize the creation of the table to perform the migration to the database.
Example:

```bash
from .model import Model

```

To create a new migration, run:
```bash
docker-compose -f docker-compose.dev.yml run api alembic revision --autogenerate -m "<nome-da-migration>"

```

To apply the migration, run:

```bash
docker-compose -f docker-compose.dev.yml run api alembic upgrade head

```

## Database

To backup, restore and clean the database in the container, use the following commands:

Backup

```bash
PGPASSWORD=${POSTGRES_PASSWORD} pg_dump -h localhost -U ${POSTGRES_USER}  ${POSTGRES_DB} > backup.sql

```

- How to update pgdump [Link](https://askubuntu.com/questions/-1456014/how-to-upgrade-postgresql-from-14-to-15-on-ubuntu-22-04).

Restore

```bash
PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost  -U ${POSTGRES_USER}  ${POSTGRES_DB} < backup.sql

```
- If you get a duplicate key error, reset the database.

Clear the Database

```bash
PGPASSWORD=${POSTGRES_PASSWORD} psql -h localhost -U ${POSTGRES_USER}  -d ${POSTGRES_DB} -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

```

## Branch and commit patterns

To create branches we use the Git Flow pattern, read more about it at:

[https://danielkummer.github.io/git-flow-cheatsheet/](https://danielkummer.github.io/git-flow-cheatsheet/)

And for commits we follow the Conventional Commits conventions, read more about it at:

[https://www.conventionalcommits.org/en/v1.0.0/](https://www.conventionalcommits.org/en/v1.0.0/)

## Contribute! 🤝
