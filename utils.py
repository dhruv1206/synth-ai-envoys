import base64
import datetime
import firebase_admin
import random
import string
from firebase_admin import credentials, storage

import openai
import pymongo

from Bookmark import Bookmark
from consts import DB_NAME, PR_COLLECTION


# Set your OpenAI API key
# openai.api_key = "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"

def count_tokens(text):
    tokens = openai.Completion.create(
        engine="davinci",  # Choose an appropriate engine
        prompt=text,
        max_tokens=1,
        temperature=0,
    )['usage']['total_tokens']
    return tokens


def get_todays_date_milliseconds():
    exact = datetime.datetime.now()
    today = datetime.datetime(exact.year, exact.month, exact.day)
    return round((today.timestamp() * 1000))


def get_milliseconds_from_date(date: int):
    if date is None:
        return None
    date = int(date)
    new_date = datetime.datetime.fromtimestamp(date / 1000)
    new_date = datetime.datetime(new_date.year, new_date.month, new_date.day)
    return int(new_date.timestamp() * 1000)


def download_image_from_url(image_data, filename):
    imgdata = base64.b64decode(image_data.replace("data:image/jpeg;base64,", ""))
    with open(filename, 'wb') as f:
        f.write(imgdata)
    return filename


def save_data_to_mongodb(collection_name, data, unique_check):
    client = pymongo.MongoClient(
        "mongodb+srv://agrawaldhruv1006:ezYjMUKpJefVGvBI@cluster0.kdxmrzd.mongodb.net/?retryWrites=true&w=majority")
    db = client[DB_NAME]
    collection = db[collection_name]
    existing_document = collection.find_one({unique_check: data[unique_check]})
    if existing_document:
        res = collection.replace_one({unique_check: data[unique_check]}, data)
        print("Document replaced successfully", res)
    else:
        res = collection.insert_one(data)
        print("Document inserted successfully", res)
    client.close()


def get_data_from_mongodb(collection_name, query={}, attrbutes = {}):
    client = pymongo.MongoClient(
        "mongodb+srv://agrawaldhruv1006:ezYjMUKpJefVGvBI@cluster0.kdxmrzd.mongodb.net/?retryWrites=true&w=majority")
    db = client[DB_NAME]
    collection = db[collection_name]

    # query = {}
    # if date is not None:
    #     query = {"date": date}
    ans = list(map(lambda x: x
                   , collection.find(query, attrbutes)))
    client.close()
    return ans


def remove_data_from_mongodb(collection_name, query):
    client = pymongo.MongoClient(
        "mongodb+srv://agrawaldhruv1006:ezYjMUKpJefVGvBI@cluster0.kdxmrzd.mongodb.net/?retryWrites=true&w=majority")
    db = client[DB_NAME]
    collection = db[collection_name]
    collection.delete_one(query)
    client.close()


def generate_random_string(length):
    characters = string.ascii_letters + string.digits  # You can include more characters if needed
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def upload_multiple_images_to_firebase(image_urls):
    try:
        bucket = storage.bucket()
        firebase_image_urls = []
        for image_path in image_urls:
            # Specify the path in Firebase Storage where you want to store the image
            destination_blob_name = f'images/{get_todays_date_milliseconds()}/{image_path.split("/")[-1]}'

            # Upload the image to Firebase Storage
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(image_path)
            blob.make_public()

            # Get the download URL for the uploaded image
            download_url = blob.public_url  # URL expiration time in seconds
            firebase_image_urls.append(download_url)
        return firebase_image_urls
    except Exception as e:
        print(e)
        return []


def upload_video_to_firebase(video_url):
    try:
        bucket = storage.bucket()
        # Specify the path in Firebase Storage where you want to store the image
        destination_blob_name = f'videos/{get_todays_date_milliseconds()}/{video_url.split("/")[-1]}'

        # Upload the image to Firebase Storage
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(video_url)
        blob.make_public()

        # Get the download URL for the uploaded image
        download_url = blob.public_url  # URL expiration time in seconds
        return download_url
    except Exception as e:
        print(e)
        return []
