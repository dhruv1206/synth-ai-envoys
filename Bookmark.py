import datetime


class Bookmark:
    def __init__(self, user_id, pr_id, thumbnail, title, description):
        self.userId = user_id
        self.prId = pr_id
        self.thumbnail = thumbnail
        self.title = title
        self.description = description
        self.date = datetime.datetime.now().timestamp()*1000

    def to_json(self):
        return {
            "userId":self.userId,
            "prId": self.prId,
            "thumbnail": self.thumbnail,
            "title": self.title,
            "description": self.description,
            "date": self.date,
        }

    @classmethod
    def from_json(cls, json_dict):
        return cls(
            json_dict["userId"],
            json_dict["prId"],
            json_dict["thumbnail"],
            json_dict["title"],
            json_dict["description"]
        )