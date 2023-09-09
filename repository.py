import datetime

import pymongo

from Bookmark import Bookmark
from DescriptiveContent import DescriptiveContent
from consts import DB_NAME, PR_COLLECTION, BOOKMARKS_COLLECTION, PrStatus
from utils import get_milliseconds_from_date, save_data_to_mongodb, remove_data_from_mongodb


def extract_pr_details(pr_id) -> any:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client[DB_NAME]
    collection = db[PR_COLLECTION]
    query = {
        "all_press_releases.press_releases.prId": pr_id
    }
    document = collection.find_one(query)
    if document:
        for release in document.get("all_press_releases", []):
            for press_release in release.get("press_releases", []):
                if press_release.get("prId") == pr_id:
                    pr = press_release
                    client.close()
                    return pr


def extract_listing_data(date=None, page_number=1, items_per_page=10, status=PrStatus.APPROVED):
    if page_number is None:
        page_number = 1
    if items_per_page is None:
        items_per_page = 10

    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client[DB_NAME]
    collection = db[PR_COLLECTION]

    # Define a query to filter documents by date if provided
    query = {}
    if date:
        query["date"] = get_milliseconds_from_date(date)
    # Find documents that match the query
    documents = collection.find(query).sort("date", -1)

    for document in documents:
        date = document["date"]
        all_releases = document["all_press_releases"]

        # Calculate the start and end indices for the current page
        start_index = (page_number - 1) * items_per_page
        end_index = start_index + items_per_page

        for release in all_releases[start_index:end_index]:
            ministry = release["ministry"]

            for press_release in release["press_releases"]:
                prId = press_release["prId"]
                title = press_release["title"]
                description = press_release["descriptive_text"]
                thumbnail = press_release["imageUrls"][0] if press_release["imageUrls"] else None
                # print(press_release["approved"], bool(approved))
                if press_release["status"] != status:
                    continue
                yield {
                    "date": date,
                    "ministry": ministry,
                    "prId": prId,
                    "title": title,
                    "description": description,
                    "thumbnail": thumbnail,
                }
    client.close()

def add_to_bookmark(user_id, pr_id):
    pr_details = extract_pr_details(pr_id)
    if pr_details is not None:
        pr_details = DescriptiveContent.from_json(pr_details)
        bookmark = Bookmark(user_id, pr_id, pr_details.imageUrls[0], pr_details.title, "\n".join(pr_details.
                                                                                                 descriptive_text))
        save_data_to_mongodb(BOOKMARKS_COLLECTION, bookmark.to_json(), "prId")
    return pr_details


def remove_from_bookmark(user_id, pr_id):
    remove_data_from_mongodb(BOOKMARKS_COLLECTION, {"userId": user_id, "prId": pr_id})


def change_status(pr_id,date, status):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client[DB_NAME]
    collection = db[PR_COLLECTION]
    document = collection.find_one({"date": date})
    for ministry_data in document["all_press_releases"]:
        for press_release in ministry_data["press_releases"]:
            if press_release['prId'] == pr_id:
                press_release['status'] = status
                collection.replace_one({"_id": document["_id"]}, document)
    client.close()


if __name__ == "__main__":
    extract_pr_details("1955324")
