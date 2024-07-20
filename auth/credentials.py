import sqlite3
from enum import Enum
import csv


# Define the enumerated type for the tools
class Tool(Enum):
    JIRA = "JIRA"
    CONFLUENCE = "CONFLUENCE"
    GITHUB = "GITHUB"


# Initialize the database
def init_db():
    conn = sqlite3.connect("tools.db")
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS credentials (
        tool TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        PRIMARY KEY (tool, username)
    )
    """
    )
    conn.commit()
    conn.close()


# Function to load data from a text file into the database
def load_credentials(file_path):
    conn = sqlite3.connect("tools.db")
    cursor = conn.cursor()
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            tool, username, password = row
            cursor.execute(
                """
            INSERT OR REPLACE INTO credentials (tool, username, password)
            VALUES (?, ?, ?)
            """,
                (tool, username, password),
            )
    conn.commit()
    conn.close()


# Function to get the password based on the tool and username
def get_password(tool, username):
    conn = sqlite3.connect("tools.db")
    cursor = conn.cursor()
    cursor.execute(
        """
    SELECT password FROM credentials
    WHERE tool = ? AND username = ?
    """,
        (tool.value, username),
    )
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return None


# Initialize the database
init_db()

# Example usage
# load_credentials('credentials.txt')
# print(get_password(Tool.JIRA, 'user1'))
