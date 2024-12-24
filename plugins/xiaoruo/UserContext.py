from . import config

class UserContext:
    def __init__(self, user_id, user_name):
        self.user_id = user_id
        self.user_name = user_name

    def has_permission(self):
        return self.user_id in [str(i) for i in config.ops]