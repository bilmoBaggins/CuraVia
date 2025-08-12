# CuraVia
### Start program for the first time
Create and activate a virtual environment, then install all the required packages
```sh
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```
- Install docker desktop to run the redis server
- Open docker from your start menu
- Make sure it is running by checking for a whale icon in your system tray

In your terminal run
```sh
docker run -d -p 6379:6379 --name redis redis
uvicorn main:app --reload
```
To check which containers are running in docker
```sh
docker ps
```
To stop redis
```sh
docker stop redis
```
And ctrl+c to quit uvicorn

### To start after initial set up
```sh
docker start redis
uvicorn main:app --reload
```
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