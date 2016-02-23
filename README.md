# Google Sign-In for Websites sample code

This sample code is supplement material for [Google Sign-In for Websites videos](). Best consumed watching them.

## Prerequisite
- Google App Engine
- Python 2.7
- pip
- Node.js
- Bower

## Configure
- Set up a new project at Google Developers Console
- Create credentials
- Download `client_secret_****.json`, rename it to `client_secrets.json`
- Place `client_secrets.json` at root of this project

## Build
```shell
$ pip install -t lib -r requirements.txt
$ bower install
```

## Run
``` shell
$ dev_appserver.py .
```
