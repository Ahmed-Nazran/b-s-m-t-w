from flask import Flask, request, redirect, url_for, render_template_string, session
from datetime import datetime
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# Simulate environment variable storage
USERS_ENV = "USERS_DATA"
POSTS_ENV = "POSTS_DATA"

def get_env_data(env):
    data = os.getenv(env, '{}')
    return json.loads(data)

def set_env_data(env, data):
    os.environ[env] = json.dumps(data)

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    posts = get_env_data(POSTS_ENV)
    posts_html = "<ul>"
    for post in posts:
        posts_html += f"<li>{post['content']} - {post['date']} by {post['username']}</li>"
    posts_html += "</ul>"
    return render_template_string('''
        <h1>Welcome {{ user }}</h1>
        <form action="{{ url_for('logout') }}" method="post">
            <button type="submit">Logout</button>
        </form>
        <form action="{{ url_for('create_post') }}" method="post">
            <textarea name="content" placeholder="Write your post"></textarea><br>
            <button type="submit">Post</button>
        </form>
        <h2>Posts:</h2>
        ''' + posts_html)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        users = get_env_data(USERS_ENV)
        
        if email in users:
            return "Email already registered."
        
        users[email] = {
            'username': username,
            'password': generate_password_hash(password)
        }
        set_env_data(USERS_ENV, users)
        return redirect(url_for('login'))
    
    return '''
        <form method="post">
            Email: <input type="email" name="email"><br>
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <button type="submit">Sign Up</button>
        </form>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = get_env_data(USERS_ENV)
        
        if email not in users or not check_password_hash(users[email]['password'], password):
            return "Invalid email or password."
        
        session['user'] = users[email]['username']
        return redirect(url_for('home'))
    
    return '''
        <form method="post">
            Email: <input type="email" name="email"><br>
            Password: <input type="password" name="password"><br>
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/create_post', methods=['POST'])
def create_post():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    content = request.form['content']
    posts = get_env_data(POSTS_ENV)
    
    new_post = {
        'content': content,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'username': session['user']
    }
    posts.append(new_post)
    set_env_data(POSTS_ENV, posts)
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
