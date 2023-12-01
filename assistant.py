import os
import core_functions
import json
import config


# Create or load assistant
def create_assistant(client):
  assistant_file_path = 'assistant.json'

  # If there is an assistant.json file, load the assistant
  if os.path.exists(assistant_file_path):
    with open(assistant_file_path, 'r') as file:
      assistant_data = json.load(file)
      assistant_id = assistant_data['assistant_id']
      print("Loaded existing assistant ID.")
  else:
    # Create a new assistant

    # Find and validate all given files
    file_ids = core_functions.get_resource_file_ids(client)

    # Create the assistant
    assistant = client.beta.assistants.create(
        instructions=config.assistant_instructions,
        model="gpt-4-1106-preview",
        tools=[
            {
                "type": "retrieval"
            },
            # Define all of your available tools here
            config.schedule_viewing_tool,
            config.create_lead_tool,
            config.property_search_tool,
            config.contact_tool
        ],
        # Assuming file_ids is defined elsewhere in your code
        file_ids=file_ids)

    # Print the assistant ID or any other details you need
    print(f"Assistant ID: {assistant.id}")

    # Create a assistant.json file to save OpenAI costs
    with open(assistant_file_path, 'w') as file:
      json.dump({'assistant_id': assistant.id}, file)
      print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

  return assistant_id
