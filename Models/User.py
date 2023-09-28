class User:
    def __init__(self, email: str, uuid: str, username=None, alternate_email=None, phone_number=None,
                 preferred_ministries=None, fcm_token=None, bookmarks=[]):
        if preferred_ministries is None:
            preferred_ministries = []
        self.email = email
        self.username = username
        self.alternate_email = alternate_email
        self.phone_number = phone_number
        self.preferred_ministries = preferred_ministries
        self.uuid = uuid
        self.fcm_token = fcm_token
        self.bookmarks = bookmarks

    def __str__(self):
        return f"User: {self.username}, Email: {self.email}, UUID: {self.uuid}"

    def add_bookmark(self, bookmark):
        """Add a bookmark to the user's list of bookmarks."""
        self.bookmarks.append(bookmark)

    def remove_bookmark(self, bookmark):
        """Remove a bookmark from the user's list of bookmarks if it exists."""
        if bookmark in self.bookmarks:
            self.bookmarks.remove(bookmark)

    def update_alternate_email(self, new_email):
        """Update the user's original email."""
        self.alternate_email = new_email

    def update_username(self, new_username):
        """Update the user's username."""
        self.username = new_username

    def add_ministry_preference(self, ministry):
        """Add a preferred ministry to the user's list of preferences."""
        self.preferred_ministries.append(ministry)

    def remove_ministry_preference(self, ministry):
        """Remove a preferred ministry from the user's list of preferences if it exists."""
        if ministry in self.preferred_ministries:
            self.preferred_ministries.remove(ministry)

    def to_json(self):
        """Serialize the User object to a JSON string."""
        user_dict = {
            "email": self.email,
            "username": self.username,
            "alternate_email": self.alternate_email,
            "phone_number": self.phone_number,
            "preferred_ministries": self.preferred_ministries,
            "uuid": self.uuid,
            "fcm_token": self.fcm_token,
            "bookmarks": self.bookmarks
        }
        return user_dict

    @classmethod
    def from_json(cls, user_dict):
        """Create a User object from a JSON string."""
        return cls(
            user_dict.get("email"),  # No default value provided, so it can be None if missing
            user_dict.get("uuid"),  # No default value provided, so it can be None if missing
            user_dict.get("username"),  # No default value provided, so it can be None if missing
            user_dict.get("alternate_email"),  # No default value provided, so it can be None if missing
            user_dict.get("phone_number"),  # No default value provided, so it can be None if missing
            user_dict.get("preferred_ministries", []),  # Provide a default empty list if missing
            user_dict.get("fcm_token"),  # No default value provided, so it can be None if missing
            user_dict.get("bookmarks", []),  # Provide a default empty list if missing
        )
