## Introduction
This code is a web application built with Flask and JavaScript for searching Azure Public IPs.

The web app retrieves data from a JSON file containing IP addresses and their associated services, and allows users to search for services or IP addresses.
The search functionality uses fuzzy matching to return the closest results to the user's query.

## Dependencies
This code requires the following dependencies to be installed:
- Flask
- rapidfuzz

## Files
app.py: This is the Flask web app script that serves the HTML and JSON data and implements the search functionality.

script.js: This is the JavaScript file that implements the frontend functionality for the web app.

index.html: This is the HTML file that defines the structure of the web app.

### Running the App
To run the app, run the app.py script. The app will be served on localhost at port 80.
You can access the app by opening a web browser and navigating to http://localhost.
