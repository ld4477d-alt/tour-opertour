-- Схема БД АС «ТурОператор» для PostgreSQL

CREATE TABLE IF NOT EXISTS roles (
    id   SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(200) NOT NULL,
    role_id       INTEGER NOT NULL REFERENCES roles(id),
    is_active     BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS directions (
    id      SERIAL PRIMARY KEY,
    country VARCHAR(100) NOT NULL,
    city    VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS hotels (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(200) NOT NULL,
    city  VARCHAR(100) NOT NULL,
    stars INTEGER CHECK (stars BETWEEN 1 AND 5)
);

CREATE TABLE IF NOT EXISTS clients (
    id        SERIAL PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    phone     VARCHAR(30),
    email     VARCHAR(120),
    passport  VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS tours (
    id           SERIAL PRIMARY KEY,
    title        VARCHAR(200) NOT NULL,
    direction_id INTEGER REFERENCES directions(id) ON DELETE SET NULL,
    hotel_id     INTEGER REFERENCES hotels(id)     ON DELETE SET NULL,
    date_start   DATE NOT NULL,
    date_end     DATE NOT NULL,
    price        NUMERIC(12,2) NOT NULL CHECK (price >= 0),
    quota        INTEGER NOT NULL DEFAULT 0 CHECK (quota >= 0),
    status       VARCHAR(30) NOT NULL DEFAULT 'Черновик'
);

CREATE TABLE IF NOT EXISTS contracts (
    id         SERIAL PRIMARY KEY,
    client_id  INTEGER NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
    tour_id    INTEGER NOT NULL REFERENCES tours(id)   ON DELETE RESTRICT,
    manager_id INTEGER REFERENCES users(id)            ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    status     VARCHAR(30) NOT NULL DEFAULT 'Оформлен',
    total      NUMERIC(12,2) NOT NULL DEFAULT 0
);

INSERT INTO roles (id, name) VALUES (1, 'admin'), (2, 'manager')
    ON CONFLICT (id) DO NOTHING;

INSERT INTO users (id, username, password_hash, full_name, role_id)
VALUES (1, 'admin', 'admin', 'Администратор', 1)
    ON CONFLICT (id) DO NOTHING;

SELECT setval('roles_id_seq', (SELECT MAX(id) FROM roles));
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));