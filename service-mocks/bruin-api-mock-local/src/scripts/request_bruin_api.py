import base64
from cmath import log

import requests

LOGIN_URL = "https://id.bruin.com/"
API_URL = "https://api.bruin.com/"

# TODO: Security risk. Load from environment file
CLIENT_ID="fPNu1rxOo63zpsYZVpB65Kf72485FdLD"
CLIENT_SECRET="Kj376v5LJatMvndcJ4g2vP5Qff8azMQxaw0brYO3eW1wJUuqtIDg4hT17XsJGq04"


def login():
    """
    Test login/identity/connect/token
    """
    login_credentials = '%s:%s' % (CLIENT_ID, CLIENT_SECRET)
    login_credentials = login_credentials.encode()
    login_credentials_b64 = base64.b64encode(login_credentials).decode()    

    headers = {
        "authorization": "Basic %s" % (login_credentials_b64),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    form_data = {
        "grant_type": "client_credentials",
        "scope": "public_api"
    }

    response = requests.post(
        f'{LOGIN_URL}identity/connect/token',
        data=form_data,
        headers=headers,
    )

    print(response)
    print(response.json())
    return response.json()["access_token"]


def main():
    access_token = login()
    print(access_token)



if __name__ == "__main__":
    main()