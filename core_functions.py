import json
import time
import logging
import openai
import os
from packaging import version
import functions


def check_openai_version():
  required_version = version.parse("1.1.1")
  current_version = version.parse(openai.__version__)
  if current_version < required_version:
    raise ValueError(
        f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1"
    )
  else:
    logging.info("OpenAI version is compatible.")


def process_tool_calls(client, thread_id, run_id):
  while True:
    run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                   run_id=run_id)
    if run_status.status == 'completed':
      break
    elif run_status.status == 'requires_action':
      for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        if hasattr(functions, function_name):
          function_to_call = getattr(functions, function_name)
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
          logging.warning(
              f"Function {function_name} not found in functions class.")
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
