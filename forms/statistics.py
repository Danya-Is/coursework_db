from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class StatisticForm(FlaskForm):
    search = StringField('Поиск', validators=[DataRequired()])
    submit = SubmitField('Искать')