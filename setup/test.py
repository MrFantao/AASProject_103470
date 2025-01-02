import requests
import time
import random

def send_request(url, headers):
    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print("Response:", response.json())
        else:
            print(f"Failed with status code {response.status_code}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    url = "http://127.0.0.1:8080/service1"
    
    # Define two sets of headers
    headers_list = [
        {"user": "admin", "password": "admin"},  # Correct credentials
        {"user": "wrong_user", "password": "wrong_password"}  # Incorrect credentials
    ]

    while True:
        headers = random.choice(headers_list)  # Randomly choose one of the headers
        send_request(url, headers)
        time.sleep(1)