import os
import json
import csv
import urllib.parse
from io import StringIO
from datetime import datetime, timedelta
from pymongo import MongoClient

client = MongoClient(os.environ['DB_CONNECTION_STRING'])


def handler(event, context):
    print(f"{client.db_name.command('ping')}")
    return {
                'statusCode': 200,
                'body': client.db_name.command('ping')
            }
