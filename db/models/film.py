from db.model import Model


class Film(Model):
    def __init__(self, id, film_name, director, release_year, description, duration, age_rate, category):
        super().__init__()
        self.id = id
        self.film_name = film_name
        self.director = director
        self.release_year = release_year
        self.description = description
        self.duration = duration
        self.age_rate = age_rate
        self.category = category
