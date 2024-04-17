import socket
import threading
import hashlib
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import urllib.parse


# Database connection parameters - replace these with your actual database details
DB_HOST = "localhost"
DB_NAME = "exam"
DB_USER = "postgres"
DB_PASS = "root"

# HTML templates for login, registration, budget, and expenses pages

# Login template


# Registration template
login_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        /* Common styles */
        body {
            font-family: Arial, sans-serif;
        }

        .container {
            margin-top: 50px;
        }

        .text-center {
            text-align: center;
        }

        /* Form styles */
        .form-group {
            margin-bottom: 20px;
        }

        .form-control {
            width: 100%;
        }

        .btn-primary {
            width: 100%;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2 class="text-center">Login</h2>
        <form action="/login" method="post">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" class="form-control" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary">Login</button>
        </form>
        <div class="text-center">
            <p>Not registered? <a href="/register">Register here</a></p>
        </div>
    </div>
</body>
</html>
'''

# Registration template
register_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        /* Common styles */
        body {
            font-family: Arial, sans-serif;
        }

        .container {
            margin-top: 50px;
        }

        .text-center {
            text-align: center;
        }

        /* Form styles */
        .form-group {
            margin-bottom: 20px;
        }

        .form-control {
            width: 100%;
        }

        .btn-primary {
            width: 100%;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2 class="text-center">Register</h2>
        <form action="/register" method="post">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" class="form-control" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" class="form-control" id="password" name="password" required>
            </div>
            <button type="submit" class="btn btn-primary">Register</button>
        </form>
    </div>
</body>
</html>
'''
# Course creation template
create_course_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Course</title>
</head>
<body>
    <h1>Create Course</h1>
    <form action="/create_course" method="post">
        <label for="course_name">Course Name:</label>
        <input type="text" id="course_name" name="course_name" required><br><br>
        <label for="description">Description:</label><br>
        <textarea id="description" name="description" rows="4" cols="50"></textarea><br><br>
        <button type="submit">Create Course</button>
    </form>
</body>
</html>
'''

# Course catalog template
course_catalog_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Course Catalog</title>
</head>
<body>
    <h1>Course Catalog</h1>
    <ul>
        {% for course in courses %}
            <li>{{ course.name }} - {{ course.description }} <a href="/enroll/{{ course.id }}">Enroll</a></li>
        {% endfor %}
    </ul>
</body>
</html>
'''

# Student dashboard template
student_dashboard_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Dashboard</title>
</head>
<body>
    <h1>Welcome, {{ username }}!</h1>
    <h2>Your Courses:</h2>
    <ul>
        {% for course in courses %}
            <li>{{ course.name }} - {{ course.description }} <a href="/drop/{{ course.id }}">Drop</a></li>
        {% endfor %}
    </ul>
</body>
</html>
'''


def create_course(course_name, description):
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cur = conn.cursor()

        # Execute SQL to insert a new course into the courses table
        cur.execute("INSERT INTO courses (course_name, description) VALUES (%s, %s)", (course_name, description))
        
        # Commit the transaction
        conn.commit()
        print("Course created successfully.")

    except psycopg2.Error as e:
        print("Error occurred during course creation:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def enroll_in_course(student_id, course_id):
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cur = conn.cursor()

        # Execute SQL to insert a new enrollment into the enrollments table
        cur.execute("INSERT INTO enrollments (user_id, course_id) VALUES (%s, %s)", (student_id, course_id))
        
        # Commit the transaction
        conn.commit()
        print("Enrollment successful.")

    except psycopg2.Error as e:
        print("Error occurred during enrollment:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def drop_course(student_id, course_id):
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cur = conn.cursor()

        # Execute SQL to delete the enrollment from the enrollments table
        cur.execute("DELETE FROM enrollments WHERE user_id = %s AND course_id = %s", (student_id, course_id))
        
        # Commit the transaction
        conn.commit()
        print("Course dropped successfully.")

    except psycopg2.Error as e:
        print("Error occurred during course drop:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Database connection initialization and functions

def connect_to_db():
    try:
        return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    except Exception as e:
        logging.error(f"Error occurred during database connection: {e}")

def create_user(username, password):
    conn = connect_to_db()
    if conn:
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cur = conn.cursor()
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s);", (username, hashed_password))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Error occurred during user registration: {e}")
            return False
    else:
        return False

def get_user(username):
    conn = connect_to_db()
    if conn:
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
            user = cur.fetchone()
            cur.close()
            conn.close()
            return user
        except Exception as e:
            logging.error(f"Error occurred while fetching user: {e}")
            return None
    else:
        return None




def handle_client(client_socket):
    request_data = client_socket.recv(1024).decode('utf-8')
    if request_data:
        request_lines = request_data.split('\n')
        request_method = request_lines[0].split(' ')[0]
        request_path = request_lines[0].split(' ')[1]

        username = None
        for line in request_lines:
            if "username=" in line:
                username = line.split('=')[1].strip()
                break

        if request_method == 'GET':
            if request_path == '/':
                response = "HTTP/1.1 302 Found\nLocation: /login\n\n"
            elif request_path == '/login':
                response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + login_template
            elif request_path == '/register':
                response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n" + register_template
            elif request_path == '/create_course':
                response == "HTTP/1.1 200 OK\nContent-Type: text/html\n\n"+ create_course_template
        elif request_method == 'POST':
            if request_path == '/login':
                response = handle_login(client_socket, request_data)
            elif request_path == '/register':
                response = handle_register(client_socket, request_data)
            elif request_path == '/create_course': 
                response = handle_create_course(client_socket, request_data)  
        else:
            response = "HTTP/1.1 405 Method Not Allowed\n\n405 Method Not Allowed"

        client_socket.sendall(response.encode('utf-8'))
        client_socket.close()


def handle_create_course(client_socket, request_data):
    # Extract course name and description from request data
    request_lines = request_data.split('\n')
    form_data = request_lines[-1]
    parsed_form_data = urllib.parse.parse_qs(form_data)
    
    # Check if both course name and description are present in the form data
    if 'course_name' in parsed_form_data and 'description' in parsed_form_data:
        course_name = parsed_form_data['course_name'][0]
        description = parsed_form_data['description'][0]

        # Call the create_course function
        create_course(course_name, description)

        # Construct HTML response - for simplicity, just redirect back to create course page
        response = "HTTP/1.1 302 Found\nLocation: /create_course\n\n"
    else:
        # If either course name or description is missing, return a bad request response
        response = "HTTP/1.1 400 Bad Request\nContent-Type: text/html\n\nMissing course name or description."

    client_socket.sendall(response.encode('utf-8'))
    client_socket.close()


def handle_login(client_socket, request_data):
    # Extract username and password from request data
    request_lines = request_data.split('\n')
    form_data = request_lines[-1]
    username = form_data.split('&')[0].split('=')[1]
    password = form_data.split('&')[1].split('=')[1]

    # Validate username and password
    user = get_user(username)
    if user and hashlib.sha256(password.encode()).hexdigest() == user['password']:
        # Construct HTML response
        response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n"
        response += "<h1>Login Successful</h1>"
        response += "<p>Welcome</p>"
        response += "<p><a href='/create_course'>dashboard</a></p>"
    else:
        # Return unauthorized message if login fails
        response = "HTTP/1.1 401 Unauthorized\nContent-Type: text/html\n\nInvalid username or password."

    client_socket.sendall(response.encode('utf-8'))
    client_socket.close()

def handle_register(client_socket, request_data):
    # Extract username and password from request data
    request_lines = request_data.split('\n')
    form_data = request_lines[-1]
    username = form_data.split('&')[0].split('=')[1]
    password = form_data.split('&')[1].split('=')[1]

    # Create new user
    if create_user(username, password):
        return "HTTP/1.1 302 Found\nLocation: /login\n\n"
    else:
        return "HTTP/1.1 500 Internal Server Error\nContent-Type: text/html\n\nFailed to register user."


# Main server function
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('127.0.0.1', 8086))
    server_socket.listen(5)

    logging.info("Server started. Listening on port 8086...")
    print("Server is running at http://127.0.0.1:8086/")

    while True:
        client_socket, addr = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    start_server()
