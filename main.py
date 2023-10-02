import asyncio
import os
import aiohttp

# See values.yaml for defaul values
NUM_RESOURCE_WORKERS = int(os.environ.get("NUM_RESOURCE_WORKERS"))
# API Endpoint for Source API
API_ENDPOINT = os.environ.get("API_ENDPOINT")
AUTH_TOKEN = os.environ.get("X_AUTH_TOKEN")
# Path range starting at 1, end at 100
RESOURCE_ID_START = int(os.environ.get("RESOURCE_ID_START"))
RESOURCE_ID_END = int(os.environ.get("RESOURCE_ID_END"))

# API Endpoint for Processing Service
SECOND_API_ENDPOINT = os.environ.get("SECOND_API_ENDPOINT")
SECOND_API_AUTH_TOKEN = os.environ.get("SECOND_API_AUTH_TOKEN")

# API Endpoint for Storing Service
THIRD_API_ENDPOINT = os.environ.get("THIRD_API_ENDPOINT")
THIRD_API_AUTH_TOKEN = os.environ.get("THIRD_API_AUTH_TOKEN")

# Max number of attempts
MAX_RETRY_ATTEMPTS = 3

# Semaphore to limit the number of concurrent workers
semaphore = asyncio.Semaphore(NUM_RESOURCE_WORKERS)

# Fetch data from the Source API asynchronously and return JSON data
async def fetch_resource(session, resource_id, retry_count=0):
    url = f"{API_ENDPOINT}/{resource_id}"
    headers = {"X-Auth-Token": AUTH_TOKEN} if AUTH_TOKEN else {}

    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            return data
        else:
            error_message = await response.text()
            print(f"Failed to collect resource {resource_id}, Response Code: {response.status}, Error Message: {error_message}")

            if retry_count < MAX_RETRY_ATTEMPTS:
                # Retry the resource with an increased retry count
                print(f"Retrying ({retry_count + 1}/{MAX_RETRY_ATTEMPTS}) for resource {resource_id}")
                return await fetch_resource(session, resource_id, retry_count + 1)

            print(f"Maximum retry attempts reached for resource {resource_id}")
            # Return None when maximum retry attempts reached
            return None

# Post data to the Processing or Storing API asynchronously and return JSON data
async def post_resource(session, api_endpoint, auth_token, data_to_post, retry_count=0):
    url = f"{api_endpoint}"
    headers = {"X-Auth-Token": auth_token} if auth_token else {}

    async with session.post(url, headers=headers, json=data_to_post) as response:
        if response.status == 201:
            print(f"Posted resource successfully: {data_to_post}")
        else:
            error_message = await response.text()
            print(f"Failed to post resource: {data_to_post}, Response Code: {response.status}, Error Message: {error_message}")

            if retry_count < MAX_RETRY_ATTEMPTS:
                # Retry posting the resource with an increased retry count
                print(f"Retrying ({retry_count + 1}/{MAX_RETRY_ATTEMPTS}) for resource: {data_to_post}")
                return await post_resource(session, api_endpoint, auth_token, data_to_post, retry_count + 1)

            print(f"Maximum retry attempts reached for resource: {data_to_post}")
            # Return None when maximum retry attempts reached
            return None

# Function to retry failed resources asynchronously by Worker 1
async def retry_failed_resources(session):
    while True:
        item = await retry_queue.get()
        if item is None:
            break  # Exit the loop when None is encountered in the queue

        resource_type, api_endpoint, auth_token, resource_data, retry_count = item

        if retry_count <= MAX_RETRY_ATTEMPTS:
            if resource_type == "fetch":
                await fetch_resource(session, resource_data, retry_count)
            elif resource_type == "post":
                await post_resource(session, api_endpoint, auth_token, resource_data, retry_count)
        else:
            print(f"Maximum retry attempts reached for resource: {resource_data}")

        retry_queue.task_done()

retry_queue = asyncio.Queue()

# Function to collect data using asyncio
async def collect_data():
    resource_ids = range(RESOURCE_ID_START, RESOURCE_ID_END + 1)

    async with aiohttp.ClientSession() as session:
        # Create a group of tasks for data collection and posting
        tasks = []

        for resource_id in resource_ids:
            # Attempt to acquire the semaphore to limit the number of concurrent workers
            async with semaphore:
                response_task = asyncio.create_task(fetch_resource(session, resource_id))
                tasks.append(response_task)
                data = await response_task
                if data:
                    post_task = asyncio.create_task(post_resource(session, SECOND_API_ENDPOINT,SECOND_API_AUTH_TOKEN, data))
                    tasks.append(post_task)

                    # If the post to the Processing API was successful, send the data to the Storage API
                    if post_task and post_task.result() and post_task.result().status == 201:
                        post_data = await post_task.result().json()
                        await post_resource(session, THIRD_API_AUTH_TOKEN, THIRD_API_ENDPOINT, post_data)

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

    # End retry worker
    await retry_queue.put(None)

if __name__ == "__main__":
    # Create a task for retrying failed resources by Worker 1
    retry_task = asyncio.create_task(retry_failed_resources(aiohttp.ClientSession()))

    # Run data collection
    asyncio.run(collect_data())

    # Wait for the retry task to finish
    asyncio.run(retry_queue.join())
    retry_task.cancel()