import os
import gzip
from io import BytesIO
import threading
from flask import Flask, render_template, request, redirect, flash, url_for
import pymysql
from pymysql import Error

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Sai#0709") # Update this if needed (e.g., "admin123")
DB_NAME = os.environ.get("DB_NAME", "portfolio")

# Initialize Flask App
app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')
app.secret_key = 'super-secret-portfolio-key'

# Thread-local storage for persistent database connections
_thread_local = threading.local()

def get_db_connection():
    """Establish or retrieve a thread-safe persistent connection to the MySQL database."""
    connection = getattr(_thread_local, 'db_connection', None)
    try:
        if connection is None or not connection.open:
            connection = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            _thread_local.db_connection = connection
        else:
            connection.ping(reconnect=True)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Caching & Gzip Compression Middleware
@app.after_request
def optimize_response(response):
    # 1. Add Browser Caching for static assets (max-age = 30 days)
    if (request.path.startswith('/static/') or 
        request.path.endswith('.css') or 
        request.path.endswith('.jpg') or 
        request.path.endswith('.png') or 
        request.path.endswith('.svg') or 
        request.path.endswith('.js')):
        response.headers['Cache-Control'] = 'public, max-age=2592000' # 30 days
    else:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'

    # 2. Gzip Compression for text/SVG responses
    accept_encoding = request.headers.get('Accept-Encoding', '')
    if 'gzip' not in accept_encoding.lower():
        return response

    if response.status_code < 200 or response.status_code >= 300 or 'Content-Encoding' in response.headers:
        return response

    content_type = response.content_type or ''
    if 'text/' in content_type or 'javascript' in content_type or 'json' in content_type or 'image/svg+xml' in content_type:
        response.direct_passthrough = False
        data = response.get_data()
        
        gzip_buffer = BytesIO()
        with gzip.GzipFile(mode='wb', fileobj=gzip_buffer) as gzip_file:
            gzip_file.write(data)
        
        response.set_data(gzip_buffer.getvalue())
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Length'] = len(response.get_data())
        response.headers['Vary'] = 'Accept-Encoding'

    return response

# Global Error Handler for MySQL connection failures
@app.errorhandler(500)
def internal_server_error(e):
    return "An internal error occurred. Please check your MySQL database connection and credentials in app.py.", 500

@app.route('/')
@app.route('/Home.html')
@app.route('/Akhila.html')
def index():
    return render_template('Home.html')


@app.route('/About.html')
def about():
    return render_template('About.html')

@app.route('/Contact.html')
def contact():
    return render_template('Contact.html')

@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    if request.method == 'POST':
        # Get data from the form
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject') # This will be None if from Contact.html
        budget = request.form.get('budget')   # This will be None if from Contact.html
        message = request.form.get('message')
        
        # Connect to Database and Insert Data
        conn = get_db_connection()
        if not conn:
            flash("Database connection failed. Please ensure MySQL is running and credentials are correct.", "error")
            return redirect('/Contact.html')

        try:
            cursor = conn.cursor()
            query = """INSERT INTO messages (name, email, subject, budget, message) 
                       VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, (name, email, subject, budget, message))
            conn.commit()
            
            # Use javascript alert and redirect backwards since this form exists on multiple pages
            return f'''
                <script>
                    alert("Thank you, {name}! Your message has been sent successfully.");
                    window.history.back();
                </script>
            '''
        except Error as e:
            print(f"Failed to insert record: {e}")
            return f'''
                <script>
                    alert("There was an error sending your message. Please try again later.");
                    window.history.back();
                </script>
            '''
        finally:
            if 'cursor' in locals():
                cursor.close()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
