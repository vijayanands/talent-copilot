import hashlib
import random
import sqlite3
from typing import Any, Dict, Optional

# Connect to SQLite database (or create if it doesn't exist)
conn = sqlite3.connect("user_mapping.db")
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS unique_users (
        email TEXT PRIMARY KEY,
        firstname TEXT,
        lastname TEXT,
        address TEXT,
        phone_number TEXT
    )
"""
)

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS user_mapping (
        external_username TEXT PRIMARY KEY,
        unique_user_email TEXT,
        FOREIGN KEY (unique_user_email) REFERENCES unique_users (email)
    )
"""
)

conn.commit()


# Function to generate random profile info
def generate_random_profile():
    firstnames = ["John", "Jane", "Michael", "Emily"]
    lastnames = ["Smith", "Johnson", "Williams", "Brown"]
    streets = ["Main St", "Oak Ave", "Pine Rd", "Maple Ln"]
    cities = ["New York", "Los Angeles", "Chicago", "Houston"]
    states = ["NY", "CA", "IL", "TX"]

    return {
        "firstname": random.choice(firstnames),
        "lastname": random.choice(lastnames),
        "address": f"{random.randint(100, 999)} {random.choice(streets)}, {random.choice(cities)}, {random.choice(states)} {random.randint(10000, 99999)}",
        "phone_number": f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
    }


# Function to create or get unique users
def create_or_get_unique_users():
    emails = [
        "vijayanands@gmail.com",
        "vijayanands@yahoo.com",
        "vjy1970@gmail.com",
        "email2vijay@gmail.com",
    ]

    for email in emails:
        cursor.execute("SELECT email FROM unique_users WHERE email = ?", (email,))
        if not cursor.fetchone():
            profile = generate_random_profile()
            cursor.execute(
                """
                INSERT INTO unique_users (email, firstname, lastname, address, phone_number)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    email,
                    profile["firstname"],
                    profile["lastname"],
                    profile["address"],
                    profile["phone_number"],
                ),
            )
    conn.commit()

    cursor.execute("SELECT email FROM unique_users")
    return [row[0] for row in cursor.fetchall()]


# Function to map external username to unique user
def map_user(external_username, unique_user_emails):
    hash_value = int(hashlib.md5(external_username.encode()).hexdigest(), 16)
    mapped_user_email = unique_user_emails[hash_value % len(unique_user_emails)]

    cursor.execute(
        """
        INSERT OR REPLACE INTO user_mapping (external_username, unique_user_email)
        VALUES (?, ?)
    """,
        (external_username, mapped_user_email),
    )
    conn.commit()


# API function to get mapped user info
def get_mapped_user_info(external_username):
    cursor.execute(
        """
        SELECT u.email, u.firstname, u.lastname, u.address, u.phone_number
        FROM user_mapping m
        JOIN unique_users u ON m.unique_user_email = u.email
        WHERE m.external_username = ?
    """,
        (external_username,),
    )
    result = cursor.fetchone()

    if result:
        return {
            "email": result[0],
            "firstname": result[1],
            "lastname": result[2],
            "address": result[3],
            "phone_number": result[4],
        }
    else:
        return None


def get_mapped_user(external_username: str) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect("user_mapping.db")
    cursor = conn.cursor()

    hash_value = hashlib.md5(external_username.encode()).hexdigest()

    cursor.execute(
        """
        SELECT u.email, u.firstname, u.lastname, u.address, u.phone_number
        FROM user_mapping m
        JOIN unique_users u ON m.unique_user_email = u.email
        WHERE m.external_username = ?
    """,
        (hash_value,),
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "email": result[0],
            "firstname": result[1],
            "lastname": result[2],
            "address": result[3],
            "phone_number": result[4],
        }
    return None


# Example usage
if __name__ == "__main__":
    unique_user_emails = create_or_get_unique_users()

    # Example of mapping external usernames
    external_usernames = ["alice", "bob", "charlie", "david", "eve"]
    for username in external_usernames:
        map_user(username, unique_user_emails)

    # Example of getting mapped user info
    for username in external_usernames:
        info = get_mapped_user_info(username)
        print(f"Mapped info for {username}: {info}")

# Don't forget to close the database connection when you're done
# conn.close()
