from enum import Enum

DB_NAME = "SIH_2023"
PR_COLLECTION = "press_releases"
BOOKMARKS_COLLECTION = "bookmarks"
USERS_COLLECTION = "users"
STORAGE_BUCKET = "synth-ai-envoys.appspot.com"
API_KEY = "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"
FCM_API_KEY = "AAAAty8MAr0:APA91bG3H_TmVaUod6TkrrJMOR91gd2XMyNuRnSO5Ip-phnwXBUJgPWAQGbOg_lxB8zlIanlMBxOtpMfpuE5B7by8Z8NRickecugAPv3_pDUrhoHt2v9CI7BVKxw67d54wFq9paOnekH"

class PrStatus(Enum):
    APPROVED = "approved"
    PENDING = "pending"
    REJECTED = "rejected"
    ALL = "all"
