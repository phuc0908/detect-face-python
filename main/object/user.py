class User:
    def __init__(self, user_id, name, cccd, image_path, status="None"):
        self.user_id = user_id
        self.name = name
        self.cccd = cccd
        self.image_path = image_path
        self.status = status

    def update_status(self, new_status):
        self.status = new_status

    def get_info(self):
        return {
            "id": self.user_id,
            "name": self.name,
            "cccd": self.cccd,
            "image": self.image_path,
            "status": self.status,
        }

    def __str__(self):
        return f"User({self.user_id}, {self.name}, {self.cccd}, {self.status})"
