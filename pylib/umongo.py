import bson.json_util
import json
import os
import pymongo


def get_mongo_client():
    MONGO_HOST = os.environ['MONGO_HOST']
    MONGO_PORT = int(os.environ['MONGO_PORT'])
    MONGO_USERNAME = os.environ['MONGO_USERNAME']
    MONGO_PASSWORD = os.environ['MONGO_PASSWORD']
    return pymongo.MongoClient(f'mongodb://{MONGO_HOST}:{MONGO_PORT}/',
                               username=MONGO_USERNAME, password=MONGO_PASSWORD)


def bson_to_json(mongo_data, length=0):
    if mongo_data is None:
        return {}
    return json.loads(bson.json_util.dumps(mongo_data))


def bulk_replace_upsert(collection, key, docs):
  ops = []
  for doc in docs:
    ops.append(pymongo.ReplaceOne({key: doc[key]}, doc, upsert=True))
    if(len(ops) == 1000):
      # replace 1000 entries
      collection.bulk_write(ops, ordered=False)
      ops = []

  # replace remaining
  if(len(ops) > 0):
    collection.bulk_write(ops, ordered=False)