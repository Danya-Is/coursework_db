from db.model import Model


class Session(Model):
    def __init__(self, id, session_date, start_time, hall_id, film_id, end_time):
        super().__init__()
        self.film_name = None
        self.id = id
        self.session_date = session_date
        self.start_time = start_time
        self.hall_id = hall_id
        self.film_id = film_id
        self.end_time = end_time

    def set_film_name(self, name: str):
        self.film_name = name
