from flask import *
from flask_login import *
from werkzeug.urls import url_parse

import babel

from db import db, User, Film, Session, Hall, Seat, Ticket
from forms.add_film import AddFilmForm
from forms.add_session import AddSessionForm
from forms.auth import LoginForm
from forms.registration import RegistrationForm
from forms.statistics import StatisticForm

app = Flask(__name__)
app.config.from_object('config')

login = LoginManager(app)
login.login_view = 'sign_in'

categories = {'Кинофильм': 1, 'Мультфильм': 2}


@login.user_loader
def load_user(id):
    data = db.get_by_unique_int('user_account', 'id', int(id))
    if data is None:
        return None
    else:
        return User(*data)


@app.template_filter()
def format_datetime(value, format='time'):
    if format == 'date':
        format="EEEE, d MMMM y"
    elif format == 'time':
        format="HH:mm"
    return babel.dates.format_datetime(value, format)


@app.route('/', methods=['GET', 'POST'])
def sign_in():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        data = db.get_by_unique_str('user_account', 'email', email)
        if data is None:
            return {
                'message': 'User not found ERROR'
            }
        else:
            user = User(*data)
            if user.password == password:
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('index')
                return redirect(next_page)
            else:
                return {
                    'message': 'Incorrect password'
                }
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('sign_in'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        db.insert('user_account', {
            'email': form.email.data,
            'password': form.password.data,
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'is_administrator': False
        })
        user = User(*db.get_by_unique_str('user_account', 'email', form.email.data))
        db.insert('client', {'user_id': user.id,
                             'cinema_id': 1})
        login_user(user, remember=False)
        return redirect(url_for('index'))
    return render_template('registration.html', title='Register', form=form)


@app.route('/index')
@login_required
def index():
    if current_user.is_administrator:
        return render_template('sudo_index.html')
    else:
        return render_template('index.html')


@app.route('/sessions')
@login_required
def sessions():
    sessions_data = db.get_future_sessions()
    sessions_list = []
    for i in range(len(sessions_data)):
        s = Session(*sessions_data[i])
        film = Film(*db.get_by_unique_int('film', 'id', s.film_id))
        s.set_film_name(film.film_name)
        sessions_list.append(s)
    return render_template('sessions.html', sessions=sessions_list)


@app.route('/add_session', methods=['GET', 'POST'])
@login_required
def add_session():
    if not current_user.is_administrator:
        return redirect(url_for('index'))
    else:
        form = AddSessionForm()
        if form.validate_on_submit():
            date = form.date.data
            start_time = form.start_time.data
            end_time = form.end_time.data
            hall_id = form.hall_id.data
            film = db.get_film_by_name(form.film_name.data, form.director.data)
            if film is None:
                form.film_name.errors.append('Такого фильма в кинотеатре нет')
            else:
                film_id = [0]
                db.insert('cinema_session', {'session_date': date,
                                             'start_time': start_time,
                                             'hall_id': hall_id,
                                             'film_id': film_id,
                                             'end_time': end_time})
                return redirect(url_for('add_session'))
        return render_template('add_session.html', form=form)


@app.route('/add_film', methods=['GET', 'POST'])
@login_required
def add_film():
    if not current_user.is_administrator:
        return redirect(url_for('index'))
    else:
        global categories
        form = AddFilmForm()
        if form.validate_on_submit():
            name = form.name.data
            director = form.director.data
            year = form.year.data
            description = form.description.data
            duration = form.duration.data
            age_rate = form.age_rate.data
            category = categories[form.category.data]
            genres = form.genres.data.split(',')
            db.insert('film', {'film_name': name,
                               'director': director,
                               'release_year': year,
                               'description': description,
                               'duration': duration,
                               'age_rate': age_rate,
                               'category': category})
            film_id = db.get_film_by_name(name, director)[0]
            db.insert_genres(genres, film_id)

            return redirect(url_for('add_film'))
        return render_template('add_film.html', form=form)


@app.route('/session/<int:session_id>/tickets')
@login_required
def tickets(session_id):
    seats_data = db.get_free_seats(session_id)
    seats = []
    for i in range(len(seats_data)):
        seat = Seat(*seats_data[i])
        seats.append(seat)
    return render_template('seats.html', tickets=seats, session_id=session_id)


@app.route('/user/<int:user_id>/tickets')
@login_required
def user_tickets(user_id):
    tickets_data = db.get_user_tickets(user_id)
    tickets = []
    seats = []
    for i in range(len(tickets_data)):
        ticket = Ticket(*tickets_data[i])
        seat = Seat(*db.get_by_unique_int('seat', 'id', ticket.seat_id))
        session = Session(*db.get_by_unique_int('cinema_session', 'id', ticket.session_id))
        tickets.append((ticket, seat, session))
    return render_template('tickets.html', tickets=tickets)


@app.route('/films')
def films():
    if current_user.is_administrator:
        films_data = db.get_all('film')
    else:
        films_data = db.get_available_films()
    films = []
    for i in range(len(films_data)):
        film = Film(*films_data[i])
        films.append(film)
    return render_template('films.html', films=films)


@app.route('/session/<int:session_id>/tickets/<int:seat_id>')
@login_required
def buy_ticket(session_id, seat_id):

    db.insert('ticket', {'session_id': session_id,
                         'seat_id': seat_id,
                         'user_id': current_user.id,
                         'cost': 300})
    return redirect(url_for('tickets', session_id=session_id))


@app.route('/statistic', methods=['GET', 'POST'])
@login_required
def statistic():
    genres = db.get_genres_stat()
    form = StatisticForm()
    if form.validate_on_submit():
        film_data = db.get_by_unique_str('film', 'film_name', form.search.data)
        if film_data is None:
            return render_template('error.html', message='Фильм с таким именем не найден')
        else:
            film = Film(*film_data)
            film_stat = db.get_film_stat(film.id)
            return render_template('film_stat.html', film_name=film.film_name, film_stat=film_stat)
    return render_template('statistics.html', form=form, genres=genres)

