from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)

DATABASE = "placement_tracker.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    # ========================================================
    # SKILLS TABLE
    # ========================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # ========================================================
    # APPLICATIONS TABLE
    # ========================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL,
            application_date TEXT,
            deadline TEXT
        )
    """)

    # Add deadline to an older database that does not have it yet.
    columns = connection.execute(
        "PRAGMA table_info(applications)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    if "deadline" not in column_names:
        connection.execute(
            "ALTER TABLE applications ADD COLUMN deadline TEXT"
        )

    # ========================================================
    # DSA TABLE
    # ========================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS dsa_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # ========================================================
    # APTITUDE TABLE
    # ========================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS aptitude_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # ========================================================
    # REASONING TABLE
    # ========================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reasoning_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # ========================================================
    # STUDENT PROFILE TABLE
    # ========================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS student_profile (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            phone TEXT,
            college TEXT,
            branch TEXT,
            graduation_year TEXT,
            career_goal TEXT
        )
    """)

    # ========================================================
    # CERTIFICATIONS TABLE
    # ========================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            organization TEXT,
            date TEXT,
            credential TEXT
        )
    """)

    # ========================================================
    # PROJECTS TABLE
    # ========================================================

    connection.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            technologies TEXT,
            status TEXT,
            github_link TEXT
        )
    """)

    connection.commit()
    return connection


# ============================================================
# HELPER: CALCULATE DEADLINE STATUS
# ============================================================

def get_deadline_info(deadline):
    if not deadline:
        return "No Deadline", None

    try:
        deadline_date = date.fromisoformat(deadline)
    except ValueError:
        return "Invalid Date", None

    days_left = (deadline_date - date.today()).days

    if days_left < 0:
        return "Deadline Passed", days_left

    if days_left <= 3:
        return "Due Soon", days_left

    return "Upcoming", days_left


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():
    connection = get_db_connection()

    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    skills = connection.execute(
        "SELECT * FROM skills"
    ).fetchall()

    total_skills = len(skills)
    completed_skills = sum(
        1 for skill in skills
        if skill["status"] == "Completed"
    )

    skill_progress = (
        completed_skills / total_skills * 100
        if total_skills > 0 else 0
    )

    # --------------------------------------------------------
    # DSA
    # --------------------------------------------------------

    dsa_topics = connection.execute(
        "SELECT * FROM dsa_topics"
    ).fetchall()

    total_dsa = len(dsa_topics)
    completed_dsa = sum(
        1 for topic in dsa_topics
        if topic["status"] == "Completed"
    )

    dsa_progress = (
        completed_dsa / total_dsa * 100
        if total_dsa > 0 else 0
    )

    # --------------------------------------------------------
    # APTITUDE
    # --------------------------------------------------------

    aptitude_topics = connection.execute(
        "SELECT * FROM aptitude_topics"
    ).fetchall()

    total_aptitude = len(aptitude_topics)
    completed_aptitude = sum(
        1 for topic in aptitude_topics
        if topic["status"] == "Completed"
    )

    aptitude_progress = (
        completed_aptitude / total_aptitude * 100
        if total_aptitude > 0 else 0
    )

    # --------------------------------------------------------
    # REASONING
    # --------------------------------------------------------

    reasoning_topics = connection.execute(
        "SELECT * FROM reasoning_topics"
    ).fetchall()

    total_reasoning = len(reasoning_topics)
    completed_reasoning = sum(
        1 for topic in reasoning_topics
        if topic["status"] == "Completed"
    )

    reasoning_progress = (
        completed_reasoning / total_reasoning * 100
        if total_reasoning > 0 else 0
    )

    # --------------------------------------------------------
    # APPLICATIONS + DEADLINES
    # --------------------------------------------------------

    applications = connection.execute(
        "SELECT * FROM applications"
    ).fetchall()

    total_applications = len(applications)
    interview_applications = 0
    selected_applications = 0
    rejected_applications = 0
    upcoming_deadlines = 0
    due_soon = 0
    passed_deadlines = 0

    for application in applications:
        if application["status"] == "Interview":
            interview_applications += 1
        elif application["status"] == "Selected":
            selected_applications += 1
        elif application["status"] == "Rejected":
            rejected_applications += 1

        deadline_status, _ = get_deadline_info(
            application["deadline"]
        )

        if deadline_status == "Upcoming":
            upcoming_deadlines += 1
        elif deadline_status == "Due Soon":
            due_soon += 1
        elif deadline_status == "Deadline Passed":
            passed_deadlines += 1

    # --------------------------------------------------------
    # CERTIFICATIONS
    # --------------------------------------------------------

    total_certifications = connection.execute(
        "SELECT COUNT(*) FROM certifications"
    ).fetchone()[0]

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    total_projects = connection.execute(
        "SELECT COUNT(*) FROM projects"
    ).fetchone()[0]

    connection.close()

    return render_template(
        "dashboard.html",
        total_skills=total_skills,
        completed_skills=completed_skills,
        skill_progress=round(skill_progress, 2),
        total_dsa=total_dsa,
        completed_dsa=completed_dsa,
        dsa_progress=round(dsa_progress, 2),
        total_aptitude=total_aptitude,
        completed_aptitude=completed_aptitude,
        aptitude_progress=round(aptitude_progress, 2),
        total_reasoning=total_reasoning,
        completed_reasoning=completed_reasoning,
        reasoning_progress=round(reasoning_progress, 2),
        total_applications=total_applications,
        interview_applications=interview_applications,
        selected_applications=selected_applications,
        rejected_applications=rejected_applications,
        upcoming_deadlines=upcoming_deadlines,
        due_soon=due_soon,
        passed_deadlines=passed_deadlines,
        total_certifications=total_certifications,
        total_projects=total_projects
    )


