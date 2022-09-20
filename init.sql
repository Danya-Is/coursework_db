DROP TABLE IF EXISTS user_account, cinema, administrator, client, hall, seat, film, cinema_session,
    ticket, genre, film_genre;

CREATE TABLE user_account (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    email varchar(64) NOT NULL UNIQUE,
    password varchar(64) NOT NULL,
    first_name varchar(64) NOT NULL,
    last_name varchar(64) NOT NULL,
    is_administrator boolean NOT NULL
);

CREATE TABLE cinema (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    address varchar(128) NOT NULL UNIQUE,
    cinema_name varchar(64) NOT NULL
);

CREATE TABLE administrator (
    id integer PRIMARY KEY REFERENCES user_account(id) ON DELETE CASCADE,
    cinema_id integer REFERENCES cinema(id) ON DELETE CASCADE
);

CREATE TABLE client (
    id integer PRIMARY KEY REFERENCES user_account(id) ON DELETE CASCADE
);

CREATE TABLE hall (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    hall_number integer NOT NULL UNIQUE,
    hall_name varchar(64) NOT NULL UNIQUE,
    cinema_id integer REFERENCES cinema(id) ON DELETE CASCADE
);

CREATE TABLE seat (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    hall_id integer REFERENCES hall(id) ON DELETE CASCADE,
    row_number integer NOT NULL,
    seat_number integer NOT NULL,
    category integer CHECK (category IN (0, 1, 2)),
    UNIQUE (hall_id, row_number, seat_number)
);

CREATE TABLE film (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    film_name varchar(128) NOT NULL,
    director varchar(128) NOT NULL,
    UNIQUE  (film_name, director),
    release_year integer NOT NULL
        CHECK (1895 <= release_year AND film.release_year <= date_part('year', CURRENT_DATE)),
    description text,
    duration time NOT NULL DEFAULT '01:00:00',
    age_rate integer NOT NULL DEFAULT 0
        CHECK (0 <= age_rate AND age_rate <= 18),
    category integer NOT NULL DEFAULT 0 CHECK (category IN (0, 1))
);

CREATE TABLE cinema_session (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    session_date date NOT NULL DEFAULT CURRENT_DATE,
    start_time time with time zone NOT NULL DEFAULT '08:00 PM',
    hall_id integer REFERENCES hall(id) ON DELETE CASCADE,
    UNIQUE (session_date, start_time, hall_id),
    film_id integer REFERENCES film(id) ON DELETE CASCADE,
    end_time time NOT NULL CHECK (end_time > start_time)
);

CREATE TABLE ticket (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    session_id integer REFERENCES cinema_session(id) ON DELETE CASCADE,
    seat_id integer REFERENCES seat(id) ON DELETE CASCADE,
    UNIQUE (session_id, seat_id),
    user_id integer REFERENCES user_account(id) ON DELETE CASCADE,
    cost real NOT NULL DEFAULT 300
);

CREATE TABLE genre (
    id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    genre_name varchar(64) NOT NULL UNIQUE
);

CREATE TABLE film_genre (
    film_id integer REFERENCES film(id) ON DELETE CASCADE,
    genre_id integer REFERENCES genre(id), -- удаление запрещено
    PRIMARY KEY (film_id, genre_id)
);

INSERT INTO user_account (email, password, first_name, last_name, is_administrator)
VALUES ('ivani@mail.ru', '123456', 'Иван', 'Иванов', FALSE),
('stanp@mail.ru', '123456', 'Петр', 'Станиславский', TRUE);

INSERT INTO cinema (address, cinema_name)
VALUES ('3я Парковая, д2', 'Иллюзион');

INSERT INTO administrator (id, cinema_id)
VALUES (2, 1);

INSERT INTO client (id)
VALUES (1);

INSERT INTO hall (hall_number, hall_name, cinema_id)
VALUES (1, 'Москва', 1), (2, 'Владивосток', 1), (3, 'Ленинград', 1);

INSERT INTO seat (hall_id, row_number, seat_number, category)
VALUES (1, 1, 1, 1), (1, 1, 2, 1), (1, 1, 3, 1),
       (1, 2, 1, 1), (1, 2, 2, 1), (1, 2, 3, 1),
       (2, 1, 1, 1), (2, 1, 2, 1), (2, 1, 3, 1),
       (2, 2, 1, 1), (2, 2, 2, 1), (2, 2, 3, 1);

INSERT INTO film (film_name, director, release_year, description, duration, age_rate, category)
VALUES ('Солнцестояние', 'Ари Астер', 2019, 'Гости идиллического шведского праздника становятся жертвами зловещих ритуалов', '02:28:00', 18, 1),
       ('Ла-Ла Ленд', 'Дэмьен Шазелл', 2016, 'Трагикомичный мюзикл о компромиссе в жизни артиста', '02:08:00', 16, 1);

INSERT INTO cinema_session (session_date, start_time, hall_id, film_id, end_time)
VALUES ('2023-09-21', '08:00:00', 2, 1, '10:40:00'),
       ('2023-09-21', '10:50:00', 2, 1, '13:30:00'),
       ('2023-09-21', '08:00:00', 1, 2, '10:20:00'),
       ('2023-09-21', '10:30:00', 1, 2, '12:50:00');

INSERT INTO genre (genre_name)
VALUES ('Ужасы'), ('Мюзикл');

INSERT INTO film_genre (film_id, genre_id)
VALUES (1, 1), (2, 2);