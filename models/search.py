from models.database import Database
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

    return finalKeywords

def filter(query):
    filtered_query = ""
    return filtered_query