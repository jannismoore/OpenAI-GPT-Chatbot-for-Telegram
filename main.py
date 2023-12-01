import os
import logging
from flask import Flask, request, jsonify
import openai
import core_functions
import assistant

# Configure logging
logging.basicConfig(level=logging.INFO)

# Check OpenAI version compatibility
core_functions.check_openai_version()

# Create Flask app
app = Flask(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
  raise ValueError("No OpenAI API key found in environment variables")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Create or load assistant
assistant_id = assistant.create_assistant(client)


# Route to start the conversation
@app.route('/start', methods=['GET'])
def start_conversation():
  logging.info("Starting a new conversation...")
  thread = client.beta.threads.create()
  logging.info(f"New thread created with ID: {thread.id}")
  return jsonify({"thread_id": thread.id})


# Route to chat with the assistant
@app.route('/chat', methods=['POST'])
def chat():
  data = request.json
  thread_id = data.get('thread_id')
  user_input = data.get('message', '')

  if not thread_id:
    logging.error("Error: Missing thread_id")
    return jsonify({"error": "Missing thread_id"}), 400

  logging.info(f"Received message: {user_input} for thread ID: {thread_id}")
  client.beta.threads.messages.create(thread_id=thread_id,
                                      role="user",
                                      content=user_input)
  run = client.beta.threads.runs.create(thread_id=thread_id,
                                        assistant_id=assistant_id)
  # This processes any possible action requests
  core_functions.process_tool_calls(client, thread_id, run.id)

  messages = client.beta.threads.messages.list(thread_id=thread_id)
  response = messages.data[0].content[0].text.value
  logging.info(f"Assistant response: {response}")
  return jsonify({"response": response})


# start the app
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
