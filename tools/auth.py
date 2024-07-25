import base64

from requests.auth import HTTPBasicAuth

from tools.credentials import get_password, init_db, load_credentials


def initialize():
    init_db()
    CREDENTIALS_FILE_ROOT: str = "/home/vijay/workspace/talent-copilot-1"
    load_credentials(f"{CREDENTIALS_FILE_ROOT}/credentials.txt")


def get_auth_header(username: str, tool: str) -> HTTPBasicAuth:
    password = get_password(tool, username)
    return HTTPBasicAuth(username, password)


def base64_encode_string(input_string: str) -> str:
    """
    Encode a string to base64.

    :param input_string: The string to encode
    :return: The base64 encoded string
    """
    # Convert the string to bytes
    input_bytes = input_string.encode("utf-8")

    # Perform base64 encoding
    encoded_bytes = base64.b64encode(input_bytes)

    # Convert the result back to a string
    encoded_string = encoded_bytes.decode("utf-8")

    return encoded_string


def get_basic_auth_header(username: str, password: str):
    auth_string = f"{username}:{password}"
    return f"Basic {base64_encode_string(auth_string)}"
