import json

from bson import json_util

from DescriptiveContent import DescriptiveContentGenerator
from consts import PR_COLLECTION
from generate_pr_video import GeneratePRVideo
from repository import extract_listing_data, extract_pr_details, add_to_bookmark, remove_from_bookmark, change_status, \
    get_user_bookmarks
from scrape_images import scrape_images
from scrape_pib import scrape_pib
from utils import get_todays_date_milliseconds, save_data_to_mongodb, get_data_from_mongodb, get_milliseconds_from_date


def generate_videos_controller():
    save_press_releases()


def retrieve_press_releases_controller(date, page, items_count, status):
    correct_date = date

    res = extract_listing_data(date, page, items_count, status)

    if res is not None and res != []:
        # for i, d in enumerate(data):
        #     data[i] = json.dumps(d)
        return json_util.dumps(res), 200, {"Content-Type": "application/json"}
    return [{"all_press_releases": [], "date": correct_date}], 200, {
        "Content-Type": "application/json"}


def retrieve_press_release_details_controller(prId):
    return extract_pr_details(prId)


def add_bookmark(user_id, pr_id):
    return add_to_bookmark(user_id, pr_id)


def remove_bookmark(user_id, pr_id):
    return remove_from_bookmark(user_id, pr_id)


def user_bookmarks(userId):
    return list(map(
        lambda x: x.to_json(),
        get_user_bookmarks(userId)
    ))


def change_pr_status(pr_id, date, status):
    change_status(pr_id, date, status)


def save_press_releases():
    data = scrape_pib()
    if data == {}:
        return

    descriptive_content_generator = DescriptiveContentGenerator()

    pr_array = []

    for ministry, press_releases in data.items():
        pr_dict = {"ministry": ministry, "press_releases": []}
        for pr in press_releases:
            try:
                descriptive_content = descriptive_content_generator.generate_descriptive_content(pr)
                descriptive_content.imageUrls += scrape_images(descriptive_content.key_words)
                print(f"DESCRIPTIVE CONTENT: {descriptive_content.to_json()}")
                descriptive_content.videoUrls = GeneratePRVideo(descriptive_content)
                pr_dict["press_releases"].append(descriptive_content.to_json())
            except Exception as e:
                print(f"ERROR OCCURED WHILE GENERATING DESCRIPTIVE CONTENT OF : {pr} {e}")
        pr_array.append(pr_dict)
    res = {"date": get_todays_date_milliseconds(), "all_press_releases": pr_array}
    save_data_to_mongodb(PR_COLLECTION, res)
    return res
