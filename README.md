# Fast-Api Starter Template

## License

This project is licensed under the terms of the MIT license.

## What does this project include

This project is intended for a base for your fastapi projects. It includes JWT Token authentication, pytest configurations, email verification, events, and an overall organized project structure. With this project you can start worrying about what to actually implement, rather than the infrastructure, authentication, configurations etc. you need to build in order to create your API.

### How to run the app

#### Either you use docker-compose

`docker-compose up -d`

#### Or run locally

When you're running the project locally, make sure you rename .env.sample to .env

`python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

### How to make migrations

make migrations:

`alembic revision --autogenerate -m "create account table"`

update db:

`alembic upgrade head`

### How to run tests

Simply use `pytest` command to run all the tests.

### Access to Swagger

You can access to documentation after running the server at localhost:8000/docs

### Commit Rules

Be sure to install pre-commit hooks before you start working on the project. You can do this by running `pre-commit install` in the root directory of the project. This will ensure that your code is formatted correctly and that you don't commit unformatted code.
To install required packages, run `pip install -r requirements-dev.txt` in the root directory of the project.
Use pre-commit before pushing, `pre-commit run --all` this will fix errors as well as notifying you about the inconsistencies

#### Contribution

Since this project is meant to be a starter template, we shouldn't add more to it, rather, if there are some stuff you think that needs cutting out, I am willing to cut them out of this project.

All the PR's should follow this project's pre-commit rules.
