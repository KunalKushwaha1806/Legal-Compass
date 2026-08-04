-- ============================================================
-- Legal Compass — PostgreSQL Schema
-- Run via: psql $DATABASE_URL -f models/schema.sql
-- Or: it is executed automatically at server startup.
-- ============================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(100)        NOT NULL,
    email        VARCHAR(255) UNIQUE NOT NULL,
    password     VARCHAR(255)        NOT NULL,
    created_at   TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);

-- Chat history table
CREATE TABLE IF NOT EXISTS chats (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER             NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question       TEXT                NOT NULL,
    answer         TEXT                NOT NULL,
    sources        JSONB               NOT NULL DEFAULT '[]',
    response_time  FLOAT,
    created_at     TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_chats_user_id    ON chats(user_id);
CREATE INDEX IF NOT EXISTS idx_chats_created_at ON chats(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_email      ON users(email);
