from flask import *
from flask_login import *
from werkzeug.urls import url_parse

from db import db, User, Film, Session, Hall, Seat, Ticket
from forms.auth import LoginForm
from forms.registration import RegistrationForm
from forms.statistics import StatisticForm

app = Flask(__name__)
app.config.from_object('config')

login = LoginManager(app)
login.login_view = 'sign_in'


@login.user_loader
def load_user(id):
    data = db.get_by_unique_int('user_account', 'id', int(id))
    if data is None:
        return None
    else:
        return User(*data)


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
    sessions_data = db.get_all('cinema_session')
    sessions_list = []
    for i in range(len(sessions_data)):
        s = Session(*sessions_data[i])
        film = Film(*db.get_by_unique_int('film', 'id', s.film_id))
        s.set_film_name(film.film_name)
        sessions_list.append(s)
    return render_template('sessions.html', sessions=sessions_list)


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
    for i in range(len(tickets_data)):
        ticket = Ticket(*tickets_data[i])
        tickets.append(ticket)
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

