\c "PeopleDb";

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS meta;

CREATE TABLE IF NOT EXISTS meta.relationship_types
(
    relationship_type varchar(50) PRIMARY KEY,
    description       text NOT NULL
);

INSERT INTO meta.relationship_types(relationship_type, description) VALUES
('MANAGER_OF', 'Primary manager relationship'),
('TEAM_MEMBER', 'Membership between employee and team'),
('USER_JOB', 'Relationship between a user and their job')
ON CONFLICT (relationship_type) DO NOTHING;

CREATE TABLE IF NOT EXISTS meta.skill_levels
(
    level       smallint PRIMARY KEY,
    label       varchar(32) NOT NULL,
    description text        NOT NULL
);

INSERT INTO meta.skill_levels(level, label, description) VALUES
    (0, 'None', 'No exposure to the skill'),
    (1, 'Basic', 'Basic familiarity'),
    (2, 'Intermediate', 'Comfortable independently'),
    (3, 'Advanced', 'Advanced practitioner and mentor'),
    (4, 'Expert', 'Recognized expert / advisor')
ON CONFLICT (level) DO NOTHING;

CREATE SCHEMA IF NOT EXISTS people;

CREATE TABLE people.employees
(
    uid          uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    employee_id  varchar(64)  NOT NULL,
    first_name   varchar(100) NOT NULL,
    last_name    varchar(100) NOT NULL,
    email        varchar(128) NOT NULL,
    title        varchar(120) NOT NULL,
    department   varchar(120) NOT NULL,
    location     varchar(120),
    manager_uid  uuid REFERENCES people.employees(uid) ON DELETE SET NULL,
    role         varchar(32)  NOT NULL CHECK (role IN ('ADMIN','HR','SENIOR_MANAGER','MANAGER','IC')),
    status       varchar(32)  NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','ON_LEAVE','TERMINATED')),
    hire_date    date,
    created_at   timestamptz  NOT NULL DEFAULT now(),
    updated_at   timestamptz  NOT NULL DEFAULT now()
);

ALTER TABLE people.employees
    ADD CONSTRAINT employees_employee_id_unique UNIQUE (employee_id),
    ADD CONSTRAINT employees_email_unique UNIQUE (email);

CREATE TABLE people.teams
(
    uid             uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    name            varchar(120) NOT NULL,
    description     text,
    parent_team_uid uuid REFERENCES people.teams(uid) ON DELETE SET NULL,
    leader_uid      uuid REFERENCES people.employees(uid) ON DELETE SET NULL,
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (name)
);

CREATE TABLE people.team_memberships
(
    uid          uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    team_uid     uuid NOT NULL REFERENCES people.teams(uid) ON DELETE CASCADE,
    employee_uid uuid NOT NULL REFERENCES people.employees(uid) ON DELETE CASCADE,
    role         varchar(64),
    is_primary   boolean      NOT NULL DEFAULT FALSE,
    start_date   date,
    end_date     date,
    UNIQUE (team_uid, employee_uid)
);

CREATE TABLE people.skills_catalog
(
    uid         uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    name        varchar(120) NOT NULL,
    category    varchar(64),
    description text,
    tags        text[]        NOT NULL DEFAULT ARRAY[]::text[],
    is_active   boolean       NOT NULL DEFAULT TRUE,
    created_at  timestamptz   NOT NULL DEFAULT now(),
    updated_at  timestamptz   NOT NULL DEFAULT now(),
    UNIQUE (name)
);

CREATE TABLE people.employee_skills
(
    uid              uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    employee_uid     uuid NOT NULL REFERENCES people.employees(uid) ON DELETE CASCADE,
    skill_uid        uuid NOT NULL REFERENCES people.skills_catalog(uid) ON DELETE CASCADE,
    level            smallint   NOT NULL REFERENCES meta.skill_levels(level),
    source           varchar(32) NOT NULL CHECK (source IN ('MANAGER','IC_PROPOSAL','SYSTEM')),
    notes            text,
    last_updated_by  uuid NOT NULL REFERENCES people.employees(uid) ON DELETE SET NULL,
    last_updated_at  timestamptz NOT NULL DEFAULT now(),
    UNIQUE (employee_uid, skill_uid)
);

