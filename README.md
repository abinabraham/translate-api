# Translate Using Python

## Project setup

Build the image:

$ docker-compose build

Once the image is built, run the container:

$ docker-compose up -d

Its available on http://127.0.0.1:8008/



# The main components are:

 ## API Server: 
 This is a Python FastAPI application that handles incoming requests and communicates with the database and Google Translate.
 ## Database: 
 This is a persistent data store that stores word data, including definitions, synonyms, and translations.
 ## Google Translate:
 This is an external service that provides translations and examples for a given word.


## Endpoints
#### Get Word Details
GET /word/{word}

This endpoint returns the details about a given word. The response includes definitions, synonyms, translations, and examples taken from the corresponding Google Translate page. If the word is not found in the database, the handler falls back to Google Translate and saves the fetched data to the database for future use.

#### Get Word List
GET /words

This endpoint returns a list of words stored in the database. Pagination, sorting, and filtering by word are required. Partial matching is used for filtering. Definitions, synonyms, and translations are not included in the response by default, but can be enabled by providing corresponding query parameters.

#### Delete Word
DELETE /word/{word}

This endpoint deletes the given word from the database.


####
GET /word/{word}: Get the details about the given word.
GET /words: Get the list of the words stored in the database.
POST /word: Add a new word to the database.
DELETE /word/{word}: Delete a word from the database.
Here's a brief overview of each endpoint:

GET /word/{word}: This endpoint takes a single path parameter, word, which is the word to retrieve details for. It returns the details for the given word, including the definition, synonyms, translation, and examples. If the word is not found in the database, an HTTP 404 response is returned.

GET /words: This endpoint returns a list of all words stored in the database, along with their associated details. It supports pagination, sorting, and filtering by word. By default, the response only includes the word itself, but additional details can be included by specifying query parameters. For example, to include definitions and synonyms in the response, use /words?include_definitions=true&include_synonyms=true.

POST /word: This endpoint allows a new word to be added to the database. The word is provided as a JSON payload in the request body. If the word already exists in the database, an HTTP 400 response is returned.

DELETE /word/{word}: This endpoint allows a word to be deleted from the database. The word is specified as a path parameter, word. If the word is not found in the database, no error is returned.

####





## Implementation
API Server
The API server is a Python FastAPI application. It has three main components:

API routes: These define the various endpoints that the server responds to.
Database: This is where the word data is stored.
Google Translate client: This is a client library that communicates with Google Translate and fetches data.
Database
The database stores word data, including definitions, synonyms, and translations. The choice of database is up to you, but some good options might be PostgreSQL or MongoDB.

## Google Translate
Google Translate provides translations and examples for a given word. You can use the Google Cloud Translation API or scrape the Google Translate page directly. If you choose to scrape the Google Translate page directly, you can use libraries like Beautiful Soup to parse the HTML and extract the necessary data.



