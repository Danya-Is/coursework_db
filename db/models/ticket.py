from db.model import Model


class Ticket(Model):
    def __init__(self, id, session_id, seat_id, user_id, cost):
        super().__init__()
        self.id = id
        self.session_id = session_id
        self.seat_id = seat_id
        self.user_id = user_id
        self.cost = cost
