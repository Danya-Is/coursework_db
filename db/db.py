from typing import Union, Tuple

import psycopg2

db_config = {
    'dbname': 'cinema_db',
    'user': 'daria',
    'password': 'qwerty',
    'host': 'localhost'
}


def get_db_connection():
    conn = psycopg2.connect(**db_config)
    return conn


def execute_select_one(query: str):
    with get_db_connection().cursor() as cursor:
        cursor.execute(query)
        entry = cursor.fetchone()
        return entry


def execute_select_all(query: str):
    with get_db_connection().cursor() as cursor:
        cursor.execute(query)
        entry = cursor.fetchall()
        return entry


def get_by_unique_str(table: str, by: str, value: str) -> Union[Tuple, None]:
    return execute_select_one('SELECT * FROM {} WHERE {}=\'{}\''.format(table, by, value))


def get_by_unique_int(table: str, by: str, value: int) -> Union[Tuple, None]:
    return execute_select_one('SELECT * FROM {} WHERE {}={}'.format(table, by, value))


def get_all(table: str):
    return execute_select_all('SELECT * FROM {}'.format(table))


def insert(table: str, entry: dict):
    field_names = ', '.join([k for k in entry.keys()])
    dummy = ', '.join('%s' for _ in entry.keys())
    query = 'INSERT INTO {}({}) VALUES ({})'.format(table, field_names, dummy)
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, list(entry.values()))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)
        return False
    return True


def get_film_by_name(name, director):
    query = 'SELECT * FROM film as f ' \
            'WHERE (f.film_name = \'{}\' AND f.director = \'{}\')'\
        .format(name, director)
    return execute_select_one(query)


def get_future_sessions():
    print('CURRENT DATE')
    query = 'SELECT * FROM cinema_session as s ' \
            'WHERE (s.session_date > CURRENT_DATE OR (s.session_date = CURRENT_DATE  AND s.start_time > CURRENT_TIME ))'
    return execute_select_all(query)


def get_free_seats(session_id: int):
    session = get_by_unique_int('cinema_session', 'id', session_id)
    hall = get_by_unique_int('hall', 'id', session[3])
    query = 'SELECT * FROM seat as s WHERE s.hall_id = {} AND\
                (NOT EXISTS (SELECT * FROM ticket as t WHERE t.seat_id = s.id AND t.session_id = {}))' \
        .format(hall[0], session_id)
    return execute_select_all(query)


def get_seats(session_id: int):
    session = get_by_unique_int('cinema_session', 'id', session_id)
    hall = get_by_unique_int('hall', 'id', session[3])
    query = 'SELECT * FROM seat as s WHERE s.hall_id = {}' \
        .format(hall[0], session_id)
    return execute_select_all(query)


def get_user_tickets(user_id: int):
    query = 'SELECT * FROM ticket as t WHERE t.user_id={}'.format(user_id)
    return execute_select_all(query)


def get_available_films():
    queue = 'SELECT * FROM film as f WHERE EXIST (' \
            'SELECT * FROM cinema_session as s WHERE s.film_id=f.id)'
    return execute_select_all(queue)


def get_session_stat(session_id: int) -> float:
    return (len(get_seats(session_id)) - len(get_free_seats(session_id))) / len(get_seats(session_id))


def get_film_stat(film_id: int) -> float:
    sessions = execute_select_all('SELECT * FROM cinema_session as s WHERE s.film_id={}'
                                  .format(film_id))
    sum = 0
    for session in sessions:
        sum += get_session_stat(session[0])
    return sum / len(sessions)


def get_genre_stat(genre_id: int) -> float:
    films = execute_select_all('SELECT * FROM film as f WHERE'
                              ' EXISTS (SELECT * FROM film_genre as fg '
                              'WHERE fg.film_id=f.id AND fg.genre_id={})'.format(genre_id))
    sum = 0
    for film in films:
        sum += get_film_stat(film[0])
    return sum / len(films)


def get_genres_stat():
    genres = get_all('genre')
    res = {}
    for genre in genres:
        res[genre[1]] = get_genre_stat(genre[0])
    return res
