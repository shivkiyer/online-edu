# online-edu
## An open-source project for hosting online video courses.

The objective of this project is to provide online educators a platform to host their online courses along with other educational services.

For an instructor:
- Allows an unrestricted platform for hosting online courses - no restrictions on the length of courses, type of courses or nature of videos.
- Allows to manage student registration and to adjust prices of courses.
- Provides a forum to market other educational services to students who have indicated their preference to receive these notifications.


For a student:
- Can browse through available published courses and preview courses before purchasing them.
- Can post questions and queries similar to most other MOOC websites.
- Can form groups for collaborative study.
- Allows a certain degree of anonymity and to opt out of marketing emails.


### Components of the web app:
- A Python/Django/Django Rest Framework backend
- An Angular frontend
- A React frontend
- A MySQL database

This app is under construction. This is the current state of the app:
- A superuser needs to be created who can assign admin privileges to other users.
- Users can register through the API specifying an email as username and a password. Users will receive a verification email that needs to be clicked to activate the account.
- Only an admin user can be an instructor. An admin can create new courses and add other admin users as instructors.
- An instructor can publish or unpublish courses, add lectures to courses, and video content to lectures.
- A normal user can fetch the list of published courses, and within a published course, view the list of lectures.
- A normal user can register for a course, after which they can view the details of lectures.



## Installation

`pip install -r requirements.txt`

## Configuration

To be able to run a development server, environment keys need to be entered in env.py in online_edu/server directory. Use the env_specs.py file to find out which keys need to be entered. The app will send verification emails for which an email account needs to be configured. Check out the instructions on our email provider to find out how to perform email integration. The password that needs to be entered in the env.py file is not the same as the email password entered in the web or mobile app, but rather a password generated on the email provider.

## Development server

To spin up a development server, first setup the database:

`cd online_edu`

`python manage.py makemigrations user_auth courses registration lectures video_contents`

`python manage.py migrate`

To run the Django development server:

`python manage.py runserver`

The API can be accessed through either Postman or through a browser or even command line.
