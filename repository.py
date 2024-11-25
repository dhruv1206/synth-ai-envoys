import json

import pymongo
from bson import json_util

from Models.User import User
from consts import DB_NAME, PR_COLLECTION, PrStatus, USERS_COLLECTION
from utils import get_milliseconds_from_date, save_data_to_mongodb, get_data_from_mongodb

client = pymongo.MongoClient(
    "mongodb+srv://agrawaldhruv1006:ezYjMUKpJefVGvBI@cluster0.kdxmrzd.mongodb.net/?retryWrites=true&w=majority")


def extract_pr_details(pr_id) -> any:
    # client = pymongo.MongoClient(
    #     host='SIH_2023',
    #     port=27017, username='root', password="pass", authSource='admin')
    db = client[DB_NAME]
    collection = db[PR_COLLECTION]
    query = {
        "prId": pr_id
    }
    document = collection.find_one(query)
    data = json.loads(json_util.dumps(document)
                      ) if document is not None else None
    # client.close()
    return data


def extract_listing_data(date=None, page_number=1, items_per_page=10, status=PrStatus.APPROVED.value):
    if page_number is None:
        page_number = 1
    if items_per_page is None:
        items_per_page = 10

    # client = pymongo.MongoClient(
    #     host='SIH_2023',
    #     port=27017, username='root', password="pass", authSource='admin')
    db = client[DB_NAME]
    collection = db[PR_COLLECTION]

    # Define a query to filter documents by date if provided
    query = {}
    if date:
        query["date"] = get_milliseconds_from_date(date)
    if status != PrStatus.ALL.value:
        query["status"] = status

    # Calculate the start and end indices for the current page
    start_index = (page_number - 1) * items_per_page
    print(query)
    # Find documents that match the query
    documents = collection.find(query).sort(
        "date", -1).skip(start_index).limit(items_per_page)
    data = list(map(lambda x: json.loads(json_util.dumps(x)), documents))

    # client.close()
    return data


def add_to_bookmark(user_id, pr_id):
    user = get_data_from_mongodb(USERS_COLLECTION, {"uuid": user_id})
    if user is not None and user != []:
        user = User.from_json(user[0])
        print(user)
        if pr_id not in user.bookmarks:
            user.add_bookmark(pr_id)
        save_data_to_mongodb(USERS_COLLECTION, user.to_json(), "uuid")


def remove_from_bookmark(user_id, pr_id):
    user = get_data_from_mongodb(USERS_COLLECTION, {"uuid": user_id})
    if user is not None and user != []:

        user = User.from_json(user[0])
        if pr_id in user.bookmarks:
            user.remove_bookmark(pr_id)
        save_data_to_mongodb(USERS_COLLECTION, user.to_json(), "uuid")


def change_status(pr_id, status):
    # client = pymongo.MongoClient(
    #     host='SIH_2023',
    #     port=27017, username='root', password="pass", authSource='admin')
    db = client[DB_NAME]
    collection = db[PR_COLLECTION]
    document = collection.find_one({"prId": pr_id})
    document['status'] = status
    collection.replace_one({"_id": document["_id"]}, document)
    # client.close()


def get_user_bookmarks(userId):
    # client = pymongo.MongoClient(
    #     host='SIH_2023',
    #     port=27017, username='root', password="pass", authSource='admin')
    db = client[DB_NAME]
    collection = db[USERS_COLLECTION]
    document = collection.find_one({"uuid": userId})
    if document is None:
        return []
    bookmarks = []
    collection = db[PR_COLLECTION]
    for pr_id in document["bookmarks"]:
        bookmarks.append(json.loads(json_util.dumps(
            collection.find_one({"prId": pr_id}))))

    # client.close()
    return bookmarks

    # collection = db[BOOKMARKS_COLLECTION]
    # documents = collection.find({"userId": userId})
    # bookmarks = []
    # for document in documents:
    #     bookmarks.append(json.loads(json_util.dumps(document)))
    # client.close()
    # return bookmarks


def search_repository(search_query, page=1, itemsCount=10):
    if page is None:
        page = 1
    if itemsCount is None:
        itemsCount = 10
    # client = pymongo.MongoClient(
    #     host='SIH_2023',
    #     port=27017, username='root', password="pass", authSource='admin')
    db = client[DB_NAME]
    collection = db[PR_COLLECTION]
    query = {
        "$or": [
            {"title": {"$regex": search_query, "$options": "i"}},
            {"description": {"$regex": search_query, "$options": "i"}},
            {"keyWords": {"$in": [search_query]}},
            {"ministry": {"$regex": search_query, "$options": "i"}},
        ]
    }
    data = list(map(lambda x: json.loads(json_util.dumps(x)), collection.find(query).skip((page - 1) * itemsCount)
                    .limit(itemsCount)))
    # client.close()

    return data


if __name__ == "__main__":
    extract_pr_details("1955324")
