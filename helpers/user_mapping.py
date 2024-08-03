import sqlite3
import random
import hashlib
from typing import Dict, List, Any, Optional

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


def generate_random_profile():
    firstnames = ["John", "Jane", "Michael", "Emily", "David", "Sarah"]
    lastnames = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia"]
    streets = ["Main St", "Oak Ave", "Pine Rd", "Maple Ln", "Cedar Blvd", "Elm St"]
    cities = [
        "New York",
        "Los Angeles",
        "Chicago",
        "Houston",
        "Phoenix",
        "Philadelphia",
    ]
    states = ["NY", "CA", "IL", "TX", "AZ", "PA"]

    return {
        "firstname": random.choice(firstnames),
        "lastname": random.choice(lastnames),
        "address": f"{random.randint(100, 999)} {random.choice(streets)}, {random.choice(cities)}, {random.choice(states)} {random.randint(10000, 99999)}",
        "phone_number": f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
    }


def create_or_get_unique_users() -> List[str]:
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


def map_user(external_username: str, unique_user_emails: List[str]):
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


def get_mapped_user_info(external_username: str) -> Optional[Dict[str, Any]]:
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
    return None


def create_internal_to_external_mapping() -> Dict[str, List[str]]:
    cursor.execute(
        """
        SELECT u.email, m.external_username
        FROM user_mapping m
        JOIN unique_users u ON m.unique_user_email = u.email
    """
    )

    results = cursor.fetchall()

    internal_to_external = {}
    for email, external_username in results:
        if email not in internal_to_external:
            internal_to_external[email] = []
        internal_to_external[email].append(external_username)

    return internal_to_external


def get_external_usernames(unique_username: str) -> List[str]:
    cursor.execute(
        """
        SELECT external_username
        FROM user_mapping
        WHERE unique_user_email = ?
    """,
        (unique_username,),
    )
    results = cursor.fetchall()
    return [row[0] for row in results]


def get_mapped_user(external_username: str) -> Optional[Dict[str, Any]]:
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
    return None


# Example usage
if __name__ == "__main__":
    unique_user_emails = create_or_get_unique_users()

    # Example of mapping external usernames
    external_usernames = ["alice", "bob", "charlie", "david", "eve"]
    for username in external_usernames:
        map_user(username, unique_user_emails)

    # Example of getting mapped user info
    print("Mapped User Info:")
    for username in external_usernames:
        info = get_mapped_user_info(username)
        print(f"Mapped info for {username}: {info}")

    # Create and print the internal to external mapping
    internal_to_external = create_internal_to_external_mapping()
    print("\nInternal to External Mapping:")
    for internal_email, external_usernames in internal_to_external.items():
        print(f"Internal email: {internal_email}")
        print(f"External usernames: {', '.join(external_usernames)}")
        print("---")

    # Example of getting external usernames for a specific unique username
    print("\nExternal Usernames for Specific Unique Username:")
    for unique_email in unique_user_emails:
        external_names = get_external_usernames(unique_email)
        print(f"Unique email: {unique_email}")
        print(f"External usernames: {', '.join(external_names)}")
        print("---")

    # Example of using get_mapped_user
    print("\nUsing get_mapped_user function:")
    for username in external_usernames:
        mapped_user = get_mapped_user(username)
        if mapped_user:
            print(
                f"Mapped user for {username}: {mapped_user['firstname']} {mapped_user['lastname']} ({mapped_user['email']})"
            )
        else:
            print(f"No mapping found for {username}")

# Don't forget to close the database connection when you're done
# conn.close()
