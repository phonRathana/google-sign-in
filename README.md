# Google Sign-In for Websites sample code

This sample code assumes you watch "Google Sign-In for Websites" videos.  
Each videos have related section in this code example
- [Introduction to Google Sign-In for Websites](https://www.youtube.com/watch?v=Oy5F9h5JqEU)
    - [main.py](main.py)
        - "/"
    - [static/scripts/introduction.js](static/scripts/introduction.js)
- [Google Sign-In for Websites: Authentication with backends](https://www.youtube.com/watch?v=j_31hJtWjlw)
    - [main.py](main.py)
        - "/"
        - "/validate"
    - [static/scripts/authentication_with_backends.js](static/scripts/authentication_with_backends.js)
- [Google Sign-In for Websites: Authorization](https://www.youtube.com/watch?v=zZt8SFivjps)
    - Making API requests from client side
        - [main.py](main.py)
            - "/"
        - [static/scripts/authorization_client.js](static/scripts/authorization_client.js)
    - Making API requests from server side
        - [main.py](main.py)
            - "/"
            - "/api"
            - "/validate"
            - "/code"
        - [static/scripts/authorization_server.js](static/scripts/authorization_server.js)

## Installation

### Prerequisite
- Google App Engine
- Python 2.7
- pip
- Node.js
- Bower

### Configure
- Set up a new project at [Google Developers Console](https://console.developers.google.com/)
- Create credentials
- Download `client_secret_****.json`, rename it to `client_secrets.json`
- Place `client_secrets.json` at root of this project

### Build
```sh
# Install Python dependencies
$ pip install -t lib -r requirements.txt
# Install front-end dependencies
$ bower install
```

### Run
``` sh
# Launch App Engine at root dir of this project with following command
$ dev_appserver.py .
```
