from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Define the Word model that will be used for request and response payloads
class Word(BaseModel):
    id: Optional[int] = None
    word: str
    definition: Optional[str]
    synonyms: Optional[str]
    translation: Optional[str]
    examples: Optional[str]

# Define the connection to the SQLite database
def get_db():
    conn = sqlite3.connect('dictionary.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create the words table if it doesn't exist
conn = get_db()
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS words (id INTEGER PRIMARY KEY AUTOINCREMENT, word TEXT NOT NULL, definition TEXT, synonyms TEXT, translation TEXT, examples TEXT)')
conn.commit()

# Endpoint to get details about a given word
@app.get("/word/{word}", response_model=Word)
async def get_word(word: str):
    # Try to find the word in the database
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM words WHERE word = ?', (word,))
    row = cur.fetchone()
    print("---response1")

    # If the word is in the database, return it
    if row is not None:
        return Word(**row)

    # If the word is not in the database, fetch it from Google Translate
    url = f"https://translate.google.com/?sl=en&tl=es&text={word}&op=translate"
    response = requests.get(url)
    print("---response",response)
    soup = BeautifulSoup(response.content, 'html.parser')
    divs = soup.find_all('div', {'class': 'gt-def-row'})
    if len(divs) > 0:
        definition = divs[0].get_text().strip()
    else:
        definition = None
    synonyms = None
    translation = soup.find('span', {'class': 'tlid-translation translation'}).get_text().strip()
    examples = None

    # Save the word to the database
    cur.execute('INSERT INTO words (word, definition, synonyms, translation, examples) VALUES (?, ?, ?, ?, ?)', (word, definition, synonyms, translation, examples))
    conn.commit()

    # Return the word
    return Word(id=cur.lastrowid, word=word, definition=definition, synonyms=synonyms, translation=translation, examples=examples)


# Endpoint to get a list of words stored in the database
@app.get("/words", response_model=List[Word])
async def get_words(
    skip: int = 0,
    limit: int = 100,
    q: Optional[str] = Query(None, min_length=1),
    include_definitions: Optional[bool] = False,
    include_synonyms: Optional[bool] = False,
    include_translation: Optional[bool] = False,
    include_examples: Optional[bool] = False
):
    # Build the SQL query to get the words
    query = 'SELECT * FROM words'
    params = []
    if q is not None:
        query += ' WHERE word LIKE ?'
        params.append(f'%{q}%')
    query += f' LIMIT {limit} OFFSET {skip}'

    # Execute the SQL query and return the results as a list of Word objects
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    results = []
    for row in rows:
        data = {'id': row['id'], 'word': row['word']}
        if include_definitions:
            data['definition'] = row['definition']
        if include_synonyms:
            data['synonyms'] = row['synonyms']
        if include_translation:
            data['translation'] = row['translation']
        if include_examples:
            data['examples'] = row['examples']
        results.append(Word(**data))
    return results

# Endpoint to add a new word to the database
@app.post("/word", response_model=Word)
async def add_word(word: Word):
    # Check if the word already exists in the database
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM words WHERE word = ?', (word.word,))
    row = cur.fetchone()
    

    # If the word already exists, raise an HTTPException
    if row:
        raise HTTPException(status_code=400, detail="Word already exists")
    synonyms = None
    definition = None
    examples = None
    translation = None
    try:
        # Fetch the word details from Google Translate
        url = f"https://translate.google.com/?sl=en&tl=ru&text={word.word}&op=translate"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        soup.prettify()
        divs = soup.find_all('div', {'class': 'gt-def-row'})
        if len(divs) > 0:
            definition = divs[0].get_text().strip()
        else:
            definition = None
        
        try:
            translation = soup.find('span', {'class': 'tlid-translation translation'}).get_text().strip()
        except AttributeError:
            translation = None
        examples = None
    except:
        pass
    if not translation:
        try:
            translation = translate(word.word)
        except:
            raise HTTPException(status_code=400, detail="Google Translate API error") 

    # Insert the new word into the database and return it
    cur.execute('INSERT INTO words (word, definition, synonyms, translation, examples) VALUES (?, ?, ?, ?, ?)', (word.word, definition, synonyms, translation, examples))
    conn.commit()
    word.id = cur.lastrowid
    word.definition = definition
    word.synonyms = synonyms
    word.translation = translation
    word.examples = examples
    return word

@app.delete("/word/{word}")
async def delete_word(word: str):
    '''
    Delete a word from the database
    '''
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM words WHERE word = ?', (word,))
    conn.commit()


def translate(text):
    '''
    Translate a word using Google Translate
    '''
    from googletrans import Translator
    translator = Translator()
    translated = translator.translate(text,dest='ru')
    return translated.text