from enum import Enum

DB_NAME = "SIH_2023"
PR_COLLECTION = "press_releases"
BOOKMARKS_COLLECTION = "bookmarks"
STORAGE_BUCKET = "synth-ai-envoys.appspot.com"
API_KEY = "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"


class PrStatus(Enum):
    APPROVED = "approved"
    PENDING = "pending"
    REJECTED = "rejected"
