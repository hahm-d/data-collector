import requests
# RUN in terminal:  python -m pip install requests
# rickandmortyapi.com/documentation/
# importing threading to include workers
# using httpbin.org to mimic porcessing service / storage service


def fetch_messages(api_url, api_key):
    messages = []
    page = 1

    while True:
        # Make a GET request to the API with pagination parameters
        params = {
            'page': page,
            'api_key': api_key  # Replace with your API key or authentication method
        }

        response = requests.get(api_url, params=params)

        if response.status_code == 200:
            # Assuming the API returns messages as a list in JSON format
            new_messages = response.json()

            if not new_messages:
                break

            messages.extend(new_messages)
            page += 1
        elif response.status_code == 401:
            print("Unauthorized: Check your API key or authentication.")
            break
        elif response.status_code == 429:
            print("Too many requests: Requests are limited to 120 requests per minute. If this limit is exceeded all requests for the auth token will be blocked for 30 seconds..")
            break            
        elif response.status_code == 500:
            print("Internal Server Error: The API encountered an issue.")
            break
        else:
            print(f"{response.reason}. Status code: {response.status_code}")
            break

    return messages

def post_message(process_url, process_key, message_data):
    headers = {
        'Authorization': f'Bearer {process_key}',  # Replace with your authentication method
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(process_url, headers=headers, json=message_data)

        if response.status_code == 201:
            # on success, send to stoage service. 
            print("Message posted successfully.")
            print(response.json())
        else:
            # if fails try again up to 3  times. log on 3rd failed attempt
            print(f"{response.reason}. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Replace with your API URL and API key or authentication method
    api_url = "https://rickandmortyapi.com/api/"
    api_key = ""
    process_url = ""
    process_key = ""
    storage_url = ""
    storage_key = ""
    num_workers = 3

    collected_messages = fetch_messages(api_url, api_key)

    if collected_messages:
        # send directly to processing service 
        print(f"Collected {len(collected_messages)} messages.")
        processed_message = post_message(process_url, process_key, collected_messages)
        if processed_message: 
            # confirm on success
            store_message = post_message(storage_url, storage_key, processed_message)
        else:
            print("log the failed response here")
    else:
        # if fails try again up to 3 times. Log on 3rd failed attempt.
        print("No messages were collected.")
