import json

import bson.json_util
import pymongo
from pymongo import MongoClient

from consts import DB_NAME, PR_COLLECTION, PrStatus
from utils import save_data_to_mongodb


def extract_listing_data(date=None, page_number=1, items_per_page=100):
    client = pymongo.MongoClient(
        "mongodb+srv://agrawaldhruv1006:ezYjMUKpJefVGvBI@cluster0.kdxmrzd.mongodb.net/?retryWrites=true&w=majority")
    db = client[DB_NAME]
    collection = db["press_releases"]

    # Define a query to filter documents by date if provided
    query = {}
    # Find documents that match the query
    documents = collection.find(query).sort("date", -1)

    for document in documents:
        date = document["date"]
        all_releases = document["all_press_releases"]

        for release in all_releases:
            ministry = release["ministry"]

            for press_release in release["press_releases"]:
                prId = press_release["prId"]
                title = press_release["title"]
                description = press_release["descriptive_text"]
                imageUrls = press_release["imageUrls"] if press_release["imageUrls"] else []
                videoUrls = []
                key_words = press_release["key_words"] if press_release["key_words"] else []
                language = press_release["language"]
                try:
                    videoUrls = press_release["videoUrls"] if press_release["videoUrls"] else []
                except:
                    pass

                yield {
                    "date": date,
                    "ministry": ministry,
                    "prId": prId,
                    "title": title,
                    "description": description,
                    "imageUrls": imageUrls,
                    "videoUrls": videoUrls,
                    "keyWords": key_words,
                    "language": language,
                }
    client.close()


data = json.loads(bson.json_util.dumps(extract_listing_data()))
print(data[0], len(data))
for d in data:
    d["status"] = PrStatus.PENDING.value
    save_data_to_mongodb("new_press_releases", d, "prId")

