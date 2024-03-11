# RSS Reader

## Prerequisites
- Docker
- Make

## Getting Started

1. Navigate to the project directory:
    ```bash
    cd rss-reader
    ```

2. Build and start the application:
    ```bash
    make build
    make up
    ```
    ps:
    You can also run unit tests after building:
    ```bash
    make test
    ```
3. Access the API documentation:
    Open your browser and go to `http://0.0.0.0:8000/docs`.

4. Register a new user:
    - Click on the "Register" endpoint in the API documentation.
    - Fill in the required fields and click "Try it out!".
    - Take note of the generated access token.

5. Authorize API requests:
    - Click on the "Authorize" button on the top right corner of the API documentation.
    - Enter the access token obtained from the registration step.
    - Click "Authorize" to enable authorization for API requests.

6. Start using the API endpoints:
    - Explore the available endpoints in the API documentation.
    - Click on an endpoint to expand its details.
    - Fill in the required parameters and click "Try it out!" to make a request.

7. Register an RSS URL:
    - Make a POST request to the `feed` endpoint in the API documentation.
    - Provide the necessary parameters, such as the RSS URL.
    - Click "Try it out!" to register the RSS URL to the system.

8. Subscribe to a feed:
    - After registering an RSS URL, make a POST request to the `subscribe` endpoint.
    - Provide the necessary parameters, such as the feed ID.
    - make the request to subscribe to a feed.

9. Get your feed:
    - Once you have subscribed to a feed, you can retrieve it by making a GET request to the correct URL.
    - Replace the placeholder in the URL with the feed ID.
    - make the request to get your feed.

10. Force refresh:
    - If you don't want to wait for background tasks to finish, you can force refresh a feed by making a POST request to the `force-refresh` endpoint.
    - Provide the necessary parameters, such as the feed ID.
    - make the request

11. Mark feeds as read or unread:
    - To mark a feed as read, make a POST request to the "mark-read" endpoint.
    - Provide the necessary parameters, such as the feed ID.
    - Click "Try it out!" to mark the feed as read.
    - To mark a feed as unread, make a POST request to the "mark-unread" endpoint.
    - Provide the necessary parameters, such as the feed ID.
    - make the request

You can explore api docs for othe possible actions you can take (e.g unsubscribe) or you can check out `makefile` to see available useful developer commands for inspection.