# ============================================================
# SKILLS
# ============================================================

@app.route("/skills")
def skills():
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()

    connection = get_db_connection()

    query = "SELECT * FROM skills WHERE 1 = 1"
    parameters = []

    if search:
        query += " AND name LIKE ?"
        parameters.append(f"%{search}%")

    if status_filter:
        query += " AND status = ?"
        parameters.append(status_filter)

    query += " ORDER BY id DESC"

    skills_data = connection.execute(
        query, parameters
    ).fetchall()

    connection.close()

    return render_template(
        "skills.html",
        skills=skills_data,
        search=search,
        status_filter=status_filter
    )


@app.route("/add-skill", methods=["POST"])
def add_skill():
    name = request.form["name"].strip()
    status = request.form["status"]

    if name:
        connection = get_db_connection()
        connection.execute(
            "INSERT INTO skills (name, status) VALUES (?, ?)",
            (name, status)
        )
        connection.commit()
        connection.close()

    return redirect("/skills")


@app.route("/update-skill/<int:id>", methods=["POST"])
def update_skill(id):
    name = request.form["name"].strip()
    status = request.form["status"]

    connection = get_db_connection()
    connection.execute(
        """
        UPDATE skills
        SET name = ?, status = ?
        WHERE id = ?
        """,
        (name, status, id)
    )
    connection.commit()
    connection.close()

    return redirect("/skills")


@app.route("/delete-skill/<int:id>", methods=["POST"])
def delete_skill(id):
    connection = get_db_connection()
    connection.execute(
        "DELETE FROM skills WHERE id = ?",
        (id,)
    )
    connection.commit()
    connection.close()

    return redirect("/skills")


# ============================================================
# PROGRESS
# ============================================================

# ============================================================
# PROGRESS
# ============================================================

