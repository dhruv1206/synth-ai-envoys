import json

from bson import json_util

from DescriptiveContent import DescriptiveContentGenerator
from consts import PR_COLLECTION
from generate_pr_video import GeneratePRVideo
from repository import extract_listing_data, extract_pr_details, add_to_bookmark, remove_from_bookmark, change_status, \
    get_user_bookmarks, search_repository
from scrape_images import scrape_images
from scrape_pib import scrape_pib
from utils import get_todays_date_milliseconds, save_data_to_mongodb, get_data_from_mongodb, get_milliseconds_from_date


def generate_videos_controller():
    save_press_releases()


def retrieve_press_releases_controller(date, page, items_count, status):
    correct_date = get_milliseconds_from_date(date)

    res = extract_listing_data(correct_date, page, items_count, status)

    if res is not None and res != []:
        # for i, d in enumerate(data):
        #     data[i] = json.dumps(d)
        return json_util.dumps(res), 200, {"Content-Type": "application/json"}
    return [], 200, {
        "Content-Type": "application/json"}


def retrieve_press_release_details_controller(prId):
    return extract_pr_details(prId)


def add_bookmark(user_id, pr_id):
    return add_to_bookmark(user_id, pr_id)


def remove_bookmark(user_id, pr_id):
    return remove_from_bookmark(user_id, pr_id)


def user_bookmarks(userId):
    return get_user_bookmarks(userId)


def search_controller(searchQuery, page, itemsCount):
    return search_repository(searchQuery, page, itemsCount)


def change_pr_status(pr_id, status):
    change_status(pr_id, status)


def save_press_releases():
    data = scrape_pib()
    if data == {}:
        return

    descriptive_content_generator = DescriptiveContentGenerator()
    pr_id_list = list(map(lambda x: x["prId"], get_data_from_mongodb(PR_COLLECTION, {}, {"prId": 1})))

    # pr_array = []
    get = get_data_from_mongodb(PR_COLLECTION)
    for ministry, press_releases in data.items():
        # pr_dict = {"ministry": ministry, "press_releases": []}
        for pr in press_releases:
            try:
                if pr["prId"] in pr_id_list:
                    print(f"PR ALREADY EXISTS: {pr['prId']}")
                    continue
                descriptive_content = descriptive_content_generator.generate_descriptive_content(pr)
                descriptive_content.imageUrls += scrape_images(descriptive_content.key_words)
                print(f"DESCRIPTIVE CONTENT: {descriptive_content.to_json()}")
                descriptive_content.videoUrls = GeneratePRVideo(descriptive_content)
                descriptive_content.ministry = ministry
                save_data_to_mongodb(PR_COLLECTION, descriptive_content.to_json(), "prId")

            except Exception as e:
                print(f"ERROR OCCURED WHILE GENERATING DESCRIPTIVE CONTENT OF : {pr} {e}")
        # pr_array.append(pr_dict)
    # res = {"date": get_todays_date_milliseconds(), "all_press_releases": pr_array}
    # return res
