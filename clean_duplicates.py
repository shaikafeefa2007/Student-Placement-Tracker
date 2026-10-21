import sqlite3

connection = sqlite3.connect("placement_tracker.db")
cursor = connection.cursor()

cursor.execute("""
DELETE FROM skills
WHERE id NOT IN (
    SELECT MIN(id)
    FROM skills
    GROUP BY name
)
""")

connection.commit()

print("Duplicate skills removed successfully!")

cursor.execute("SELECT * FROM skills")

skills = cursor.fetchall()

print("\nRemaining skills:")

for skill in skills:
    print(skill)

connection.close()