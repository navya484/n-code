import mysql.connector
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from datetime import datetime
from werkzeug.security import check_password_hash


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flash messages

# Database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",           # Replace with your database host
        user="root",       # Replace with your database username
        password="root123",   # Replace with your database password
        database="empower_women"    # Replace with your database name
    )
    return connection

# Sample data for available initiatives and events
initiatives = [
    {"name": "Leadership Workshops for Women", "description": "Join our workshops designed to empower women leaders with the skills to thrive in any professional setting."},
    {"name": "Entrepreneurship Bootcamp", "description": "Develop your entrepreneurial skills and learn how to start and grow your own business in a supportive environment."},
    {"name": "Women in Tech Networking", "description": "A networking event connecting women working in technology, fostering collaboration and mentorship opportunities."}
]

events = [
    {"name": "Global Women Entrepreneurship Summit", "description": "A global summit bringing together female entrepreneurs from all over the world to share insights, strategies, and success stories."},
    {"name": "Women Empowerment Gala", "description": "An evening to celebrate the achievements of women in various fields, with keynote speakers and awards."},
    {"name": "Career Development Workshop", "description": "This workshop focuses on career growth strategies, CV building, and interview preparation to help women succeed in their careers."}
]

user_data = {
    "joined_initiatives": [],
    "joined_events": [],
    "joined_mentorships": []
}

@app.route("/emp_initiative")
def emp_initiative():
    return render_template(
        'emp_initiative.html',
        initiatives=initiatives,
        events=events,
        joined_initiatives=user_data["joined_initiatives"],
        joined_events=user_data["joined_events"]
    )

@app.route("/join_initiative", methods=["POST"])
def join_initiative():
    initiative_name = request.form.get("initiative_name")
    if initiative_name and initiative_name not in user_data["joined_initiatives"]:
        user_data["joined_initiatives"].append(initiative_name)
        flash(f"You have joined the initiative: {initiative_name}.", "success")
    return redirect(url_for("emp_initiative"))

