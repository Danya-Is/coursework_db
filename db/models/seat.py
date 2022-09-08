from db.model import Model


class Seat(Model):
    def __init__(self, id, hall_id, row_number, seat_number, category):
        super().__init__()
        self.id = id
        self.hall_id = hall_id
        self.row_number = row_number
        self.seat_number = seat_number
        self.category = category
