#sample script

import requests
import concurrent.futures
import logging

# Configure logging to write messages to a log file
logging.basicConfig(
    filename="api_interaction.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def fetch_messages(api_url, api_key, page):
    params = {
        'page': page,
        'api_key': api_key
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()

        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch messages (Page {page}): {str(e)}")
        return []

def post_message(api_url, api_key, message_data):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(api_url, headers=headers, json=message_data)
        response.raise_for_status()

        logging.info("Message posted successfully.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to post message: {str(e)}")

def main(api_url, api_key, num_workers=1):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        # Example message data (replace with your actual message data)
        message_data = {
            "text": "Hello, this is a test message.",
            "user_id": 12345
        }

        # Fetch messages in parallel
        pages_to_fetch = [1, 2, 3]  # Modify this list as needed
        futures = [executor.submit(fetch_messages, api_url, api_key, page) for page in pages_to_fetch]

        # Process fetched messages
        for future in concurrent.futures.as_completed(futures):
            messages = future.result()
            if messages:
                # Process the fetched messages as needed
                logging.info(f"Fetched {len(messages)} messages.")

        # Post messages in parallel
        futures = [executor.submit(post_message, api_url, api_key, message_data) for _ in range(num_workers)]

        # Wait for message posting to complete
        for future in concurrent.futures.as_completed(futures):
            pass

if __name__ == "__main__":
    # Replace with your API URL and API key or authentication method
    api_url = "https://api.example.com/messages"
    api_key = "your_api_key_here"
    
    # Specify the number of worker threads
    num_workers = 3  # Change this to the desired number of workers

    main(api_url, api_key, num_workers)