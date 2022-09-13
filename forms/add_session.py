import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TimeField, IntegerField
from wtforms.validators import ValidationError, DataRequired


class AddSessionForm(FlaskForm):
    date = DateField('Дата', validators=[DataRequired()], format='%Y-%m-%d', default=datetime.date.today())
    start_time = TimeField('Время начала', validators=[DataRequired()], default=datetime.datetime.now().time())
    end_time = TimeField('Время конца', validators=[DataRequired()], default=datetime.datetime.now().time())
    hall_id = IntegerField('Номер кинозала', validators=[DataRequired()])
    film_name = StringField('Название фильма', validators=[DataRequired()])
    director = StringField('Режиссер', validators=[DataRequired()])

    submit = SubmitField('Добавить')

    def validate_hall_id(self, hall_id):
        if hall_id.data < 0:
            raise ValidationError('Номер зала не может быть отрицательным')