@app.route("/join_event", methods=["POST"])
def join_event():
    event_name = request.form.get("event_name")
    if event_name and event_name not in user_data["joined_events"]:
        user_data["joined_events"].append(event_name)
        flash(f"You have joined the event: {event_name}.", "success")
    return redirect(url_for("emp_initiative"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query to check if the user exists in the database
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()  # Get the first result (if any)

        cursor.close()
        conn.close()

        # If the user exists and the password matches
        if user and check_password_hash(user['password'], password):
            session["logged_in"] = True
            session["username"] = username
            flash("Login successful!", "success")
            return redirect("index.html")  # Redirect to the homepage (index.html)
        else:
            flash("Invalid username or password.", "error")
            return redirect("login.html")  # Stay on the login page if credentials are incorrect

    return render_template("login.html")

# Registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Collect form data
        user_id = request.form["userid"]
        name = request.form["name"]
        password = request.form["password"]
        skills = request.form["skills"]
        user_about = request.form["user_about"]
        business_details = request.form["business_details"]
        achievement = request.form["achievement"]
        contact_info = request.form["contact_info"]
        industry = request.form["industry"]
        social_media = request.form["social_media"]

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user already exists
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("User ID already exists. Please choose another one.", "error")
            return redirect("/register")

        # Insert the new user data into the database
        cursor.execute(
            """INSERT INTO users (user_id, name, password, skills, user_about, business_details, 
                                   achievement, contact_info, industry, social_media) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (user_id, name, hashed_password, skills, user_about, business_details, achievement, 
             contact_info, industry, social_media)
        )

        # Commit the transaction
        conn.commit()

        cursor.close()
        conn.close()

        flash("Registration successful! You can now log in.", "success")
        return redirect("/login")

    return render_template("register.html")

@app.route("/")
def index():
    # Display a personalized greeting if logged in
    username = session.get("username")
    return render_template("index.html", username=username)


@app.route('/startup_networking')
def startups_networking():
    # Example startups and boards data
    startups = [
        {"name": "Tech Innovators", "description": "A tech startup focusing on AI-driven solutions for healthcare."},
        {"name": "Green Solutions", "description": "A sustainability startup aiming to revolutionize waste management."},
        {"name": "HealthCare 360", "description": "Startup focused on creating innovative healthcare applications."}
    ]
    
    boards = [
        {"name": "Tech Innovators Board", "description": "Collaborate with professionals in the tech field to drive innovation."},
        {"name": "Sustainability Innovators Board", "description": "A place for sustainability experts to collaborate on projects."}
    ]

    return render_template('startup_networking.html')



@app.route("/userprofile")
def user_profile():
    user = {
        'profile_picture': '/static/images/profile.jpg',
        'name': 'Jane Doe',
        'about': 'Passionate about empowering women entrepreneurs and inspiring leadership.',
        'skills': ['Leadership', 'Business Strategy', 'Marketing', 'Public Speaking'],
        'business_details': 'Founder of XYZ Ventures, a company focused on sustainable business practices.',
        'achievements': ['Women in Tech Award 2024', 'Best Startup Founder 2023'],
        'contact_info': {'email': 'jane.doe@example.com', 'phone': '123-456-7890'},
        'social_links': [
            'https://www.linkedin.com/in/jane-doe',
            'https://twitter.com/janedoe',
            'https://www.instagram.com/janedoe'
        ]
    }
    return render_template('userprofile.html', user=user)

@app.route("/sponsorship_finder", methods=["GET", "POST"])
def sponsorship_finder():
    if request.method == "POST":
        industry = request.form.get("industry")
        region = request.form.get("region")
        funding_stage = request.form.get("funding_stage")
        goals = request.form.get("goals")
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM sponsorships WHERE industry=%s AND region=%s AND funding_stage=%s",
            (industry, region, funding_stage)
        )
        matched_sponsors = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({"matches": matched_sponsors})
    
    return render_template("sponsorship_finder.html")

# Sample events data
events = [
    {
        "id": 1,
        "name": "Women in Tech Networking",
        "description": "Connect with women leaders in technology for collaboration and mentorship.",
        "date": "2025-02-10",
        "location": "San Francisco",
    },
    {
        "id": 2,
        "name": "Global Women Entrepreneurship Summit",
        "description": "A global summit for women entrepreneurs to share strategies and insights.",
        "date": "2025-03-15",
        "location": "Online",
    },
    {
        "id": 3,
        "name": "Women Empowerment Gala",
        "description": "Celebrate the achievements of women in various fields with awards and keynote speakers.",
        "date": "2025-04-20",
        "location": "New York",
    },
    {
        "id": 4,
        "name": "Sustainable Startups Networking",
        "description": "Meet and network with entrepreneurs focusing on sustainable business practices.",
        "date": "2025-02-25",
        "location": "London",
    },
    {
        "id": 5,
        "name": "Career Development Workshop",
        "description": "Work on career strategies, CV building, and interview preparation for professional success.",
        "date": "2025-01-30",
        "location": "Online",
    },
]

@app.route("/events")
def events_page():
    return render_template("events.html")

@app.route("/api/events")
def get_events():
    """Fetch events dynamically based on query parameters."""
    keyword = request.args.get("keyword", "").lower()
    location = request.args.get("location", "").lower()
    date = request.args.get("date", "")

    # Filter events based on user input
    filtered_events = events
    if keyword:
        filtered_events = [
            event for event in filtered_events if keyword in event["name"].lower() or keyword in event["description"].lower()
        ]
    if location:
        filtered_events = [
            event for event in filtered_events if location in event["location"].lower()
        ]
    if date:
        try:
            user_date = datetime.strptime(date, "%Y-%m-%d").date()
            filtered_events = [
                event
                for event in filtered_events
                if datetime.strptime(event["date"], "%Y-%m-%d").date() >= user_date
            ]
        except ValueError:
            return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    return jsonify(filtered_events)

@app.route('/mentorship')
def mentorship():
    # Connect to the database and fetch mentorship programs
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Correct table name is 'mentorships'
    cursor.execute("SELECT * FROM mentorships")
    mentorship_programs = cursor.fetchall()  # Fetch all mentorships
    
    cursor.close()
    connection.close()

    # Render the template with dynamic data
    return render_template('mentorship.html', mentorship_programs=mentorship_programs)

@app.route('/startup_networking')
def startup_networking():
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)  # Use dictionary=True for easier access to column names
    cursor.execute("SELECT * FROM startups")
    startups = cursor.fetchall()
    cursor.close()
    connection.close()

    # Pass the startups data to the template
    return render_template('startup_networking.html', startups=startups)

if __name__ == "__main__":
    app.run(debug=True)
