from models.database import Database
import nltk
import requests

def Hashtags(fileObj):
    # Everypixel API
    client_id = 'CLIENT ID'
    client_secret = 'CLIENT SECRET'
    finalKeywords = []
    data = {'data': fileObj, 'num_keywords': 20}

    keywords = requests.post('https://api.everypixel.com/v1/keywords',
                             files=data,
                             auth=(client_id, client_secret)).json()

    for keyword in keywords.get('keywords'):
        finalKeywords.append(keyword.get('keyword').replace('-',' ').lower().strip())

    return finalKeywords

def filter(query):
    filtered_query = ""
    return filtered_query