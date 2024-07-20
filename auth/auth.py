from requests.auth import HTTPBasicAuth
from auth.credentials import load_credentials, init_db, get_password


def initialize():
    init_db()
    CREDENTIALS_FILE_ROOT: str = "/home/vijay/workspace/talent-copilot-1"
    load_credentials(f"{CREDENTIALS_FILE_ROOT}/credentials.txt")


def get_auth_header(username: str, tool: str) -> HTTPBasicAuth:
    password = get_password(tool, username)
    return HTTPBasicAuth(username, password)
