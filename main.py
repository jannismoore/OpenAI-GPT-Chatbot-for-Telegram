import os
import logging
from flask import Flask, request, jsonify
import openai
import telebot
import openai
import core_functions
import assistant

# Configure logging
logging.basicConfig(level=logging.INFO)

# Check OpenAI version compatibility
core_functions.check_openai_version()

# Create Flask app
app = Flask(__name__)

# Add a global dictionary to map Telegram chat IDs to OpenAI thread IDs
chat_to_thread_id = core_functions.load_chat_mapping()

# Initialize OpenAI client
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
  raise ValueError("No OpenAI API key found in environment variables")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Initialize Telegram
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Initialize all available tools
tool_data = core_functions.load_tools_from_directory('tools')

# Create or load assistant
assistant_id = assistant.create_assistant(client, tool_data)


@bot.message_handler(commands=['start'])
def send_welcome(message):
  telegram_chat_id = message.chat.id
  logging.info("Starting a new conversation...")

  # Check if this chat ID already has a thread ID
  if telegram_chat_id not in chat_to_thread_id:
    thread = client.beta.threads.create()
    chat_to_thread_id[telegram_chat_id] = thread.id

    # Save the relation
    core_functions.save_chat_mapping(chat_to_thread_id)

    logging.info(f"New thread created with ID: {thread.id}")

  bot.reply_to(message, "Howdy, how can I help you?")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
  telegram_chat_id = message.chat.id
  user_input = message.text

  # Reload chat to thread ID - This can be replaced if a database setup is implemented
  chat_to_thread_id = core_functions.load_chat_mapping()

  # Retrieve the OpenAI thread ID for this chat ID
  thread_id = chat_to_thread_id.get(str(telegram_chat_id))

  logging.info(f"XXXXXX: {thread_id}")
  logging.info(f"XXXXXX: {telegram_chat_id}")

  if not thread_id:

    # Try to reconnect the chat with a new ID instead
    if telegram_chat_id not in chat_to_thread_id:
      thread = client.beta.threads.create()
      chat_to_thread_id[telegram_chat_id] = thread.id

      # Save the relation
      core_functions.save_chat_mapping(chat_to_thread_id)

      thread_id = thread.id

      logging.info(f"XXXXXX: {thread_id}")

    if not thread_id:
      logging.error("Error: Missing OpenAI thread_id")
      return

  logging.info(
      f"Received message: {user_input} for OpenAI thread ID: {thread_id}")

  try:
    client.beta.threads.messages.create(thread_id=thread_id,
                                        role="user",
                                        content=user_input)
  except openai.error.NotFoundError:
    return False  # Thread does not exist

  run = client.beta.threads.runs.create(thread_id=thread_id,
                                        assistant_id=assistant_id)
  # This processes any possible action requests
  core_functions.process_tool_calls(client, thread_id, run.id, tool_data)

  messages = client.beta.threads.messages.list(thread_id=thread_id)
  response = messages.data[0].content[0].text.value

  # Use the original Telegram chat ID here, not the OpenAI thread ID
  bot.send_message(telegram_chat_id, response, parse_mode='Markdown')


bot.polling()

# start the app
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