@app.route("/progress")
def progress():

    connection = get_db_connection()


    # ========================================================
    # SKILLS
    # ========================================================

    skills = connection.execute(
        "SELECT * FROM skills"
    ).fetchall()


    total_skills = len(skills)

    completed_skills = 0
    learning_skills = 0
    not_started_skills = 0


    for skill in skills:

        if skill["status"] == "Completed":

            completed_skills += 1

        elif skill["status"] == "Learning":

            learning_skills += 1

        elif skill["status"] == "Not Started":

            not_started_skills += 1


    if total_skills > 0:

        skill_progress = (
            completed_skills / total_skills
        ) * 100

    else:

        skill_progress = 0


    # ========================================================
    # DSA
    # ========================================================

    dsa_topics = connection.execute(
        "SELECT * FROM dsa_topics"
    ).fetchall()


    total_dsa = len(dsa_topics)

    completed_dsa = 0
    learning_dsa = 0
    not_started_dsa = 0


    for topic in dsa_topics:

        if topic["status"] == "Completed":

            completed_dsa += 1

        elif topic["status"] == "Learning":

            learning_dsa += 1

        elif topic["status"] == "Not Started":

            not_started_dsa += 1


    if total_dsa > 0:

        dsa_progress = (
            completed_dsa / total_dsa
        ) * 100

    else:

        dsa_progress = 0


    # ========================================================
    # APTITUDE
    # ========================================================

    aptitude_topics = connection.execute(
        "SELECT * FROM aptitude_topics"
    ).fetchall()


    total_aptitude = len(aptitude_topics)

    completed_aptitude = 0
    learning_aptitude = 0
    not_started_aptitude = 0


    for topic in aptitude_topics:

        if topic["status"] == "Completed":

            completed_aptitude += 1

        elif topic["status"] == "Learning":

            learning_aptitude += 1

        elif topic["status"] == "Not Started":

            not_started_aptitude += 1


    if total_aptitude > 0:

        aptitude_progress = (
            completed_aptitude / total_aptitude
        ) * 100

    else:

        aptitude_progress = 0


    # ========================================================
    # REASONING
    # ========================================================

    reasoning_topics = connection.execute(
        "SELECT * FROM reasoning_topics"
    ).fetchall()


    total_reasoning = len(reasoning_topics)

    completed_reasoning = 0
    learning_reasoning = 0
    not_started_reasoning = 0


    for topic in reasoning_topics:

        if topic["status"] == "Completed":

            completed_reasoning += 1

        elif topic["status"] == "Learning":

            learning_reasoning += 1

        elif topic["status"] == "Not Started":

            not_started_reasoning += 1


    if total_reasoning > 0:

        reasoning_progress = (
            completed_reasoning / total_reasoning
        ) * 100

    else:

        reasoning_progress = 0


    connection.close()


    return render_template(

        "progress.html",

        # Skills
        total_skills=total_skills,
        completed_skills=completed_skills,
        learning_skills=learning_skills,
        not_started_skills=not_started_skills,
        skill_progress=round(skill_progress, 2),

        # DSA
        total_dsa=total_dsa,
        completed_dsa=completed_dsa,
        learning_dsa=learning_dsa,
        not_started_dsa=not_started_dsa,
        dsa_progress=round(dsa_progress, 2),

        # Aptitude
        total_aptitude=total_aptitude,
        completed_aptitude=completed_aptitude,
        learning_aptitude=learning_aptitude,
        not_started_aptitude=not_started_aptitude,
        aptitude_progress=round(aptitude_progress, 2),

        # Reasoning
        total_reasoning=total_reasoning,
        completed_reasoning=completed_reasoning,
        learning_reasoning=learning_reasoning,
        not_started_reasoning=not_started_reasoning,
        reasoning_progress=round(reasoning_progress, 2)

    )
# ============================================================
# GENERIC PREPARATION TRACKER HELPERS
# ============================================================

def get_topics(table_name):
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()

    connection = get_db_connection()

    query = f"SELECT * FROM {table_name} WHERE 1 = 1"
    parameters = []

    if search:
        query += " AND topic LIKE ?"
        parameters.append(f"%{search}%")

    if status_filter:
        query += " AND status = ?"
        parameters.append(status_filter)

    query += " ORDER BY id DESC"

    topics = connection.execute(
        query, parameters
    ).fetchall()

    connection.close()

    return topics, search, status_filter


def add_topic(table_name):
    topic = request.form["topic"].strip()
    status = request.form["status"]

    if topic:
        connection = get_db_connection()
        connection.execute(
            f"INSERT INTO {table_name} (topic, status) VALUES (?, ?)",
            (topic, status)
        )
        connection.commit()
        connection.close()


def update_topic(table_name, id):
    topic = request.form["topic"].strip()
    status = request.form["status"]

    connection = get_db_connection()
    connection.execute(
        f"""
        UPDATE {table_name}
        SET topic = ?, status = ?
        WHERE id = ?
        """,
        (topic, status, id)
    )
    connection.commit()
    connection.close()


