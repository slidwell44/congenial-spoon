CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS meta;

CREATE TABLE meta.relationship_types
(
    relationship_type varchar(50) PRIMARY KEY,
    description       text         NOT NULL
);

INSERT INTO meta.relationship_types(relationship_type, description) VALUES
('USER_JOB', 'Relationship between a user and their job');

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

CREATE TABLE people.jobs
(
    uid          uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    id           varchar(64)  NOT NULL,
    title        varchar(200) NOT NULL,
    description  text         NOT NULL,
    status       varchar(50)  NOT NULL,
    created_at   timestamptz  NOT NULL DEFAULT now()
);

CREATE TABLE people.user_relationships
(
    uid uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    primary_uid uuid NOT NULL,
    secondary_uid uuid NOT NULL,
    relationship_type varchar(50) NOT NULL REFERENCES meta.relationship_types(relationship_type) ON DELETE NO ACTION,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (primary_uid, secondary_uid, relationship_type)
)
