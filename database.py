import json
from pymongo import MongoClient
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os 

# Load environment variables from .env file
load_dotenv()
MONGODB_STRING= os.getenv('MONGODB_STRING')
MONGODB_DB_NAME= os.getenv('MONGODB_DB_NAME')


def connect_2_db():

    #connect to mongo
    db_name = quote_plus(MONGODB_DB_NAME)
    url = MONGODB_STRING
    client = MongoClient(url)
    db = client[MONGODB_DB_NAME]
    users = db["users"]
    message_history = db["message_history"]   
    return users, message_history

def save_message_to_db(user_id, user_text, model_res):

    _, message_history = connect_2_db()
    new_messages = [{'user': user_text},
                    {'bot': model_res}]
    
    # Append messages to an existing conversation or create a new conversation
    message_history.update_one(
    {'user_id': user_id},
    {'$push': {'messages': {'$each': new_messages}}},
    upsert=True
)