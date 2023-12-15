import os
import base64
import requests
import re

CAMPAIGN_MONITOR_API_KEY = os.environ['CAMPAIGN_MONITOR_API_KEY']
CAMPAIGN_MONITOR_LIST_ID = os.environ['CAMPAIGN_MONITOR_LIST_ID']

# Encode API key for Basic Authentication
credentials = base64.b64encode(
    f"{CAMPAIGN_MONITOR_API_KEY}:x".encode()).decode()

# The tool configuration
tool_config = {
    "type": "function",
    "function": {
        "name": "signup_newsletter",
        "description": "Sign up a user to a newsletter.",
        "parameters": {
            "type": "object",
            "properties": {
                "first_name": {
                    "type": "string",
                    "description": "First name of the user."
                },
                "email": {
                    "type": "string",
                    "description": "Email address of the user."
                },
            },
            "required": ["first_name", "email"]
        }
    }
}


# Helper function to check subscription status
def is_subscribed(email):
  """
    Check if a user is subscribed to the newsletter.

    :param email: str, Email address of the user to check.
    :return: bool, True if subscribed, False otherwise.
    """
  check_url = f"https://api.createsend.com/api/v3.2/subscribers/{CAMPAIGN_MONITOR_LIST_ID}.json?email={email}"
  headers = {
      "Authorization": f"Basic {credentials}",
      "Content-Type": "application/json"
  }

  response = requests.get(check_url, headers=headers)
  return response.status_code == 200


# The callback function (Adds user to Campaign Monitor newsletter list)
def signup_newsletter(arguments):
  """
    Sign up a user to a newsletter using Campaign Monitor.

    :param arguments: dict, Contains the necessary information for signing up a user.
                       Expected keys: first_name, email.
    :return: dict or str, Response from the API or error message.
    """
  # Extracting information from arguments
  first_name = arguments.get('first_name')
  email = arguments.get('email')

  # Validating the presence of all required information
  if not all([first_name, email]):
    return "Missing required information. Please provide first name and email."

  # Validating email format
  if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
    return "Invalid email format. Please provide a valid email address."

  # First check if the user is already subscribed
  if is_subscribed(email):
    return "User is already subscribed to the newsletter."

  # Campaign Monitor API URL and headers for signing up
  url = f"https://api.createsend.com/api/v3.2/subscribers/{CAMPAIGN_MONITOR_LIST_ID}.json"
  headers = {
      "Authorization": f"Basic {credentials}",
      "Content-Type": "application/json"
  }

  # Data payload for the API request
  data = {
      "EmailAddress": email,
      "Name": first_name,
      "ConsentToTrack": "Yes"  # Can be made dynamic if necessary
  }

  # Making the API request to sign up
  response = requests.post(url, headers=headers, json=data)
  if response.status_code == 200 or response.status_code == 201:
    print("User signed up successfully.")
    return response.json()
  else:
    print(
        f"Failed to sign up user: {response.text} with code {response.status_code}"
    )
    return f"Failed to sign up user: {response.text} with code {response.status_code}"
