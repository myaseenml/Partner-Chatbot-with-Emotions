from flask import Flask, request, redirect, session, url_for, render_template
from chat import chat_bp
from payments import payments_bp
from about import about_bp
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

USER_DATA_FILE = 'users.json'

# Ensure the JSON files exist
if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump({}, f)


# Load users data
def load_users():
    with open(USER_DATA_FILE, 'r') as f:
        return json.load(f)


# Save users data
def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f)


# User login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()
        user = users.get(username)

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = username
            return redirect(url_for('chat_bp.chat'))
        else:
            return 'Invalid username or password'
    
    return render_template('login.html')

# User registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        users = load_users()
        if username in users:
            return 'Username already taken'

        user_id = len(users) + 1
        users[username] = {'id': user_id, 'password': password}
        save_users(users)

        return redirect(url_for('login'))
    
    return render_template('register.html')


# Register Blueprints
app.register_blueprint(chat_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(about_bp)

if __name__ == "__main__":
    app.run(debug=True)