def delete_topic(table_name, id):
    connection = get_db_connection()
    connection.execute(
        f"DELETE FROM {table_name} WHERE id = ?",
        (id,)
    )
    connection.commit()
    connection.close()


# ============================================================
# DSA
# ============================================================

@app.route("/dsa")
def dsa():
    topics, search, status_filter = get_topics("dsa_topics")

    return render_template(
        "dsa.html",
        topics=topics,
        search=search,
        status_filter=status_filter
    )


@app.route("/add-dsa", methods=["POST"])
def add_dsa():
    add_topic("dsa_topics")
    return redirect("/dsa")


@app.route("/update-dsa/<int:id>", methods=["POST"])
def update_dsa(id):
    update_topic("dsa_topics", id)
    return redirect("/dsa")


@app.route("/delete-dsa/<int:id>", methods=["POST"])
def delete_dsa(id):
    delete_topic("dsa_topics", id)
    return redirect("/dsa")


# ============================================================
# APTITUDE
# ============================================================

@app.route("/aptitude")
def aptitude():
    topics, search, status_filter = get_topics("aptitude_topics")

    return render_template(
        "aptitude.html",
        topics=topics,
        search=search,
        status_filter=status_filter
    )


@app.route("/add-aptitude", methods=["POST"])
def add_aptitude():
    add_topic("aptitude_topics")
    return redirect("/aptitude")


@app.route("/update-aptitude/<int:id>", methods=["POST"])
def update_aptitude(id):
    update_topic("aptitude_topics", id)
    return redirect("/aptitude")


@app.route("/delete-aptitude/<int:id>", methods=["POST"])
def delete_aptitude(id):
    delete_topic("aptitude_topics", id)
    return redirect("/aptitude")


# ============================================================
# REASONING
# ============================================================

@app.route("/reasoning")
def reasoning():
    topics, search, status_filter = get_topics("reasoning_topics")

    return render_template(
        "reasoning.html",
        topics=topics,
        search=search,
        status_filter=status_filter
    )


@app.route("/add-reasoning", methods=["POST"])
def add_reasoning():
    add_topic("reasoning_topics")
    return redirect("/reasoning")


@app.route("/update-reasoning/<int:id>", methods=["POST"])
def update_reasoning(id):
    update_topic("reasoning_topics", id)
    return redirect("/reasoning")


@app.route("/delete-reasoning/<int:id>", methods=["POST"])
def delete_reasoning(id):
    delete_topic("reasoning_topics", id)
    return redirect("/reasoning")


# ============================================================
# APPLICATIONS
# ============================================================

@app.route("/applications")
def applications():
    search = request.args.get("search", "").strip()
    status_filter = request.args.get("status", "").strip()

    connection = get_db_connection()

    query = """
        SELECT * FROM applications
        WHERE 1 = 1
    """
    parameters = []

    if search:
        query += """
            AND (
                company LIKE ?
                OR role LIKE ?
            )
        """
        search_value = f"%{search}%"
        parameters.extend([search_value, search_value])

    if status_filter:
        query += " AND status = ?"
        parameters.append(status_filter)

    query += " ORDER BY id DESC"

    applications_data = connection.execute(
        query, parameters
    ).fetchall()

    connection.close()

    application_list = []

    for application in applications_data:
        application_data = dict(application)

        deadline_status, days_left = get_deadline_info(
            application_data["deadline"]
        )

        application_data["deadline_status"] = deadline_status
        application_data["days_left"] = days_left

        application_list.append(application_data)

    return render_template(
        "applications.html",
        applications=application_list,
        search=search,
        status_filter=status_filter
    )


@app.route("/add-application", methods=["POST"])
def add_application():
    company = request.form["company"].strip()
    role = request.form["role"].strip()
    status = request.form["status"]
    application_date = request.form.get("application_date", "")
    deadline = request.form.get("deadline", "")

    if company and role:
        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO applications
            (
                company,
                role,
                status,
                application_date,
                deadline
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                company,
                role,
                status,
                application_date,
                deadline
            )
        )

        connection.commit()
        connection.close()

    return redirect("/applications")


