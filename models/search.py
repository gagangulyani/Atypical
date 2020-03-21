from models.database import Database
from string import punctuation
from json import load
import requests

def Hashtags(fileObj):
    # Everypixel API
    cred = load(open('models/config_api.json'))
    client_id = cred.get('ClientID') # CLIENT ID
    client_secret = cred.get('Secret') # CLIENT SECRET
    finalKeywords = []
    data = {'data': fileObj, 'num_keywords': 20}

    while True:
        try:
            keywords = requests.post('https://api.everypixel.com/v1/keywords',
                             files=data,
                             auth=(client_id, client_secret)).json()
        except:
            print('Connection to everypixel API failed.. Trying again..')
        else:
            break

    for keyword in keywords.get('keywords'):
        finalKeywords.append(keyword.get('keyword').replace('-',' ').lower().strip())

    return finalKeywords, keywords

def words(query):
    query = [word.lower() for word in query.split() if word.strip()][:20]
    with open("models/stop_words.txt") as f:
        stop_words = [word.strip() for word in f.readlines()]
    final_query = []
    for word in query:
        if not word in stop_words:
            final_query.append(word)
    return final_query