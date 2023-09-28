import datetime

from utils import get_todays_date_milliseconds


class OriginalPressRelease:
    todaysDate = get_todays_date_milliseconds()

    def __init__(self, pr_id, title, content, image_urls, date=todaysDate):
        self.prId = pr_id
        self.title = title
        self.content = content
        self.imageUrls = image_urls
        self.date = date

    def to_json(self):
        return {
            "prId": self.prId,
            "title": self.title,
            "content": self.content,
            "imageUrls": self.imageUrls,
            "date": self.date
        }
