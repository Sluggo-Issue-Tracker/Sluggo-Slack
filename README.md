# Sluggo-Slack
A slack application that will communicate with Sluggo's REST api.

## Installation
Currently, installation steps are focused on development. This process 
will hopefully be simplified once more complete versions of the tracker
are available.

To install Sluggo on development machines, perform the following:

1. Create the virtual environment for Sluggo using the command 
`python3 -m venv env`

2. Activate the Sluggo virtual environment. 
    
    a. For POSIX platforms (macOS
and Linux) run:
`source ./env/bin/activate`

    b. For Windows:
`.\env\Scripts\activate.bat`

3. Install the dependencies for Sluggo to run using the command 
`pip install -r ./requirements.txt`

4. Set the environment variable `SLACK_DJANGO_KEY` to some random, 
unique value (only important for production):
`export SLACK_DJANGO_KEY="not important for non producton"`

5. Obtain the Slack Bot's  _Bot User OAuth Access Token_ from [here](https://api.slack.com/apps/A01K80T5XCP/oauth?),
and set the environment variable `SLACK_BOT_TOKEN` to it in your work environment.

6. To obtain a request url for Slack to communicate with, install [Ngrok](https://ngrok.com/) and make an account.


## Running

1. Activate the virtual environment shown in the Installation steps.

    a. For POSIX platforms (macOS and Linux):
`source ./env/bin/activate`

    b. For Windows:
`.\env\Scripts\activate.bat`

2. Run the following command whenever changes to the database models 
are made. This is likely necessary whenever new versions of the 
repository are pulled, or your version of SluggoAPI is otherwise 
upgraded:
`python manage.py makemigrations; python manage.py migrate`

3. Run with:
`python manage.py runserver`

4. In a seperate terminal run:
`ngrok http <YOUR DJANGO PORT>` which will give you a url to use for all requests. Replace the URLs within the command you are working on in the api's website.