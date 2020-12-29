import requests
from rest_framework import status
from user.constants import GITHUB_URL


def get_github_data(data):
    github_token = data.get("github_token")

    headers = {
        "Content-Type": "application/json;",
        "Authorization": f"token {github_token}",
    }

    response = requests.get(GITHUB_URL, headers=headers)

    if response.status_code != status.HTTP_200_OK:
        return None

    return response.json()
