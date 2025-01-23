from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import requests
import math
from flask_session import Session
import sqlite3
from flask import Flask, g
from functools import wraps
from config import DevelopmentConfig  # or ProductionConfig for production

# Configuring Flask to use the sqlite3 database. used Claude AI to build out the code (STILL IN PROGRESS)

app = Flask(__name__)

# Load configuration
app.config.from_object(DevelopmentConfig)  # Change to ProductionConfig for production

# Initialize Flask-Session
Session(app)

# Source: https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/

def login_required(f):
    """
    Decorate routes to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if 'user_id' is in session (indicating user is logged in)
        if session.get("user_id") is None:
            return redirect("/login")  # Redirect to the login page if not logged in
        return f(*args, **kwargs)  # Proceed with the original route if logged in

    return decorated_function

# Database helper functions
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Used Gemini AI to build out fetch random poetry route and search poetry route
# FETCH RANDOM POETRY
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
     # Check if the user is logged in by verifying if 'user_id' is in the session
    if 'user_id' not in session:
        return redirect(url_for('login'))  # If not logged in, redirect to the login page

    random_poem = None
    try:
        # Make a request to get a random poem
        response = requests.get('https://poetrydb.org/random/1')
        if response.status_code == 200:
            poetry_data = response.json()[0]

            # Filter for poems with 10 lines or fewer
            if len(poetry_data.get('lines', [])) <= 10:
                random_poem = {
                    'title': poetry_data.get('title', 'Unknown Title'),
                    'author': poetry_data.get('author', 'Unknown Author'),
                    'lines': poetry_data.get('lines', ['No lines available'])
                }
            else:
                # If the poem is too long, return to index to try again
                return index()

    except Exception as e:
        print(f"Error fetching random poem: {e}")

    # Render the page with the poem (or None if an error occurred)
    return render_template('index.html', random_poem=random_poem)

# SEARCH POETRY
# Function to search poetry by title or author
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    search_query = request.form.get('search_query') or request.args.get('search_query')
    page = request.args.get('page', 1, type=int)  # Get page number, default to 1
    poems_per_page = 1  # Number of poems per page

    if not search_query:
        return render_template('index.html', error="Please enter a search term")
    

    try:
        # Search by author name
        response = requests.get(f'https://poetrydb.org/author/{search_query}')
        
        if response.status_code == 200:
            poems = response.json()
            
            if not poems:
                # If no poems found by author, try searching by title
                title_response = requests.get(f'https://poetrydb.org/title/{search_query}')
                if title_response.status_code == 200:
                    poems = title_response.json()
            
            # Pagination logic
            total_poems = len(poems)
            total_pages = math.ceil(total_poems / poems_per_page)
            
            # Slice the poems for the current page
            start_idx = (page - 1) * poems_per_page
            end_idx = start_idx + poems_per_page
            paginated_poems = poems[start_idx:end_idx]
            
            return render_template('search_results.html',
                                   poems=paginated_poems,
                                   search_query=search_query,
                                   page=page,
                                   total_pages=total_pages)
        else:
            return render_template('index.html', error="Error fetching poems from Poetry DB")
    
    except requests.RequestException as e:
        return render_template('index.html', error=f"Network error: {str(e)}")

# USER AUTHENTICATION
# Source: https://medium.com/@mosininamdar/how-to-make-a-signup-login-and-logout-route-in-flask-app-in-5-minutes-f5c771f7a8f3
#         https://www.freecodecamp.org/news/how-to-authenticate-users-in-flask/
#         https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login
    
# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login User"""

     # Forget any user_id
    session.clear()

    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        # Connect to the database and validate credentials
        conn = sqlite3.connect('poema.db')
        db = conn.cursor()
        db.execute("SELECT id, username, password_hash FROM users WHERE username = ?", (username,))
        user = db.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):  # Check if password matches
            session['user_id'] = user[0]  # Store user ID in session
            session['username'] = user[1]  # Store username in session (optional)
            return redirect(url_for('index'))  # Redirect to the index (home) page after login
        else:
            return render_template("login.html", message="Invalid credentials. Please try again.")

    return render_template("login.html")

