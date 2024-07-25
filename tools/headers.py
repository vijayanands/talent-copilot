from typing import Dict

from tools.auth import get_basic_auth_header


def get_headers(username: str, api_token: str) -> Dict[str, str]:
    headers = {
        "Accept": "application/json",
        "Authorization": get_basic_auth_header(username, api_token),
    }
    return headers
