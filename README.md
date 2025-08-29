# CuraVia-backend


### Start program for the first time

**All terminal commands should be run in the *app* folder**\
Create and activate a virtual environment, then install all the required packages

```bash
python -m venv venv
.\venv\Scripts\activate

# to open the config file in notepad
notepad $env:USERPROFILE\.docker\config.json  # delete the line ""credsStore": "desktop"" and save

# to install all dependencies and run the program
docker-compose up --build
```
Whenever a new dependency is added to requirements.txt the build command must be run again.

- Install docker desktop to run redis, fastapi and mysql
- Open docker from your start menu
- Make sure it is running by checking for a whale icon in your system tray

```bash
# to start redis, fastapi and mysql in docker
docker compose up -d

# to view all running containers
docker ps -a
```

Automatically create db, and users, chat_history and background_jobs tables for the first time
```bash
# to create a new migration
docker compose run --rm fastapi alembic revision --autogenerate -m "create users, chat_history and background_jobs tables"

# to update pending migrations
docker compose run --rm fastapi alembic upgrade head
```

#


### To quit program

```bash
# to stop docker
docker compose down
```

#


### To start after initial set up

```bash
docker compose up -d
docker compose run --rm fastapi alembic upgrade head
```

#


### Redis commands

```bash
# to clear redis
docker compose up -d
docker exec redis_service redis-cli FLUSHALL

# to view all items in redis
docker exec redis_service redis-cli KEYS '*'

# to view a specific item where '<key>' is the actual key name
docker exec redis_service redis-cli GET <key>
```

#


### To use test seeder data

```bash
docker compose run --rm fastapi python seed/seed.py
```
Then go to your db and refresh to see the data.

#


### To quality check locally

Install required packages
```bash
pip install black flake8 mypy
```

Check for formatting errors
```bash
black --check; flake8 --check; mypy --check
```

Fix formatting errors
```bash
flake8 .; black .; mypy .
```
