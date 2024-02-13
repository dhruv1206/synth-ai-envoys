import json
import threading

import firebase_admin
from firebase_admin import credentials
from flask import Flask, jsonify, request

from consts import STORAGE_BUCKET, PrStatus
from controller import generate_videos_controller, retrieve_press_releases_controller, \
    retrieve_press_release_details_controller, add_bookmark, remove_bookmark, change_pr_status, user_bookmarks, \
    search_controller, save_user

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('synth-ai-envoys-firebase-adminsdk-mz4rm-70cb455043.json')

firebase_admin.initialize_app(cred, {'storageBucket': STORAGE_BUCKET})


# # Define a list of endpoints where the middleware should not run
# exclude_endpoints = ["/generateVideos"]
#
#
# # Middleware to check Firebase Authentication token
# @app.before_request
# def check_firebase_auth():
#     if request.path in exclude_endpoints:
#         return
#
#     auth_token = request.headers.get("Authorization")
#     if not auth_token:
#         return {"error": "Unauthorized"}, 401
#
#     try:
#         print(auth_token.replace("Bearer ", ""))
#         decoded_token = auth.verify_id_token(auth_token.replace("Bearer ", ""))
#
#         # You can access user information from decoded_token
#         request.user_id = decoded_token['uid']  # Store user ID in the request context
#         print(request.user_id)
#     except auth.InvalidIdTokenError as e:
#         return {"error": "Unauthorized"}, 401
#

@app.route("/generateVideos", methods=['GET'])
def generate_videos():
    threading.Thread(target=generate_videos_controller).start()
    print("GENERATING VIDEOS.....")
    return jsonify({"message": "Generating Videos, you can come back later to check the status"})


@app.route("/getPressReleasesListing", methods=['GET'])
def retrieve_press_releases():
    date = request.args.get("date")
    page = request.args.get("page")
    status = request.args.get("status", default=PrStatus.APPROVED.value)
    itemsCount = request.args.get("itemsCount")

    if page is not None:
        page = int(page)
    if itemsCount is not None:
        itemsCount = int(itemsCount)
    data = retrieve_press_releases_controller(date, page, itemsCount, status)
    return data


@app.route("/changePressReleaseStatus", methods=["POST"])
def change_press_release_status():
    pr_id = request.args.get("prId")
    status = request.args.get("status")
    if pr_id is None is None or status is None:
        return {"error": "Parameters not passed! prId, date, status all three are mandatory!"}, 400
    change_pr_status(pr_id, status)
    return {}, 204


@app.route("/getPRDetails", methods=["GET"])
def retrieve_press_release_details():
    prId = request.args.get("prId")
    if prId is None:
        return {"error": "Missing parameter prId"}, 400
    if prId == "":
        return {"error": "Invalid prId"}, 400
    return retrieve_press_release_details_controller(prId)


@app.route("/addPRToBookmark/<prId>", methods=["POST"])
def add_pr_to_bookmark(prId):
    user_id = request.args.get("uuid")

    if prId is None:
        return {
            "error": "Please add path variable : prId"
        }, 400
    if prId == "":
        return {
            "error": "Please enter a valid prId"
        }, 400
    if user_id is None:
        return {
            "error": "Mission query parameter: user_id"
        }, 400
    if user_id.strip() == "":
        return {
            "error": "Please enter a valid userId"
        }, 400
    add_bookmark(user_id, prId)
    return {"success": "Bookmark added successfully!"}

@app.route("/removePRFromBookmark/<prId>", methods=["GET"])
def remove_pr_from_bookmark(prId):
    try:
        user_id = request.args.get("uuid")
        if prId is None:
            return {
                "error": "Please add path variable : prId"
            }, 400
        if prId == "":
            return {
                "error": "Please enter a valid prId"
            }, 400
        if user_id is None:
            return {
                "error": "Mission query parameter: userId"
            }, 400
        if user_id.strip() == "":
            return {
                "error": "Please enter a valid userId"
            }, 400
        remove_bookmark(user_id, prId)
        return {"success": "Bookmark removed successfully!"}
    except Exception as e:
        print(e)
        return {"error": "Some error occured while removing your bookmark!"}, 500


@app.route("/getUserBookmarks", methods=["GET"])
def get_user_bookmarks():
    try:
        userId = request.args.get("uuid")
        if userId is None:
            return {
                "error": "Mission query parameter 'uuid'"
            }, 400
        if userId.strip() == "":
            return {
                "error": "Please enter a valid uuid"
            }, 400
        bookmarks = json.dumps(user_bookmarks(userId))
        return bookmarks, 200, {
            "Content-Type": "application/json"}

    except Exception as e:
        print(e)
        return {"error": "Some error occured while fetching your bookmarks!"}, 500


@app.route("/getPressReleasesFromQuery", methods=["GET"])
def search_prs():
    try:
        page = request.args.get("page")
        itemsCount = request.args.get("itemsCount")

        if page is not None:
            page = int(page)
        if itemsCount is not None:
            itemsCount = int(itemsCount)
        search_query = request.args.get("q")
        if search_query is None:
            search_query = ""
        if not search_query.strip():
            return retrieve_press_releases_controller(None, page, itemsCount, PrStatus.PENDING.value)
        results = search_controller(search_query, page, itemsCount)
        return results, 200, {
            "Content-Type": "application/json"}
    except Exception as e:
        print(e)
        return {"error": "Some error occured while getting the search results!"}, 500


@app.route("/saveUser", methods=["POST"])
def saveUser():
    user_data = request.get_json()
    print(user_data)
    if user_data is None:
        return {
            "error": "Missing request body!"
        }, 400
    if user_data.get("email") is None:
        return {
            "error": "Missing required field: email"
        }, 400
    if user_data.get("email").strip() == "":
        return {
            "error": "Please enter a valid email"
        }, 400
    if user_data.get("uuid") is None:
        return {
            "error": "Missing required field: uuid"
        }, 400
    if user_data.get("uuid").strip() == "":
        return {
            "error": "Please enter a valid uuid"
        }, 400

    return save_user(user_data), 200




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
