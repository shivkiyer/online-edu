# These are the keys needed for the settings.py file.
# The keys need to entered into env.py file.

SECRET_KEY = 'string'

# Base URL
BASE_URL = 'domain name'  # for dev server - 'http://localhost:8000'

# Email settings
EMAIL_HOST = 'email-host'   # for gmail - 'smtp.gmail.com'
EMAIL_USERNAME = 'username'
EMAIL_FROM_USERNAME = 'from-username'   # can be same as username
EMAIL_PASSWORD = 'password'   # set app-password in Security of Google account
EMAIL_PORT = 123              # 587 for SMTP if using google

# Account verification settings
EMAIL_VERIFICATION_TIMELIMIT = 30        # time limit in minutes