# REGISTRATION
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register User and Auto Login"""
    
    if request.method == "POST":
        # Validate form data
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        if not username or not password:
            return render_template("register.html", message="Username and password are required.")
        
        try:
            # Connect to database
            conn = sqlite3.connect('poema.db')
            db = conn.cursor()
            
            # Check if username already exists
            db.execute("SELECT username FROM users WHERE username = ?", (username,))
            if db.fetchone():
                return render_template("register.html", message="Username already exists.")
            
            # Hash the password
            hashed_password = generate_password_hash(password)
            
            # Insert new user
            db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            
            # Get the user's ID for the session
            db.execute("SELECT id FROM users WHERE username = ?", (username,))
            user_id = db.fetchone()[0]
            
            # Close database connection
            db.close()
            conn.close()
            
            # Log the user in by storing user_id in session
            session["user_id"] = user_id
            session["username"] = username
            
            # Redirect to home page (or wherever you want users to go after registration)
            return redirect("/")
            
        except sqlite3.Error as e:
            # Handle database errors
            return render_template("register.html", message="Registration failed. Please try again.")
            
    return render_template("register.html")

# LOGOUT
@app.route("/logout")
def logout():
    # Clear the session
    session.clear()
    return redirect("/")

# CHANGE PASSWORD
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
  """Change user's password"""

  if request.method == 'POST':
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_new_password = request.form.get("confirm_new_password")

    # Get user ID from session
    user_id = session.get('user_id')

    # Validate form data
    if not current_password or not new_password or not confirm_new_password:
      return render_template("change_password.html", message="All fields are required.")

    if new_password != confirm_new_password:
      return render_template("change_password.html", message="New passwords do not match.")

    # Connect to database and fetch user by ID
    conn = sqlite3.connect('poema.db')
    db = conn.cursor()
    db.execute("SELECT id, password_hash FROM users WHERE id = ?", (user_id,))
    user = db.fetchone()
    conn.close()

    # Check if user exists
    if not user:
      return render_template("change_password.html", message="Invalid user.")

    # Validate current password
    if not check_password_hash(user[1], current_password):
      return render_template("change_password.html", message="Incorrect current password.")

    # Hash the new password
    hashed_password = generate_password_hash(new_password)

    # Update user's password in database
    conn = sqlite3.connect('poema.db')
    db = conn.cursor()
    db.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed_password, user_id))
    conn.commit()
    conn.close()

    return render_template("login.html", message="Password changed successfully! Please log in with your new password.", message_type="success")
     # Log user out and redirect user to the login page
    logout()
    

    return redirect("/")

  return render_template("change_password.html")

# FAVES SECTION 
# Used Claude AI, Gemini AI to build out the save poem, unsave poem and get saved poems routes

# Save Poem Route (POST)
# Add this new route for unsaving poems
@app.route('/unsave-poem', methods=['POST'])
@login_required
def unsave_poem():
    # Extract data from the request
    title = request.form.get('title')
    user_id = session.get('user_id')
    
    if not title or not user_id:
        return jsonify({"error": "Missing required data"}), 400
        
    try:
        conn = sqlite3.connect('poema.db')
        db = conn.cursor()
        
        # Delete the poem from saved_poems
        db.execute('''
            DELETE FROM saved_poems 
            WHERE user_id = ? AND title = ?
        ''', (user_id, title))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Poem removed from favorites"}), 200
        
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

# Modify your existing save-poem route to return JSON
@app.route('/save-poem', methods=['POST'])
@login_required
def save_poem():
    title = request.form.get('title')
    author = request.form.get('author')
    text = request.form.get('text')
    user_id = session.get('user_id')
    
    if not title or not author or not text:
        return jsonify({"error": "Title, author, and text are required"}), 400
        
    try:
        conn = sqlite3.connect('poema.db')
        db = conn.cursor()
        
        # Check if poem is already saved
        db.execute('''
            SELECT id FROM saved_poems 
            WHERE user_id = ? AND title = ?
        ''', (user_id, title))
        
        existing_poem = db.fetchone()
        
        if existing_poem:
            return jsonify({"error": "Poem already saved"}), 409
            
        db.execute('''
            INSERT INTO saved_poems (user_id, title, author, text)
            VALUES (?, ?, ?, ?)
        ''', (user_id, title, author, text))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Poem saved successfully"}), 200
        
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500

# Get Saved Poems Route (GET)
@app.route('/saved-poems', methods=['GET'])
@login_required
def saved_poems():
    user_id = session.get('user_id')
    page = request.args.get('page', 1, type=int)  # Get current page from query parameters
    poems_per_page = 1  # Number of poems per page

    try:
        conn = sqlite3.connect('poema.db')
        conn.row_factory = sqlite3.Row
        db = conn.cursor()

        # Count the total number of saved poems for the user
        db.execute('''SELECT COUNT(*) FROM saved_poems WHERE user_id = ?''', (user_id,))
        total_poems = db.fetchone()[0]
        total_pages = (total_poems // poems_per_page) + (1 if total_poems % poems_per_page else 0)

        # Query to get the saved poems for the current page
        db.execute('''
            SELECT id, title, text, author
            FROM saved_poems
            WHERE user_id = ?
            LIMIT ? OFFSET ?
        ''', (user_id, poems_per_page, (page - 1) * poems_per_page))
        
        poems = db.fetchall()
        conn.close()

        # Convert rows to dictionaries for easier template handling
        poem_list = [dict(row) for row in poems]

        return render_template(
            'faves.html',
            saved_poems=poem_list,
            page=page,
            total_pages=total_pages
        )

    except sqlite3.Error as e:
        flash(f"Error retrieving saved poems: {str(e)}", "error")
        return redirect(url_for('index'))