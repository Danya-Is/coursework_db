from db.model import Model


class Hall(Model):
    def __init__(self, id, hall_number, hall_name, cinema_id):
        super().__init__()
        self.id = id
        self.hall_number = hall_number
        self.hall_name = hall_name
        self.cinema_id = cinema_id
