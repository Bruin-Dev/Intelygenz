import os
import json
import csv
import urllib.parse
from io import StringIO
from datetime import datetime, timedelta
from pymongo import MongoClient

AUTH_TOKEN = os.environ['AUTH_TOKEN']
MONGODB_HOST = os.environ['MONGODB_HOST']
MONGODB_DATABASE = os.environ['MONGODB_DATABASE']
MONGODB_COLLECTION = os.environ['MONGODB_COLLECTION']
MONGODB_QUERYSTRING = os.environ['MONGODB_QUERYSTRING']
MONGODB_USERNAME = urllib.parse.quote_plus(os.environ['MONGODB_USERNAME'])
MONGODB_PASSWORD = urllib.parse.quote_plus(os.environ['MONGODB_PASSWORD'])

client = MongoClient(f'mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}/?{MONGODB_QUERYSTRING}')
db = client[MONGODB_DATABASE]
collection = db[MONGODB_COLLECTION]


def handler(event, context):
    auth = event['headers'].get('authorization')
    path = event['path']

    if auth != f'Bearer {AUTH_TOKEN}':
        return {'statusCode': 403}

    if path.startswith('/api'):
        return store_data(event)
    elif path.startswith('/csv'):
        return create_csv(event)
    else:
        return {'statusCode': 404}


def store_data(event):
    try:
        collection.insert_one({
            'date': datetime.now(),
            'method': event['httpMethod'],
            'path': event['path'].replace('/api', '', 1),
            'body': json.loads(event['body']) if event['body'] else None,
            'queryParams': event['queryStringParameters']
        })
    except Exception as ex:
        print('Error saving to the database:', ex)
        return {'statusCode': 500}

    return {'statusCode': 200}


def create_csv(event):
    try:
        file = StringIO()
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)

        body_keys = set()
        default_fields = ['date', 'method', 'path', 'queryParams', 'body']

        now = datetime.now().strftime('%Y-%m-%d_%H.%M.%S')

        try:
            params = event.get('queryStringParameters') or {}
            date_from = params.get('date_from')
            date_to = params.get('date_to')
            query = {}

            if date_from or date_to:
                query['date'] = {}

            if date_from:
                query['date']['$gte'] = datetime.fromisoformat(date_from)
            if date_to:
                query['date']['$lte'] = datetime.fromisoformat(date_to) + timedelta(hours=23, minutes=59, seconds=59)
        except:
            return {
                'statusCode': 400,
                'body': 'Invalid date range'
            }

        # Get unique body keys across all stored requests
        for data in collection.find(query):
            if data['body']:
                body_keys.update(data['body'].keys())

        body_keys = list(body_keys)
        writer.writerow(default_fields + [f'body_{key}' for key in body_keys])

        # Create a row for each stored request
        for data in collection.find(query):
            row = []

            for field in default_fields:
                row.append(data[field])

            for key in body_keys:
                body = data.get('body') or {}
                row.append(body.get(key))

            writer.writerow(row)
    except Exception as ex:
        print('Error generating CSV report:', ex)
        return {'statusCode': 500}

    return {
        'statusCode': 200,
        'body': file.getvalue(),
        'headers': {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename="report_{now}.csv"'
        }
    }
