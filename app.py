import threading

import bson.json_util
from flask import Flask, jsonify, request

from consts import STORAGE_BUCKET, PrStatus
from controller import generate_videos_controller, retrieve_press_releases_controller, \
    retrieve_press_release_details_controller, add_bookmark, remove_bookmark, change_pr_status
import firebase_admin
from firebase_admin import credentials, auth

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred, {'storageBucket': STORAGE_BUCKET})

# Define a list of endpoints where the middleware should not run
exclude_endpoints = ["/getPressReleasesListing", "/generateVideos"]


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
    date = request.args.get("date", type=int)
    status = request.args.get("status")
    if pr_id is None or date is None or status is None:
        return {"error": "Parameters not passed! prId, date, status all three are mandatory!"}, 400
    change_pr_status(pr_id, date, status)
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
    if prId is None:
        return {
            "error": "Please add path variable : prId"
        }, 400
    if prId == "":
        return {
            "error": "Please enter a valid prId"
        }, 400
    return bson.json_util.dumps(add_bookmark(request.user_id, prId).to_json()), 200, {
        "Content-Type": "application/json"}


@app.route("/removePRFromBookmark/<prId>", methods=["GET"])
def remove_pr_from_bookmark(prId):
    try:
        if prId is None:
            return {
                "error": "Please add path variable : prId"
            }, 400
        if prId == "":
            return {
                "error": "Please enter a valid prId"
            }, 400
        remove_bookmark(request.user_id, prId)
        return {"success": "Bookmark removed successfully!"}
    except Exception as e:
        print(e)
        return {"error": "Some error occured while removing your bookmark!"}


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=5001)
