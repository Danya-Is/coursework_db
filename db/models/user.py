from db.model import Model
from flask_login import UserMixin


class User(UserMixin, Model):
    def __init__(self, id, email, password, first_name, last_name, is_administrator):
        super().__init__()
        self.id = id
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.is_administrator = is_administrator