CREATE TABLE people.employee_skill_history
(
    uid                 uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    employee_skill_uid  uuid NOT NULL REFERENCES people.employee_skills(uid) ON DELETE CASCADE,
    previous_level      smallint REFERENCES meta.skill_levels(level),
    new_level           smallint REFERENCES meta.skill_levels(level),
    previous_notes      text,
    new_notes           text,
    changed_by          uuid NOT NULL REFERENCES people.employees(uid) ON DELETE SET NULL,
    changed_at          timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE people.one_on_one_sessions
(
    uid            uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    manager_uid    uuid NOT NULL REFERENCES people.employees(uid) ON DELETE CASCADE,
    employee_uid   uuid NOT NULL REFERENCES people.employees(uid) ON DELETE CASCADE,
    session_date   date NOT NULL,
    frequency      varchar(32),
    agenda         text,
    shared_summary text,
    created_at     timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_one_on_one_sessions_employee ON people.one_on_one_sessions(employee_uid);
CREATE INDEX IF NOT EXISTS idx_one_on_one_sessions_manager ON people.one_on_one_sessions(manager_uid);

CREATE TABLE people.one_on_one_notes
(
    uid          uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    session_uid  uuid NOT NULL REFERENCES people.one_on_one_sessions(uid) ON DELETE CASCADE,
    author_uid   uuid NOT NULL REFERENCES people.employees(uid) ON DELETE CASCADE,
    visibility   varchar(16) NOT NULL CHECK (visibility IN ('SHARED','PRIVATE')),
    content      text        NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE people.action_items
(
    uid          uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    session_uid  uuid REFERENCES people.one_on_one_sessions(uid) ON DELETE CASCADE,
    employee_uid uuid NOT NULL REFERENCES people.employees(uid) ON DELETE CASCADE,
    description  text        NOT NULL,
    owner_uid    uuid NOT NULL REFERENCES people.employees(uid) ON DELETE SET NULL,
    due_date     date,
    status       varchar(16) NOT NULL CHECK (status IN ('OPEN','IN_PROGRESS','DONE')),
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE people.role_skill_profiles
(
    uid          uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    profile_type varchar(16)  NOT NULL CHECK (profile_type IN ('ROLE','PROJECT')),
    name         varchar(200) NOT NULL,
    description  text,
    owner_uid    uuid REFERENCES people.employees(uid) ON DELETE SET NULL,
    context      jsonb,
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now(),
    UNIQUE (profile_type, name)
);

CREATE TABLE people.role_skill_requirements
(
    uid                uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    profile_uid        uuid NOT NULL REFERENCES people.role_skill_profiles(uid) ON DELETE CASCADE,
    skill_uid          uuid NOT NULL REFERENCES people.skills_catalog(uid) ON DELETE CASCADE,
    required_level     smallint NOT NULL REFERENCES meta.skill_levels(level),
    required_headcount int      NOT NULL DEFAULT 1,
    UNIQUE (profile_uid, skill_uid)
);

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
    relationship_type varchar(50) NOT NULL REFERENCES meta.relationship_types(relationship_type),
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (primary_uid, secondary_uid, relationship_type)
);

CREATE TABLE people.audit_log
(
    uid           uuid PRIMARY KEY      DEFAULT gen_random_uuid(),
    entity_type   varchar(64)  NOT NULL,
    entity_uid    uuid         NOT NULL,
    action        varchar(32)  NOT NULL,
    performed_by  uuid REFERENCES people.employees(uid) ON DELETE SET NULL,
    performed_at  timestamptz  NOT NULL DEFAULT now(),
    before_data   jsonb,
    after_data    jsonb
);
