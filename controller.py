from bson import json_util
from firebase_admin import messaging

from Models.DescriptiveContent import DescriptiveContentGenerator
from Models.User import User
from consts import PR_COLLECTION, USERS_COLLECTION
from generate_pr_video import GeneratePRVideo
from repository import extract_listing_data, extract_pr_details, add_to_bookmark, remove_from_bookmark, change_status, \
    get_user_bookmarks, search_repository
from scrape_images import scrape_images
from scrape_pib import scrape_pib
from utils import save_data_to_mongodb, get_data_from_mongodb, get_milliseconds_from_date


def generate_videos_controller():
    data, date = scrape_pib()
    if data == {}:
        return

    descriptive_content_generator = DescriptiveContentGenerator()
    pr_id_list = list(map(lambda x: x["prId"], get_data_from_mongodb(PR_COLLECTION, {}, {"prId": 1})))

    # pr_array = []

    for ministry, press_releases in data.items():
        # pr_dict = {"ministry": ministry, "press_releases": []}
        for i, pr in enumerate(press_releases):
            try:
                if pr.prId in pr_id_list:
                    print(f"PR ALREADY EXISTS: {pr.prId}")
                    continue
                # print(f"PR: {pr.to_json()}")
                descriptive_content = descriptive_content_generator.generate_descriptive_content(pr)
                descriptive_content.imageUrls += scrape_images(descriptive_content.key_words)
                # print(f"Descriptive Content: {descriptive_content.to_json()}")
                descriptive_content.videoUrl, descriptive_content.audioUrls = GeneratePRVideo(descriptive_content)
                descriptive_content.ministry = ministry
                descriptive_content.date = date
                print(f"Descriptive Content: {descriptive_content.to_json()}")

                save_data_to_mongodb(PR_COLLECTION, descriptive_content.to_json(), "prId")
                fcm_tokens = get_data_from_mongodb(USERS_COLLECTION, {"preferred_ministries": ministry},
                                                   {"fcm_token": 1})
                fcm_tokens = list(map(lambda x: x["fcm_token"], fcm_tokens))
                print("FCM TOKENS: ", fcm_tokens)
                send_notification(
                    fcm_tokens,
                    title="New Press Release",
                    body=f"New Press Release from {ministry} has been added",
                    image=descriptive_content.imageUrls[0]
                )
            except Exception as e:
                print(f"ERROR OCCURED WHILE GENERATING DESCRIPTIVE CONTENT OF : {pr} {e}")
        # pr_array.append(pr_dict)
    # res = {"date": get_todays_date_milliseconds(), "all_press_releases": pr_array}
    # return res


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


def save_user(user_json):
    user = get_data_from_mongodb(USERS_COLLECTION, {"uuid": user_json["uuid"]})
    print(user)
    if user is not None and user != []:
        user = User.from_json(user[0])
        user.update_user(user_json)
    else:
        user = User.from_json(user_json)
    save_data_to_mongodb(USERS_COLLECTION, user.to_json(), "uuid")
    return user.to_json()


def send_notification(fcm_tokens, title, body, image=None):
    for fcm_token in fcm_tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
                image=image
            ),
            token=fcm_token
        )

        try:
            response = messaging.send(message)
            print("Successfully sent message:", response)
        except Exception as e:
            print("Error sending message:", str(e))
