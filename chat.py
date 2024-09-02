from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import json
import os
from huggingface_hub import InferenceClient

chat_bp = Blueprint('chat_bp', __name__, template_folder='templates')

# Initialize the InferenceClient
client = InferenceClient(
    "HuggingFaceH4/zephyr-7b-beta",
    token="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",
)

CHAT_HISTORY_FILE = 'chat_history.json'

# Ensure the JSON file exists
if not os.path.exists(CHAT_HISTORY_FILE):
    with open(CHAT_HISTORY_FILE, 'w') as f:
        json.dump({}, f)

def load_chat_history():
    with open(CHAT_HISTORY_FILE, 'r') as f:
        return json.load(f)

def save_chat_history(chat_history):
    with open(CHAT_HISTORY_FILE, 'w') as f:
        json.dump(chat_history, f)

@chat_bp.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    username = session['username']
    chat_history = load_chat_history()

    if username not in chat_history:
        chat_history[username] = []

    if request.method == 'POST':
        user_message = request.form['message']

        if not chat_history[username]:  # If chat history is empty, show welcome message
            bot_response = "Welcome my friend. What do you do today?"
            chat_history[username].append({'role': 'bot', 'content': bot_response})

        # Continue with model-based conversation
        enhanced_input = f"{user_message} Response me like you are a cat and my best friend and call me with names like a best friend. make a response concise."

        conversation_history = [{"role": "user", "content": enhanced_input}]

        response_content = ""
        for message in client.chat_completion(
            messages=conversation_history,
            max_tokens=500,
            stream=True,
        ):
            response_content += message.choices[0].delta.content

        final_response = enhance_response(response_content)
        bot_response = final_response
        chat_history[username].append({'role': 'user', 'content': user_message})
        chat_history[username].append({'role': 'bot', 'content': bot_response})

        save_chat_history(chat_history)
        return jsonify({'response': bot_response})

    # Ensure the welcome message is added if the user is accessing the chat for the first time
    if not chat_history[username]:
        initial_bot_message = "Welcome my friend. What do you do today?"
        chat_history[username].append({'role': 'bot', 'content': initial_bot_message})
        save_chat_history(chat_history)

    user_chat_history = chat_history.get(username, [])

    return render_template('chat.html', chat_history=user_chat_history)

def enhance_response(response):
    if "I'm just a chatbot" in response or "I can't physically" in response or "I am unable to" in response:
        response = response.replace("I'm just a chatbot", "I’m here with you, just like your real cat friend would be.")
        response = response.replace("I can't physically", "Imagine I’m purring right beside you, making you feel relaxed.")
        response = response.replace("I am unable to", "Picture me curling up on your lap, making you feel calm and happy.")
    return response
