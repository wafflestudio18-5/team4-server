import requests
from rest_framework import status


def get_github_data(data):
    github_token = data.get("github_token")

    URL = "https://api.github.com/user/"
    headers = {
        "Content-Type": "application/json;",
        "Authorization": f"token {github_token}",
    }

    response = requests.get(URL, headers=headers)

    if response.status_code != status.HTTP_200_OK:
        return None

    return response.json()
