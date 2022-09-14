import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, TimeField, IntegerField, RadioField
from wtforms.validators import DataRequired


class AddFilmForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    director = StringField('Режиссер', validators=[DataRequired()])
    year = IntegerField('Год выпуска', validators=[DataRequired()], default=datetime.datetime.now().date().year)
    description = TextAreaField('Описание')
    genres = StringField('Жанры', validators=[DataRequired()])
    duration = TimeField('Продолжительность', validators=[DataRequired()], default=datetime.time(1, 30))
    age_rate = IntegerField('Ограничение по возрасту', validators=[DataRequired()])
    category = RadioField('Категория фильма', choices=['Кинофильм', 'Мультфильм'])

    submit = SubmitField('Добавить')
