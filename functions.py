import datetime
import json
import requests
import os

AIRTABLE_API_KEY = os.environ['AIRTABLE_API_KEY']


# Shedule a viewing
def schedule_viewing(arguments):
  """
  Schedule a property viewing.

  :param arguments: dict, Contains the necessary information for scheduling.
                     Expected keys: property_id, desired_date, desired_time, email.
  :return: str, Confirmation message of the scheduled viewing.
  """
  # Extracting information from arguments
  property_id = arguments.get('property_id')
  desired_date = arguments.get('desired_date')
  desired_time = arguments.get('desired_time')
  email = arguments.get('email')

  # Validating the presence of all required information
  if not all([property_id, desired_date, desired_time, email]):
    return "Missing required information. Please provide property_id, desired_date, desired_time, and email."

  # Validate email format (basic validation for demonstration)
  if "@" not in email or "." not in email:
    return "Invalid email format. Please provide a valid email address."

  try:
    viewing_date = datetime.datetime.strptime(desired_date, '%Y-%m-%d').date()
    viewing_time = datetime.datetime.strptime(desired_time, '%H:%M').time()
  except ValueError:
    return "Invalid date or time format. Please use 'YYYY-MM-DD' for date and 'HH:MM' for time."

  # Check if the date is in the past
  if viewing_date < datetime.date.today():
    return "Cannot schedule a viewing in the past. Please choose a future date."

  # Make.com Webhook URL and headers
  url = "https://hook.eu1.make.com/u4wbin7popup9jm5y538d5p9ia8w0jvr"
  headers = {"Content-Type": "application/json"}

  # Convert date and time to strings
  viewing_date_str = viewing_date.isoformat()
  viewing_time_str = viewing_time.strftime('%H:%M')

  # Data payload for the API request
  data = {
      "property_id": property_id,
      "viewing_date": viewing_date_str,
      "viewing_time": viewing_time_str,
      "email": email
  }

  # Convert data to JSON and make the request
  json_data = json.dumps(data)
  response = requests.post(url, headers=headers, data=json_data)
  if response.status_code == 200:
    print("Lead created successfully.")
  else:
    print("Failed to create lead.")
    return "Failed to create lead."

  # For demonstration, we'll just return a confirmation message
  return f"Viewing scheduled for Property ID {property_id} on {viewing_date} at {viewing_time}. Confirmation will be sent to {email}."


# Add lead to Airtable
def create_lead(arguments):
  """
  Add a lead to Airtable.

  :param arguments: dict, Contains the necessary information for creating a lead.
                     Expected keys: name, phone, email, property_preferences.
  :return: dict or str, Response from the API or error message.
  """
  # Extracting information from arguments
  name = arguments.get('name')
  phone = arguments.get('phone')
  email = arguments.get('email')
  property_preferences = arguments.get('property_preferences')

  # Validating the presence of all required information
  if not all([name, phone, email, property_preferences]):
    return "Missing required information. Please provide name, phone, email, and property preferences."

  # Airtable API URL and headers
  url = "https://api.airtable.com/v0/appsq0SSPLS4fgtuY/Leads"
  headers = {
      "Authorization": f"Bearer {AIRTABLE_API_KEY}",
      "Content-Type": "application/json"
  }

  # Data payload for the API request
  data = {
      "records": [{
          "fields": {
              "Name": name,
              "Phone": phone,
              "Email": email,
              "Property Preferences": property_preferences
          }
      }]
  }

  # Making the API request
  response = requests.post(url, headers=headers, json=data)
  if response.status_code == 200:
    print("Lead created successfully.")
    return response.json()
  else:
    print(f"Failed to create lead: {response.text}")
    return f"Failed to create lead: {response.text}"


# Search a property
def property_search(arguments):
  """
  Load properties from a JSON file and search based on user preferences.

  :param arguments: dict, Contains the necessary information for property search.
                     Expected keys: budget, location, property_type.
  :return: list, List of properties that match the search criteria.
  """
  # Load properties from the JSON file
  # You can replace 'properties' with your own API to fetch your most
  # recent listings based on specific criteria
  with open('sample_properties.json', 'r') as file:
    properties = json.load(file)

  budget = arguments.get('budget')
  location = arguments.get('location').lower()
  property_type = arguments.get('property_type').lower()

  # Filter properties based on the criteria
  matching_properties = [
      property for property in properties
      if property['Price'] <= budget or location in property['City'].lower()
      or property_type in property['Property Type'].lower()
  ]

  return matching_properties
