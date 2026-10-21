import sqlite3


# ---------------- DATABASE CONNECTION ----------------

connection = sqlite3.connect("placement_tracker.db")
cursor = connection.cursor()


# ---------------- CREATE TABLE ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    status TEXT
)
""")

connection.commit()


# ---------------- ADD SKILL ----------------

def add_skill():

    name = input("Enter skill name: ").strip()

    if name == "":
        print("Skill name cannot be empty!")
        return

    status = input("Enter status: ").strip()

    valid_status = ["Not Started", "Learning", "Completed"]

    if status not in valid_status:
        print("Invalid status!")
        print("Use: Not Started, Learning, or Completed")
        return

    cursor.execute("""
    INSERT INTO skills (name, status)
    VALUES (?, ?)
    """, (name, status))

    connection.commit()

    print("Skill added successfully!")


# ---------------- VIEW SKILLS ----------------

def view_skills():

    cursor.execute("SELECT * FROM skills")
    skills = cursor.fetchall()

    print("\nMY SKILLS")
    print("---------")

    if len(skills) == 0:
        print("No skills found.")
        return

    for skill in skills:
        print(
            "ID:", skill[0],
            "| Skill:", skill[1],
            "| Status:", skill[2]
        )


# ---------------- UPDATE SKILL ----------------

def update_skill():

    try:
        skill_id = int(input("Enter skill ID: "))
    except ValueError:
        print("Please enter a valid number.")
        return

    new_status = input("Enter new status: ").strip()

    valid_status = ["Not Started", "Learning", "Completed"]

    if new_status not in valid_status:
        print("Invalid status!")
        print("Use: Not Started, Learning, or Completed")
        return

    cursor.execute("""
    UPDATE skills
    SET status = ?
    WHERE id = ?
    """, (new_status, skill_id))

    connection.commit()

    if cursor.rowcount == 0:
        print("Skill ID not found!")
    else:
        print("Skill updated successfully!")


# ---------------- DELETE SKILL ----------------

def delete_skill():

    try:
        skill_id = int(input("Enter skill ID: "))
    except ValueError:
        print("Please enter a valid number.")
        return

    cursor.execute("""
    DELETE FROM skills
    WHERE id = ?
    """, (skill_id,))

    connection.commit()

    if cursor.rowcount == 0:
        print("Skill ID not found!")
    else:
        print("Skill deleted successfully!")


# ---------------- SHOW PROGRESS ----------------

def show_progress():

    cursor.execute("SELECT * FROM skills")
    skills = cursor.fetchall()

    completed = 0

    for skill in skills:
        if skill[2] == "Completed":
            completed += 1

    total = len(skills)

    if total > 0:
        progress = (completed / total) * 100
    else:
        progress = 0

    print("\nSKILL PROGRESS")
    print("--------------")
    print("Completed:", completed)
    print("Total:", total)
    print("Progress:", round(progress, 2), "%")


# ---------------- MAIN MENU ----------------

while True:

    print("\n===== STUDENT PLACEMENT & SKILL TRACKER =====")
    print("1. Add Skill")
    print("2. View Skills")
    print("3. Update Skill")
    print("4. Delete Skill")
    print("5. Show Progress")
    print("6. Exit")

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        add_skill()

    elif choice == "2":
        view_skills()

    elif choice == "3":
        update_skill()

    elif choice == "4":
        delete_skill()

    elif choice == "5":
        show_progress()

    elif choice == "6":
        print("Thank you for using the tracker!")
        break

    else:
        print("Invalid choice! Please choose 1 to 6.")


# ---------------- CREATE APPLICATIONS TABLE ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS applications (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    company TEXT NOT NULL,

    role TEXT NOT NULL,

    status TEXT NOT NULL,

    application_date TEXT

)
""")


# ---------------- CLOSE DATABASE ----------------

connection.close()


# ---------------- CLOSE DATABASE ----------------

connection.close()