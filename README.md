# CuraVia


### Start program for the first time

**All terminal commands should be run in the *app* folder**\
Create and activate a virtual environment, then install all the required packages

```sh
python -m venv venv
.\venv\Scripts\activate
notepad $env:USERPROFILE\.docker\config.json # to open notepad, then delete the line ""credsStore": "desktop"" and save
docker-compose up --build # to install all dependencies and run the program
```
Whenever a new dependency is added to requirements.txt the build command must be run again.

- Install docker desktop to run redis, fastapi and mysql
- Open docker from your start menu
- Make sure it is running by checking for a whale icon in your system tray

```sh
docker compose up -d # to start redis, fastapi and mysql in docker

docker ps -a # to view all running containers
```

Automatically create db, and users and chat_history tables for the first time
```sh
docker compose run --rm fastapi alembic revision --autogenerate -m "create users and chat_history tables" # to create a new migration
docker compose run --rm fastapi alembic upgrade head # to update pending migrations
```

#


### To quit program

```sh
docker compose down # to stop docker
```

#


### To start after initial set up


```sh
docker compose up -d
docker compose run --rm fastapi alembic upgrade head
```

#


### To use test seeder data

```sh
docker compose run --rm fastapi python seed/seed.py
```
Then go to your db and refresh to see the data.

#


### To quality check locally

Install required packages
```sh
pip install black flake8 mypy
```

To check for formatting errors
```sh
black --check
flake8 --check
mypy --check
```

To fix formatting errors
```sh
flake8 .
black .
mypy .
```

#