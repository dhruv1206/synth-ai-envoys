import pymongo

from consts import DB_NAME, PR_COLLECTION, PrStatus


def add_approved_attribute(prId, date, status):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client[DB_NAME]
    collection = db[PR_COLLECTION]
    document = collection.find_one({"date": date})
    for ministry_data in document["all_press_releases"]:
        for press_release in ministry_data["press_releases"]:
            if press_release['prId'] == prId:
                press_release['status'] = status
                collection.replace_one({"_id": document["_id"]}, document)
    client.close()

add_approved_attribute("1954574",1693765800000, "approved")