@app.route("/update-application/<int:id>", methods=["POST"])
def update_application(id):
    company = request.form["company"].strip()
    role = request.form["role"].strip()
    status = request.form["status"]
    application_date = request.form.get("application_date", "")
    deadline = request.form.get("deadline", "")

    connection = get_db_connection()

    connection.execute(
        """
        UPDATE applications
        SET
            company = ?,
            role = ?,
            status = ?,
            application_date = ?,
            deadline = ?
        WHERE id = ?
        """,
        (
            company,
            role,
            status,
            application_date,
            deadline,
            id
        )
    )

    connection.commit()
    connection.close()

    return redirect("/applications")


@app.route("/delete-application/<int:id>", methods=["POST"])
def delete_application(id):
    connection = get_db_connection()

    connection.execute(
        "DELETE FROM applications WHERE id = ?",
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect("/applications")


# ============================================================
# PROFILE
# ============================================================

@app.route("/profile")
def profile():
    connection = get_db_connection()

    profile_data = connection.execute(
        "SELECT * FROM student_profile WHERE id = 1"
    ).fetchone()

    connection.close()

    return render_template(
        "profile.html",
        profile=profile_data
    )


@app.route("/update-profile", methods=["POST"])
def update_profile():
    name = request.form["name"].strip()
    email = request.form["email"].strip()
    phone = request.form.get("phone", "").strip()
    college = request.form.get("college", "").strip()
    branch = request.form.get("branch", "").strip()
    graduation_year = request.form.get("graduation_year", "").strip()
    career_goal = request.form.get("career_goal", "").strip()

    connection = get_db_connection()

    existing_profile = connection.execute(
        "SELECT * FROM student_profile WHERE id = 1"
    ).fetchone()

    if existing_profile:
        connection.execute(
            """
            UPDATE student_profile
            SET
                name = ?,
                email = ?,
                phone = ?,
                college = ?,
                branch = ?,
                graduation_year = ?,
                career_goal = ?
            WHERE id = 1
            """,
            (
                name,
                email,
                phone,
                college,
                branch,
                graduation_year,
                career_goal
            )
        )
    else:
        connection.execute(
            """
            INSERT INTO student_profile
            (
                id,
                name,
                email,
                phone,
                college,
                branch,
                graduation_year,
                career_goal
            )
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                email,
                phone,
                college,
                branch,
                graduation_year,
                career_goal
            )
        )

    connection.commit()
    connection.close()

    return redirect("/profile")


# ============================================================
# CERTIFICATIONS
# ============================================================

@app.route("/certifications")
def certifications():
    connection = get_db_connection()

    certifications_data = connection.execute(
        """
        SELECT * FROM certifications
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "certifications.html",
        certifications=certifications_data
    )


@app.route("/add-certification", methods=["POST"])
def add_certification():
    name = request.form["name"].strip()
    organization = request.form.get("organization", "").strip()
    certification_date = request.form.get("date", "").strip()
    credential = request.form.get("credential", "").strip()

    if name:
        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO certifications
            (
                name,
                organization,
                date,
                credential
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                organization,
                certification_date,
                credential
            )
        )

        connection.commit()
        connection.close()

    return redirect("/certifications")


@app.route("/delete-certification/<int:id>", methods=["POST"])
def delete_certification(id):
    connection = get_db_connection()

    connection.execute(
        "DELETE FROM certifications WHERE id = ?",
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect("/certifications")


# ============================================================
# PROJECTS
# ============================================================

@app.route("/projects")
def projects():
    connection = get_db_connection()

    projects_data = connection.execute(
        """
        SELECT * FROM projects
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "projects.html",
        projects=projects_data
    )


@app.route("/add-project", methods=["POST"])
def add_project():
    name = request.form["name"].strip()
    description = request.form.get("description", "").strip()
    technologies = request.form.get("technologies", "").strip()
    status = request.form["status"]
    github_link = request.form.get("github_link", "").strip()

    if name:
        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO projects
            (
                name,
                description,
                technologies,
                status,
                github_link
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                description,
                technologies,
                status,
                github_link
            )
        )

        connection.commit()
        connection.close()

    return redirect("/projects")


@app.route("/delete-project/<int:id>", methods=["POST"])
def delete_project(id):
    connection = get_db_connection()

    connection.execute(
        "DELETE FROM projects WHERE id = ?",
        (id,)
    )

    connection.commit()
    connection.close()

    return redirect("/projects")


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(debug=True)
