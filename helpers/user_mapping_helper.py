import sqlite3
from typing import Any, Dict


def get_mapped_user_info(external_username: str) -> Dict[str, Any]:
    conn = sqlite3.connect("user_mapping.db")
    cursor = conn.cursor()

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
    conn.close()

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


def map_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    mapped_data = {}
    for username, value in data.items():
        mapped_user = get_mapped_user_info(username)
        if mapped_user:
            mapped_username = f"{mapped_user['firstname']} {mapped_user['lastname']}"
            mapped_data[mapped_username] = value
        else:
            mapped_data[username] = value
    return mapped_data

