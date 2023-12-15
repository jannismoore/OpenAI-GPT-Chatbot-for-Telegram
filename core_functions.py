import json
import importlib.util
from flask import request, abort
import time
import logging
import openai
import os
from packaging import version

CUSTOM_API_KEY = os.environ.get('CUSTOM_API_KEY')


# Function to retrieve the relation between the thread ID and the telegram ID
# Change that to a database approach in case you want to scale
def load_chat_mapping():
  try:
    with open('chat_to_thread_id.json', 'r') as file:
      return json.load(file)
  except FileNotFoundError:
    return {}


# Function to store the relation between the thread ID and the telegram ID
# Change that to a database approach in case you want to scale
def save_chat_mapping(chat_to_thread_id):
  with open('chat_to_thread_id.json', 'w') as file:
    json.dump(chat_to_thread_id, file)


# Function to check API key
def check_api_key():
  api_key = request.headers.get('X-API-KEY')
  if api_key != CUSTOM_API_KEY:
    abort(401)  # Unauthorized access


# Check the current OpenAI version
def check_openai_version():
  required_version = version.parse("1.1.1")
  current_version = version.parse(openai.__version__)
  if current_version < required_version:
    raise ValueError(
        f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1"
    )
  else:
    logging.info("OpenAI version is compatible.")


# Process the actions that are initiated by the assistants API
def process_tool_calls(client, thread_id, run_id, tool_data):
  while True:
    run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                   run_id=run_id)
    if run_status.status == 'completed':
      break
    elif run_status.status == 'requires_action':
      for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
        function_name = tool_call.function.name

        try:
          arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
          logging.error(
              f"JSON decoding failed: {e.msg}. Input: {tool_call.function.arguments}"
          )
          arguments = {}  # Set to default value

        # Use the function map from tool_data
        if function_name in tool_data["function_map"]:
          function_to_call = tool_data["function_map"][function_name]
          output = function_to_call(arguments)
          client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id,
                                                       run_id=run_id,
                                                       tool_outputs=[{
                                                           "tool_call_id":
                                                           tool_call.id,
                                                           "output":
                                                           json.dumps(output)
                                                       }])
        else:
          logging.warning(f"Function {function_name} not found in tool data.")
      time.sleep(1)


# Get all of the available resources
def get_resource_file_ids(client):
  file_ids = []
  resources_folder = 'resources'
  if os.path.exists(resources_folder):
    for filename in os.listdir(resources_folder):
      file_path = os.path.join(resources_folder, filename)
      if os.path.isfile(file_path):
        with open(file_path, 'rb') as file:
          response = client.files.create(file=file, purpose='assistants')
          file_ids.append(response.id)
  return file_ids


# Function to load tools from a file
def load_tools_from_directory(directory):
  tool_data = {"tool_configs": [], "function_map": {}}

  for filename in os.listdir(directory):
    if filename.endswith('.py'):
      module_name = filename[:-3]
      module_path = os.path.join(directory, filename)
      spec = importlib.util.spec_from_file_location(module_name, module_path)
      module = importlib.util.module_from_spec(spec)
      spec.loader.exec_module(module)

      # Load tool configuration
      if hasattr(module, 'tool_config'):
        tool_data["tool_configs"].append(module.tool_config)

      # Map functions
      for attr in dir(module):
        attribute = getattr(module, attr)
        if callable(attribute) and not attr.startswith("__"):
          tool_data["function_map"][attr] = attribute

  return tool_data
