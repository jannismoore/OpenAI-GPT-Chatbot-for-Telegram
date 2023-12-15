import os
import base64
import requests

CAMPAIGN_MONITOR_API_KEY = os.environ['CAMPAIGN_MONITOR_API_KEY']
CAMPAIGN_MONITOR_LIST_ID = os.environ['CAMPAIGN_MONITOR_LIST_ID']

# Encode API key for Basic Authentication
credentials = base64.b64encode(
    f"{CAMPAIGN_MONITOR_API_KEY}:x".encode()).decode()

# The tool configuration
tool_config = {
    "type": "function",
    "function": {
        "name": "unsubscribe_newsletter",
        "description": "Unsubscribe a user from a newsletter.",
        "parameters": {
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Email address of the user."
                }
            },
            "required": ["email"]
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


# The callback function (Unsubscribes user from Campaign Monitor newsletter list)
def unsubscribe_newsletter(arguments):
  """
    Unsubscribe a user from a newsletter using Campaign Monitor.

    :param arguments: dict, Contains the necessary information for unsubscribing a user.
                       Expected key: email.
    :return: dict or str, Response from the API or error message.
    """
  # Extracting information from arguments
  email = arguments.get('email')

  # Validating the presence of the email
  if not email:
    return "Missing required information. Please provide an email address."

  # First check if the user is subscribed
  if not is_subscribed(email):
    return "User is not subscribed to the newsletter."

  # Campaign Monitor API URL and headers for unsubscribing
  url = f"https://api.createsend.com/api/v3.2/subscribers/{CAMPAIGN_MONITOR_LIST_ID}/unsubscribe.json"
  headers = {
      "Authorization": f"Basic {credentials}",
      "Content-Type": "application/json"
  }

  # Data payload for the unsubscribe API request
  data = {"EmailAddress": email}

  # Making the API request to unsubscribe
  response = requests.post(url, headers=headers, json=data)
  if response.status_code == 200:
    print("User unsubscribed successfully.")
    return response.json()
  else:
    print(f"Failed to unsubscribe user: {response.text}")
    return f"Failed to unsubscribe user: {response.text}"
