CREATE DATABASE "PeopleDb";
\c "PeopleDb";

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS people;

CREATE TABLE people.users
(
    uid        uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    id         varchar(64)  NOT NULL,
    first_name varchar(100) NOT NULL,
    last_name  varchar(100) NOT NULL,
    email      varchar(64)  NOT NULL,
    created_at timestamptz  NOT NULL DEFAULT now()
);

ALTER TABLE people.users
    ADD CONSTRAINT users_id_unique UNIQUE (id),
    ADD CONSTRAINT users_email_unique UNIQUE (email);
